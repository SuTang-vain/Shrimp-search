#!/usr/bin/env python3
"""
硬件资源占用报告生成脚本
监控和报告RAG系统的硬件资源使用情况
"""

import os
import sys
import time
import json
import psutil
import threading
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import statistics
from pathlib import Path

# 尝试导入GPU监控库
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    print("警告: GPUtil未安装，GPU监控功能不可用")

# 尝试导入CUDA相关库
try:
    import torch
    TORCH_AVAILABLE = torch.cuda.is_available()
except ImportError:
    TORCH_AVAILABLE = False

# 导入项目模块
try:
    from performance_monitor import PerformanceMonitor, PerformanceContext
    from Enhanced_Interactive_Multimodal_RAG_v2 import EnhancedRAGSystemV2
    from enhanced_document_manager import EnhancedDocumentManager
except ImportError as e:
    print(f"警告: 无法导入项目模块: {e}")
    sys.exit(1)

@dataclass
class SystemResourceMetrics:
    """系统资源指标"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_available_gb: float
    disk_usage_percent: float
    gpu_metrics: List[Dict[str, Any]] = field(default_factory=list)
    network_io: Dict[str, int] = field(default_factory=dict)
    process_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BenchmarkResult:
    """基准测试结果"""
    test_name: str
    duration: float
    success: bool
    throughput: Optional[float] = None
    latency_stats: Optional[Dict[str, float]] = None
    resource_usage: Optional[SystemResourceMetrics] = None
    error_message: str = ""
    additional_metrics: Dict[str, Any] = field(default_factory=dict)

class HardwareResourceMonitor:
    """硬件资源监控器"""
    
    def __init__(self, monitoring_interval: float = 1.0):
        self.monitoring_interval = monitoring_interval
        self.is_monitoring = False
        self.resource_history: List[SystemResourceMetrics] = []
        self.monitor_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        
        # 获取当前进程
        self.current_process = psutil.Process()
        
        print(f"硬件资源监控器初始化完成 (监控间隔: {monitoring_interval}s)")
        
    def get_gpu_metrics(self) -> List[Dict[str, Any]]:
        """获取GPU指标"""
        gpu_metrics = []
        
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                for i, gpu in enumerate(gpus):
                    gpu_info = {
                        'id': i,
                        'name': gpu.name,
                        'load': gpu.load * 100,  # 转换为百分比
                        'memory_used': gpu.memoryUsed,  # MB
                        'memory_total': gpu.memoryTotal,  # MB
                        'memory_percent': (gpu.memoryUsed / gpu.memoryTotal) * 100,
                        'temperature': gpu.temperature
                    }
                    gpu_metrics.append(gpu_info)
            except Exception as e:
                print(f"获取GPU指标失败: {e}")
        
        # 如果有PyTorch CUDA支持，添加CUDA信息
        if TORCH_AVAILABLE:
            try:
                for i in range(torch.cuda.device_count()):
                    device = torch.cuda.device(i)
                    memory_allocated = torch.cuda.memory_allocated(i) / 1024**2  # MB
                    memory_cached = torch.cuda.memory_reserved(i) / 1024**2  # MB
                    
                    # 更新对应GPU的信息
                    if i < len(gpu_metrics):
                        gpu_metrics[i].update({
                            'cuda_memory_allocated': memory_allocated,
                            'cuda_memory_cached': memory_cached
                        })
                    else:
                        # 如果GPUtil不可用，创建基本的CUDA信息
                        gpu_metrics.append({
                            'id': i,
                            'name': torch.cuda.get_device_name(i),
                            'cuda_memory_allocated': memory_allocated,
                            'cuda_memory_cached': memory_cached
                        })
            except Exception as e:
                print(f"获取CUDA信息失败: {e}")
        
        return gpu_metrics
    
    def get_current_metrics(self) -> SystemResourceMetrics:
        """获取当前系统资源指标"""
        # CPU和内存信息
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 网络IO
        net_io = psutil.net_io_counters()
        network_io = {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }
        
        # 当前进程信息
        try:
            process_info = {
                'cpu_percent': self.current_process.cpu_percent(),
                'memory_percent': self.current_process.memory_percent(),
                'memory_info': self.current_process.memory_info()._asdict(),
                'num_threads': self.current_process.num_threads(),
                'open_files': len(self.current_process.open_files())
            }
        except Exception as e:
            process_info = {'error': str(e)}
        
        return SystemResourceMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_gb=memory.used / (1024**3),
            memory_available_gb=memory.available / (1024**3),
            disk_usage_percent=disk.percent,
            gpu_metrics=self.get_gpu_metrics(),
            network_io=network_io,
            process_metrics=process_info
        )
    
    def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        print("开始硬件资源监控...")
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        print("硬件资源监控已停止")
    
    def _monitoring_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                metrics = self.get_current_metrics()
                with self.lock:
                    self.resource_history.append(metrics)
                    # 保持历史记录在合理范围内
                    if len(self.resource_history) > 1000:
                        self.resource_history = self.resource_history[-500:]
                
                time.sleep(self.monitoring_interval)
            except Exception as e:
                print(f"监控循环错误: {e}")
                time.sleep(self.monitoring_interval)
    
    def get_resource_summary(self) -> Dict[str, Any]:
        """获取资源使用摘要"""
        if not self.resource_history:
            return {"error": "无监控数据"}
        
        with self.lock:
            history = self.resource_history.copy()
        
        # CPU统计
        cpu_values = [m.cpu_percent for m in history]
        cpu_stats = {
            'min': min(cpu_values),
            'max': max(cpu_values),
            'avg': statistics.mean(cpu_values),
            'median': statistics.median(cpu_values)
        }
        
        # 内存统计
        memory_values = [m.memory_percent for m in history]
        memory_stats = {
            'min': min(memory_values),
            'max': max(memory_values),
            'avg': statistics.mean(memory_values),
            'median': statistics.median(memory_values)
        }
        
        # GPU统计
        gpu_stats = {}
        if history and history[0].gpu_metrics:
            for gpu_id in range(len(history[0].gpu_metrics)):
                gpu_loads = []
                gpu_memory_percents = []
                
                for metrics in history:
                    if gpu_id < len(metrics.gpu_metrics):
                        gpu_info = metrics.gpu_metrics[gpu_id]
                        if 'load' in gpu_info:
                            gpu_loads.append(gpu_info['load'])
                        if 'memory_percent' in gpu_info:
                            gpu_memory_percents.append(gpu_info['memory_percent'])
                
                if gpu_loads:
                    gpu_stats[f'gpu_{gpu_id}_load'] = {
                        'min': min(gpu_loads),
                        'max': max(gpu_loads),
                        'avg': statistics.mean(gpu_loads),
                        'median': statistics.median(gpu_loads)
                    }
                
                if gpu_memory_percents:
                    gpu_stats[f'gpu_{gpu_id}_memory'] = {
                        'min': min(gpu_memory_percents),
                        'max': max(gpu_memory_percents),
                        'avg': statistics.mean(gpu_memory_percents),
                        'median': statistics.median(gpu_memory_percents)
                    }
        
        return {
            'monitoring_period': {
                'start': datetime.fromtimestamp(history[0].timestamp).isoformat(),
                'end': datetime.fromtimestamp(history[-1].timestamp).isoformat(),
                'duration_seconds': history[-1].timestamp - history[0].timestamp,
                'sample_count': len(history)
            },
            'cpu_stats': cpu_stats,
            'memory_stats': memory_stats,
            'gpu_stats': gpu_stats,
            'current_metrics': self.get_current_metrics().__dict__
        }

class PerformanceBenchmark:
    """性能基准测试"""
    
    def __init__(self, cache_dir: str = "document_cache"):
        self.cache_dir = cache_dir
        self.resource_monitor = HardwareResourceMonitor()
        self.performance_monitor = PerformanceMonitor(enable_detailed_monitoring=True)
        self.benchmark_results: List[BenchmarkResult] = []
        
        # 初始化RAG系统
        try:
            self.rag_system = EnhancedRAGSystemV2(
                enable_performance_monitoring=True,
                cache_dir=cache_dir
            )
            print("RAG系统初始化完成")
        except Exception as e:
            print(f"RAG系统初始化失败: {e}")
            self.rag_system = None
    
    def run_document_processing_benchmark(self, test_documents: List[str]) -> BenchmarkResult:
        """文档处理性能测试"""
        print("\n=== 文档处理性能测试 ===")
        
        if not self.rag_system:
            return BenchmarkResult(
                test_name="document_processing",
                duration=0,
                success=False,
                error_message="RAG系统未初始化"
            )
        
        start_time = time.time()
        self.resource_monitor.start_monitoring()
        
        try:
            # 执行文档处理
            self.rag_system.setup_knowledge_base(
                sources=test_documents,
                source_type="path",
                force_reprocess=True
            )
            
            duration = time.time() - start_time
            success = True
            
            # 计算吞吐量
            throughput = len(test_documents) / duration if duration > 0 else 0
            
            print(f"文档处理完成: {len(test_documents)} 个文档, 耗时 {duration:.2f}s")
            print(f"处理速度: {throughput:.2f} docs/s")
            
        except Exception as e:
            duration = time.time() - start_time
            success = False
            throughput = 0
            print(f"文档处理失败: {e}")
        
        self.resource_monitor.stop_monitoring()
        
        result = BenchmarkResult(
            test_name="document_processing",
            duration=duration,
            success=success,
            throughput=throughput,
            resource_usage=self.resource_monitor.get_current_metrics(),
            additional_metrics={
                'document_count': len(test_documents),
                'resource_summary': self.resource_monitor.get_resource_summary()
            }
        )
        
        self.benchmark_results.append(result)
        return result
    
    def run_query_latency_benchmark(self, test_queries: List[str], iterations: int = 10) -> BenchmarkResult:
        """查询延迟性能测试"""
        print(f"\n=== 查询延迟性能测试 (查询数: {len(test_queries)}, 迭代: {iterations}) ===")
        
        if not self.rag_system or not self.rag_system.knowledge_base_initialized:
            return BenchmarkResult(
                test_name="query_latency",
                duration=0,
                success=False,
                error_message="知识库未初始化"
            )
        
        latencies = []
        start_time = time.time()
        self.resource_monitor.start_monitoring()
        
        try:
            # 确保RAG系统已设置模型
            if not hasattr(self.rag_system, 'llm') or self.rag_system.llm is None:
                print("正在设置查询模型...")
                self.rag_system.setup_llm(
                    model_name="qwen2.5:7b",
                    base_url="http://localhost:11434",
                    temperature=0.7
                )
            
            for i in range(iterations):
                for query in test_queries:
                    query_start = time.time()
                    
                    # 执行查询
                    result = self.rag_system.enhanced_query_v2(
                        query=query,
                        retrieval_mode="快速检索"
                    )
                    
                    query_latency = time.time() - query_start
                    latencies.append(query_latency)
                    
                    print(f"查询 {i+1}/{iterations}: {query[:50]}... -> {query_latency:.3f}s")
            
            duration = time.time() - start_time
            success = True
            
            # 计算延迟统计
            latency_stats = {
                'min': min(latencies),
                'max': max(latencies),
                'avg': statistics.mean(latencies),
                'median': statistics.median(latencies),
                'p95': statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies),
                'p99': statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)
            }
            
            throughput = len(latencies) / duration if duration > 0 else 0
            
            print(f"查询测试完成: {len(latencies)} 次查询, 总耗时 {duration:.2f}s")
            print(f"平均延迟: {latency_stats['avg']:.3f}s, 查询速度: {throughput:.2f} queries/s")
            
        except Exception as e:
            duration = time.time() - start_time
            success = False
            latency_stats = None
            throughput = 0
            print(f"查询测试失败: {e}")
        
        self.resource_monitor.stop_monitoring()
        
        result = BenchmarkResult(
            test_name="query_latency",
            duration=duration,
            success=success,
            throughput=throughput,
            latency_stats=latency_stats,
            resource_usage=self.resource_monitor.get_current_metrics(),
            additional_metrics={
                'query_count': len(test_queries),
                'iterations': iterations,
                'total_queries': len(latencies),
                'resource_summary': self.resource_monitor.get_resource_summary()
            }
        )
        
        self.benchmark_results.append(result)
        return result
    
    def run_vectorization_benchmark(self, test_texts: List[str]) -> BenchmarkResult:
        """向量化性能测试"""
        print(f"\n=== 向量化性能测试 (文本数: {len(test_texts)}) ===")
        
        if not self.rag_system:
            return BenchmarkResult(
                test_name="vectorization",
                duration=0,
                success=False,
                error_message="RAG系统未初始化"
            )
        
        start_time = time.time()
        self.resource_monitor.start_monitoring()
        
        try:
            # 创建测试元数据
            test_metadata = [{'source': f'test_{i}', 'chunk_id': i} for i in range(len(test_texts))]
            
            # 执行向量化
            self.rag_system.vector_retriever.add_documents(
                texts=test_texts,
                metadata=test_metadata,
                batch_size=32,
                show_progress=True
            )
            
            duration = time.time() - start_time
            success = True
            throughput = len(test_texts) / duration if duration > 0 else 0
            
            print(f"向量化完成: {len(test_texts)} 个文本, 耗时 {duration:.2f}s")
            print(f"向量化速度: {throughput:.2f} texts/s")
            
        except Exception as e:
            duration = time.time() - start_time
            success = False
            throughput = 0
            print(f"向量化失败: {e}")
        
        self.resource_monitor.stop_monitoring()
        
        result = BenchmarkResult(
            test_name="vectorization",
            duration=duration,
            success=success,
            throughput=throughput,
            resource_usage=self.resource_monitor.get_current_metrics(),
            additional_metrics={
                'text_count': len(test_texts),
                'resource_summary': self.resource_monitor.get_resource_summary()
            }
        )
        
        self.benchmark_results.append(result)
        return result
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成综合性能报告"""
        print("\n=== 生成综合性能报告 ===")
        
        # 系统信息
        system_info = {
            'platform': sys.platform,
            'python_version': sys.version,
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / (1024**3),
            'gpu_info': self.resource_monitor.get_gpu_metrics()
        }
        
        # 基准测试结果摘要
        benchmark_summary = {}
        for result in self.benchmark_results:
            benchmark_summary[result.test_name] = {
                'success': result.success,
                'duration': result.duration,
                'throughput': result.throughput,
                'latency_stats': result.latency_stats,
                'error_message': result.error_message
            }
        
        # 性能监控摘要
        performance_summary = self.performance_monitor.get_system_performance_summary()
        
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'system_info': system_info,
            'benchmark_summary': benchmark_summary,
            'performance_monitoring': performance_summary,
            'detailed_results': [result.__dict__ for result in self.benchmark_results]
        }
        
        return report
    
    def save_report(self, filename: str = None) -> str:
        """保存性能报告"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"hardware_performance_report_{timestamp}.json"
        
        report = self.generate_comprehensive_report()
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"✓ 性能报告已保存到: {filename}")
            return filename
            
        except Exception as e:
            print(f"⚠ 保存性能报告失败: {e}")
            return ""
    
    def print_summary_report(self):
        """打印摘要报告"""
        print("\n" + "="*80)
        print("硬件资源占用报告摘要")
        print("="*80)
        
        # 系统信息
        current_metrics = self.resource_monitor.get_current_metrics()
        print(f"\n📊 当前系统状态:")
        print(f"  CPU使用率: {current_metrics.cpu_percent:.1f}%")
        print(f"  内存使用率: {current_metrics.memory_percent:.1f}%")
        print(f"  内存使用量: {current_metrics.memory_used_gb:.2f}GB")
        print(f"  磁盘使用率: {current_metrics.disk_usage_percent:.1f}%")
        
        if current_metrics.gpu_metrics:
            print(f"\n🎮 GPU状态:")
            for gpu in current_metrics.gpu_metrics:
                print(f"  GPU {gpu['id']} ({gpu['name']}):")
                if 'load' in gpu:
                    print(f"    负载: {gpu['load']:.1f}%")
                if 'memory_percent' in gpu:
                    print(f"    显存: {gpu['memory_percent']:.1f}%")
        
        # 基准测试结果
        if self.benchmark_results:
            print(f"\n🏃 基准测试结果:")
            for result in self.benchmark_results:
                status = "✓" if result.success else "✗"
                print(f"  {status} {result.test_name}:")
                print(f"    耗时: {result.duration:.2f}s")
                if result.throughput:
                    print(f"    吞吐量: {result.throughput:.2f} ops/s")
                if result.latency_stats:
                    print(f"    平均延迟: {result.latency_stats['avg']:.3f}s")
                    print(f"    P95延迟: {result.latency_stats['p95']:.3f}s")
        
        # 性能监控摘要
        perf_summary = self.performance_monitor.get_system_performance_summary()
        if 'total_operations' in perf_summary:
            print(f"\n📈 性能监控摘要:")
            print(f"  总操作数: {perf_summary['total_operations']}")
            print(f"  成功率: {perf_summary['overall_success_rate']:.1%}")
            print(f"  平均耗时: {perf_summary['avg_duration']:.2f}s")
            print(f"  平均内存使用: {perf_summary['avg_memory_usage']:.1f}MB")
        
        print("\n" + "="*80)

def main():
    """主函数"""
    print("硬件资源占用报告生成器")
    print("="*50)
    
    # 创建基准测试实例
    benchmark = PerformanceBenchmark()
    
    # 检查测试文档
    test_documents = []
    upload_dir = Path("uploaded_documents")
    if upload_dir.exists():
        test_documents = [str(f) for f in upload_dir.glob("*.pdf")][:3]  # 限制测试文档数量
    
    if not test_documents:
        print("警告: 未找到测试文档，将跳过文档处理测试")
    else:
        print(f"找到 {len(test_documents)} 个测试文档")
    
    # 测试查询
    test_queries = [
        "这个文档的主要内容是什么？",
        "有哪些重要的技术特性？",
        "系统的架构是怎样的？"
    ]
    
    # 测试文本
    test_texts = [
        "这是一个测试文本，用于向量化性能测试。",
        "人工智能技术正在快速发展，为各行各业带来变革。",
        "机器学习模型的训练需要大量的计算资源和数据。",
        "自然语言处理是人工智能的重要分支之一。",
        "深度学习在图像识别、语音识别等领域取得了突破性进展。"
    ] * 10  # 扩展测试数据
    
    try:
        # 运行基准测试
        if test_documents:
            benchmark.run_document_processing_benchmark(test_documents)
        
        benchmark.run_vectorization_benchmark(test_texts)
        
        if test_documents:  # 只有在有文档的情况下才运行查询测试
            benchmark.run_query_latency_benchmark(test_queries, iterations=5)
        
        # 生成并保存报告
        report_file = benchmark.save_report()
        benchmark.print_summary_report()
        
        if report_file:
            print(f"\n📄 详细报告已保存到: {report_file}")
        
    except KeyboardInterrupt:
        print("\n用户中断测试")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        benchmark.resource_monitor.stop_monitoring()
        print("\n测试完成")

if __name__ == "__main__":
    main()
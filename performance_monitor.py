"""
性能监控模块 - 监控RAG系统的性能指标
"""

import time
import psutil
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    timestamp: float
    operation: str
    duration: float
    memory_usage: float
    cpu_usage: float
    success: bool
    error_message: str = ""
    additional_data: Dict[str, Any] = field(default_factory=dict)

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, enable_detailed_monitoring: bool = True):
        self.enable_detailed_monitoring = enable_detailed_monitoring
        self.metrics_history: List[PerformanceMetrics] = []
        self.current_operations: Dict[str, float] = {}
        self.lock = threading.Lock()
        
        # 系统基线性能
        self.baseline_memory = psutil.virtual_memory().used
        self.baseline_cpu = psutil.cpu_percent()
        
        print(f"性能监控器初始化 (详细监控: {'开启' if enable_detailed_monitoring else '关闭'})")
    
    def start_operation(self, operation_name: str) -> str:
        """开始监控操作"""
        operation_id = f"{operation_name}_{int(time.time() * 1000)}"
        
        with self.lock:
            self.current_operations[operation_id] = time.time()
        
        if self.enable_detailed_monitoring:
            print(f"⏱ 开始监控: {operation_name}")
        
        return operation_id
    
    def end_operation(self, operation_id: str, success: bool = True, 
                     error_message: str = "", additional_data: Optional[Dict] = None) -> PerformanceMetrics:
        """结束监控操作"""
        end_time = time.time()
        
        with self.lock:
            start_time = self.current_operations.pop(operation_id, end_time)
            duration = end_time - start_time
            
            # 获取系统资源使用情况
            memory_usage = psutil.virtual_memory().used - self.baseline_memory
            cpu_usage = psutil.cpu_percent()
            
            # 创建性能指标
            metrics = PerformanceMetrics(
                timestamp=end_time,
                operation=operation_id.split('_')[0],
                duration=duration,
                memory_usage=memory_usage / (1024 * 1024),  # 转换为MB
                cpu_usage=cpu_usage,
                success=success,
                error_message=error_message,
                additional_data=additional_data or {}
            )
            
            self.metrics_history.append(metrics)
            
            if self.enable_detailed_monitoring:
                status = "✓" if success else "✗"
                print(f"{status} 操作完成: {metrics.operation} "
                      f"(耗时: {duration:.2f}s, 内存: {metrics.memory_usage:.1f}MB)")
            
            return metrics
    
    def get_operation_stats(self, operation_name: str) -> Dict[str, Any]:
        """获取特定操作的统计信息"""
        operation_metrics = [m for m in self.metrics_history if m.operation == operation_name]
        
        if not operation_metrics:
            return {"error": f"未找到操作 '{operation_name}' 的性能数据"}
        
        durations = [m.duration for m in operation_metrics]
        memory_usages = [m.memory_usage for m in operation_metrics]
        success_count = sum(1 for m in operation_metrics if m.success)
        
        return {
            "operation": operation_name,
            "total_calls": len(operation_metrics),
            "success_rate": success_count / len(operation_metrics),
            "duration_stats": {
                "min": min(durations),
                "max": max(durations),
                "avg": sum(durations) / len(durations),
                "total": sum(durations)
            },
            "memory_stats": {
                "min": min(memory_usages),
                "max": max(memory_usages),
                "avg": sum(memory_usages) / len(memory_usages)
            }
        }
    
    def get_system_performance_summary(self) -> Dict[str, Any]:
        """获取系统性能摘要"""
        if not self.metrics_history:
            return {"message": "暂无性能数据"}
        
        # 按操作类型分组统计
        operations = {}
        total_duration = 0
        total_memory = 0
        success_count = 0
        
        for metric in self.metrics_history:
            op_name = metric.operation
            if op_name not in operations:
                operations[op_name] = {
                    "count": 0,
                    "total_duration": 0,
                    "total_memory": 0,
                    "success_count": 0
                }
            
            operations[op_name]["count"] += 1
            operations[op_name]["total_duration"] += metric.duration
            operations[op_name]["total_memory"] += metric.memory_usage
            if metric.success:
                operations[op_name]["success_count"] += 1
            
            total_duration += metric.duration
            total_memory += metric.memory_usage
            if metric.success:
                success_count += 1
        
        # 计算平均值
        for op_name in operations:
            op_data = operations[op_name]
            op_data["avg_duration"] = op_data["total_duration"] / op_data["count"]
            op_data["avg_memory"] = op_data["total_memory"] / op_data["count"]
            op_data["success_rate"] = op_data["success_count"] / op_data["count"]
        
        return {
            "total_operations": len(self.metrics_history),
            "overall_success_rate": success_count / len(self.metrics_history),
            "total_duration": total_duration,
            "avg_duration": total_duration / len(self.metrics_history),
            "total_memory_usage": total_memory,
            "avg_memory_usage": total_memory / len(self.metrics_history),
            "operations_breakdown": operations,
            "monitoring_period": {
                "start": datetime.fromtimestamp(self.metrics_history[0].timestamp).isoformat(),
                "end": datetime.fromtimestamp(self.metrics_history[-1].timestamp).isoformat()
            }
        }
    
    def print_performance_report(self):
        """打印性能报告"""
        print("\n" + "="*60)
        print("性能监控报告")
        print("="*60)
        
        summary = self.get_system_performance_summary()
        
        if "message" in summary:
            print(summary["message"])
            return
        
        print(f"总操作数: {summary['total_operations']}")
        print(f"整体成功率: {summary['overall_success_rate']:.1%}")
        print(f"总耗时: {summary['total_duration']:.2f}秒")
        print(f"平均耗时: {summary['avg_duration']:.2f}秒")
        print(f"平均内存使用: {summary['avg_memory_usage']:.1f}MB")
        
        print(f"\n操作详情:")
        print("-" * 60)
        for op_name, op_data in summary['operations_breakdown'].items():
            print(f"{op_name}:")
            print(f"  调用次数: {op_data['count']}")
            print(f"  成功率: {op_data['success_rate']:.1%}")
            print(f"  平均耗时: {op_data['avg_duration']:.2f}秒")
            print(f"  平均内存: {op_data['avg_memory']:.1f}MB")
            print()
        
        print("="*60)
    
    def save_metrics_to_file(self, filename: str = None):
        """保存性能指标到文件"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"performance_metrics_{timestamp}.json"
        
        try:
            # 转换为可序列化的格式
            serializable_metrics = []
            for metric in self.metrics_history:
                serializable_metrics.append({
                    "timestamp": metric.timestamp,
                    "operation": metric.operation,
                    "duration": metric.duration,
                    "memory_usage": metric.memory_usage,
                    "cpu_usage": metric.cpu_usage,
                    "success": metric.success,
                    "error_message": metric.error_message,
                    "additional_data": metric.additional_data
                })
            
            data = {
                "summary": self.get_system_performance_summary(),
                "detailed_metrics": serializable_metrics
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ 性能指标已保存到: {filename}")
            
        except Exception as e:
            print(f"⚠ 保存性能指标失败: {e}")
    
    def clear_metrics(self):
        """清空性能指标历史"""
        with self.lock:
            self.metrics_history.clear()
            self.current_operations.clear()
        print("✓ 性能指标历史已清空")

class PerformanceContext:
    """性能监控上下文管理器"""
    
    def __init__(self, monitor: PerformanceMonitor, operation_name: str, 
                 additional_data: Optional[Dict] = None):
        self.monitor = monitor
        self.operation_name = operation_name
        self.additional_data = additional_data or {}
        self.operation_id = None
        self.success = True
        self.error_message = ""
    
    def __enter__(self):
        self.operation_id = self.monitor.start_operation(self.operation_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.success = False
            self.error_message = str(exc_val)
        
        self.monitor.end_operation(
            self.operation_id,
            success=self.success,
            error_message=self.error_message,
            additional_data=self.additional_data
        )
        
        return False  # 不抑制异常
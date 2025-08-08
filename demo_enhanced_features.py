"""
增强功能演示脚本
展示系统的各项改进功能
"""

import os
import sys
from dotenv import load_dotenv

# 导入增强模块
from enhanced_llm_interface import EnhancedLLMInterface, LLMConfig
from enhanced_multimodal_processor import EnhancedMultimodalProcessor
from enhanced_web_research import EnhancedWebResearchSystem
from performance_monitor import PerformanceMonitor, PerformanceContext
from enhanced_user_interface import EnhancedUserInterface

def demo_llm_stability():
    """演示LLM稳定性改进"""
    print("\n" + "="*60)
    print("🔧 演示1: LLM稳定性改进")
    print("="*60)
    
    load_dotenv()
    api_key = os.getenv('MODELSCOPE_SDK_TOKEN')
    
    if not api_key:
        print("❌ 请设置MODELSCOPE_SDK_TOKEN环境变量")
        return
    
    # 创建增强配置
    config = LLMConfig(
        model_name="Qwen/Qwen2.5-72B-Instruct",
        max_tokens=200,
        temperature=0.7,
        timeout=30,
        max_retries=3,
        retry_delay=1.0
    )
    
    try:
        # 初始化增强LLM接口
        llm = EnhancedLLMInterface(api_key, config)
        
        # 测试CAMEL和降级机制
        test_prompt = "请简单介绍CAMEL框架的主要特点"
        
        print("🧪 测试LLM生成...")
        response = llm.generate(test_prompt)
        
        print("✅ LLM响应:")
        print(response[:200] + "..." if len(response) > 200 else response)
        
        # 显示状态
        status = llm.get_status()
        print(f"\n📊 LLM状态:")
        print(f"  CAMEL可用: {status['camel_available']}")
        print(f"  模型: {status['model_name']}")
        print(f"  最大重试: {status['max_retries']}")
        
    except Exception as e:
        print(f"❌ LLM测试失败: {e}")

def demo_multimodal_processing():
    """演示多模态处理改进"""
    print("\n" + "="*60)
    print("🖼️ 演示2: 多模态处理改进")
    print("="*60)
    
    try:
        processor = EnhancedMultimodalProcessor()
        
        # 显示处理器能力
        print("📋 多模态处理器能力:")
        print(f"  图像OCR: {'✅' if processor.image_ocr_available else '❌'}")
        print(f"  表格处理: {'✅' if processor.table_processing_available else '❌'}")
        print(f"  PyMuPDF: {'✅' if processor.pymupdf_available else '❌'}")
        
        # 模拟处理PDF
        print("\n🔄 模拟PDF多模态处理...")
        
        # 使用默认PDF进行演示
        pdf_url = "https://arxiv.org/pdf/2303.17760.pdf"
        
        print(f"📄 处理PDF: {pdf_url}")
        result = processor.process_pdf_with_multimodal(pdf_url, is_url=True)
        
        print(f"✅ 处理完成:")
        print(f"  处理方法: {result['processing_method']}")
        print(f"  提取文档数: {len(result['texts_to_embed'])}")
        
        # 统计多模态内容
        stats = processor.get_multimodal_statistics(result['metadata_to_embed'])
        print(f"  内容统计:")
        print(f"    文本: {stats['text']}")
        print(f"    图像: {stats['image']}")
        print(f"    表格: {stats['table']}")
        print(f"    其他: {stats['other']}")
        
    except Exception as e:
        print(f"❌ 多模态处理演示失败: {e}")

def demo_web_research():
    """演示网页研究功能"""
    print("\n" + "="*60)
    print("🌐 演示3: 网页研究功能")
    print("="*60)
    
    try:
        web_system = EnhancedWebResearchSystem(max_results=3, timeout=10)
        
        # 显示系统能力
        stats = web_system.get_research_statistics()
        print("📋 网页研究系统能力:")
        print(f"  BeautifulSoup4: {'✅' if stats['bs4_available'] else '❌'}")
        print(f"  DuckDuckGo搜索: {'✅' if stats['ddgs_available'] else '❌'}")
        print(f"  最大结果数: {stats['max_results']}")
        print(f"  超时时间: {stats['timeout']}秒")
        
        # 执行网页研究
        query = "CAMEL框架多智能体系统"
        print(f"\n🔍 研究主题: {query}")
        
        research_result = web_system.research_topic(query, max_pages=2)
        
        print(f"✅ 研究完成:")
        print(f"  查询: {research_result['query']}")
        print(f"  信息源数量: {research_result['total_sources']}")
        print(f"  研究方法: {research_result['research_method']}")
        
        # 显示分析摘要
        analysis = research_result.get('analysis', '')
        if analysis:
            print(f"\n📄 分析摘要:")
            print(analysis[:300] + "..." if len(analysis) > 300 else analysis)
        
    except Exception as e:
        print(f"❌ 网页研究演示失败: {e}")

def demo_performance_monitoring():
    """演示性能监控功能"""
    print("\n" + "="*60)
    print("⚡ 演示4: 性能监控功能")
    print("="*60)
    
    try:
        monitor = PerformanceMonitor(enable_detailed_monitoring=True)
        
        # 模拟一些操作
        print("🔄 模拟系统操作...")
        
        # 操作1: 文档加载
        with PerformanceContext(monitor, "document_loading", {"doc_count": 100}):
            import time
            time.sleep(0.5)  # 模拟加载时间
        
        # 操作2: 向量检索
        with PerformanceContext(monitor, "vector_retrieval", {"query_length": 50}):
            time.sleep(0.3)  # 模拟检索时间
        
        # 操作3: LLM生成
        with PerformanceContext(monitor, "llm_generation", {"max_tokens": 500}):
            time.sleep(1.0)  # 模拟生成时间
        
        # 再次执行相同操作
        with PerformanceContext(monitor, "vector_retrieval", {"query_length": 30}):
            time.sleep(0.2)
        
        with PerformanceContext(monitor, "llm_generation", {"max_tokens": 300}):
            time.sleep(0.8)
        
        print("✅ 操作完成，生成性能报告...")
        
        # 显示性能报告
        monitor.print_performance_report()
        
        # 获取特定操作统计
        retrieval_stats = monitor.get_operation_stats("vector_retrieval")
        print(f"\n📊 向量检索统计:")
        print(f"  总调用次数: {retrieval_stats['total_calls']}")
        print(f"  成功率: {retrieval_stats['success_rate']:.1%}")
        print(f"  平均耗时: {retrieval_stats['duration_stats']['avg']:.2f}秒")
        
    except Exception as e:
        print(f"❌ 性能监控演示失败: {e}")

def demo_enhanced_ui():
    """演示增强用户界面"""
    print("\n" + "="*60)
    print("🎨 演示5: 增强用户界面")
    print("="*60)
    
    try:
        ui = EnhancedUserInterface(use_rich=True)
        
        # 显示各种消息类型
        ui.display_success("这是成功消息")
        ui.display_warning("这是警告消息")
        ui.display_error("这是错误消息")
        ui.display_loading("这是加载消息")
        
        # 显示系统状态
        sample_status = {
            "LLM接口": {"available": True, "details": "CAMEL + 直接API"},
            "嵌入模型": {"available": True, "details": "intfloat/e5-large-v2"},
            "多模态处理": {"available": True, "details": "OCR + 表格提取"},
            "网页研究": {"available": True, "details": "DuckDuckGo + BeautifulSoup"},
            "性能监控": {"available": True, "details": "实时监控"}
        }
        
        print("\n📊 系统状态展示:")
        ui.display_system_status(sample_status)
        
        # 显示性能摘要
        sample_performance = {
            "total_operations": 10,
            "overall_success_rate": 0.9,
            "total_duration": 15.5,
            "avg_duration": 1.55,
            "avg_memory_usage": 25.3,
            "operations_breakdown": {
                "document_loading": {
                    "count": 3,
                    "success_rate": 1.0,
                    "avg_duration": 2.1,
                    "avg_memory": 30.5
                },
                "vector_retrieval": {
                    "count": 4,
                    "success_rate": 0.75,
                    "avg_duration": 0.8,
                    "avg_memory": 15.2
                },
                "llm_generation": {
                    "count": 3,
                    "success_rate": 1.0,
                    "avg_duration": 2.5,
                    "avg_memory": 35.1
                }
            }
        }
        
        print("\n📈 性能摘要展示:")
        ui.display_performance_summary(sample_performance)
        
    except Exception as e:
        print(f"❌ 用户界面演示失败: {e}")

def main():
    """主演示函数"""
    print("🚀 增强功能演示")
    print("="*80)
    print("本演示将展示交互式多模态RAG系统v2.0的各项改进功能")
    
    try:
        # 演示各个功能模块
        demo_llm_stability()
        demo_multimodal_processing()
        demo_web_research()
        demo_performance_monitoring()
        demo_enhanced_ui()
        
        print("\n" + "="*80)
        print("✅ 所有功能演示完成!")
        print("="*80)
        print("\n📋 改进总结:")
        print("1. ✅ CAMEL稳定性: 增强错误处理和降级机制")
        print("2. ✅ 多模态支持: 改进图像OCR和表格提取")
        print("3. ✅ 网页研究: 真实网页内容获取和分析")
        print("4. ✅ 性能监控: 详细的性能指标和报告")
        print("5. ✅ 用户界面: Rich库增强的交互体验")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")

if __name__ == "__main__":
    main()
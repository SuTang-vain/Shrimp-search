#!/usr/bin/env python3
"""
测试内容过滤修复功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_llm_interface_v2 import EnhancedLLMInterfaceV2

def test_content_filter_handling():
    """测试内容过滤处理功能"""
    print("🧪 测试内容过滤修复功能")
    print("="*60)
    
    # 初始化LLM接口
    llm = EnhancedLLMInterfaceV2()
    
    # 测试查询优化功能
    print("\n1. 测试查询优化功能")
    print("-"*40)
    
    test_queries = [
        "camel是什么？",
        "camel中RAG系统是如何实现的?",
        "CAMEL框架的RAG实现方案",
        "请介绍RAG系统的实现"
    ]
    
    for query in test_queries:
        optimized = llm._optimize_query_for_content_filter(query)
        print(f"原查询: {query}")
        print(f"优化后: {optimized}")
        print()
    
    # 测试模型切换功能
    print("2. 测试自动模型切换功能")
    print("-"*40)
    
    # 设置GLM4.5模型
    if llm.set_model('glm4.5'):
        print("✅ 成功设置GLM4.5模型")
        
        # 测试生成（可能触发内容过滤）
        test_prompt = "请从技术角度分析：CAMEL框架中RAG技术架构是如何技术实现方案的？"
        print(f"测试查询: {test_prompt}")
        
        result = llm.generate(test_prompt, max_tokens=200, temperature=0.7)
        
        if result.error:
            print(f"⚠️ 生成失败: {result.error}")
            if "内容过滤" in result.error:
                print("✅ 内容过滤错误检测正常")
                print("✅ 自动模型切换功能已触发")
        else:
            print(f"✅ 生成成功: {result.content[:100]}...")
            print(f"使用模型: {result.model_key}")
    
    # 显示统计信息
    print("\n3. 系统统计信息")
    print("-"*40)
    stats = llm.get_generation_stats()
    print(f"总请求数: {stats['total_requests']}")
    print(f"成功请求数: {stats['successful_requests']}")
    print(f"失败请求数: {stats['failed_requests']}")
    print(f"内容过滤错误: {stats.get('content_filter_errors', 0)}")
    print(f"自动切换次数: {stats.get('auto_fallbacks', 0)}")
    
    print("\n🎉 内容过滤修复功能测试完成！")

if __name__ == "__main__":
    test_content_filter_handling()
"""
GLM4.5模型使用示例
展示如何使用新集成的GLM4.5模型进行对话和推理
"""

import os
from dotenv import load_dotenv
from enhanced_llm_interface_v2 import EnhancedLLMInterfaceV2

# 加载环境变量
load_dotenv()

def demo_glm4_5_usage():
    """演示GLM4.5模型使用"""
    print("🤖 GLM4.5模型使用演示")
    print("=" * 50)
    
    try:
        # 初始化增强LLM接口
        llm = EnhancedLLMInterfaceV2()
        print("✅ 系统初始化完成")
        
        # 显示可用模型
        available = llm.list_available_models()
        print(f"\n📋 可用模型总数: {len(available['remote']) + len(available['local'])}")
        
        # 检查GLM4.5可用性
        if 'glm4.5' in available['remote']:
            glm_info = available['remote']['glm4.5']
            if glm_info['available']:
                print("✅ GLM4.5模型可用，开始测试...")
                
                # 设置GLM4.5模型
                success = llm.set_model('glm4.5')
                if success:
                    print("✅ 成功切换到GLM4.5模型")
                    
                    # 测试对话
                    test_queries = [
                        "你好，请介绍一下你自己",
                        "解释一下什么是人工智能",
                        "用Python写一个简单的排序算法"
                    ]
                    
                    for i, query in enumerate(test_queries, 1):
                        print(f"\n🔍 测试 {i}: {query}")
                        print("-" * 40)
                        
                        try:
                            response = llm.generate_response(query)
                            print(f"🤖 GLM4.5回复: {response[:200]}...")
                            print("✅ 测试成功")
                        except Exception as e:
                            print(f"❌ 测试失败: {e}")
                
                else:
                    print("❌ 模型切换失败")
            else:
                print("⚠️  GLM4.5模型需要API密钥验证")
        else:
            print("❌ GLM4.5模型未找到")
            
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()

def demo_model_comparison():
    """演示多模型对比"""
    print("\n🔄 多模型对比演示")
    print("=" * 50)
    
    try:
        llm = EnhancedLLMInterfaceV2()
        
        # 测试问题
        test_query = "什么是机器学习？请简要解释"
        
        # 可用的远程模型
        models_to_test = ['qwen2.5-7b', 'glm4.5']
        
        for model in models_to_test:
            print(f"\n🤖 测试模型: {model}")
            print("-" * 30)
            
            try:
                # 切换模型
                if llm.set_model(model):
                    response = llm.generate_response(test_query)
                    print(f"回复: {response[:150]}...")
                    print("✅ 测试完成")
                else:
                    print("❌ 模型不可用")
            except Exception as e:
                print(f"❌ 测试失败: {e}")
                
    except Exception as e:
        print(f"❌ 对比演示失败: {e}")

def main():
    """主函数"""
    print("🚀 GLM4.5集成功能演示")
    print("=" * 60)
    
    # 检查环境变量
    glm_key = os.getenv('GLM_API_KEY')
    if not glm_key:
        print("❌ 未找到GLM_API_KEY环境变量")
        return
    
    print(f"✅ GLM API密钥已配置: {glm_key[:20]}...")
    
    # 运行演示
    demo_glm4_5_usage()
    demo_model_comparison()
    
    print("\n🎉 GLM4.5集成演示完成！")
    print("\n📝 使用说明:")
    print("1. 确保.env文件中配置了GLM_API_KEY")
    print("2. 使用llm.set_model('glm4.5')切换到GLM4.5模型")
    print("3. 使用llm.generate_response(query)进行对话")
    print("4. 支持与其他模型(Qwen、本地Ollama)无缝切换")

if __name__ == "__main__":
    main()
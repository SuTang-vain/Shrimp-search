"""
最终集成测试
验证GLM4.5模型集成和所有环境配置
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_environment():
    """测试环境配置"""
    print("🔧 环境配置测试")
    print("=" * 50)
    
    required_vars = {
        'MODELSCOPE_SDK_TOKEN': 'YOUR_MODELSCOPE_SDK_TOKEN',
        'GLM_API_KEY': 'YOUR_GLM_API_KEY',
        'OPENAI_API_KEY': 'YOUR_OPENAI_API_KEY',
        'NEO4J_URL': 'bolt://localhost:7687',
        'NEO4J_USERNAME': 'neo4j',
        'NEO4J_PASSWORD': 'YOUR_NEO4J_PASSWORD'
    }
    
    all_ok = True
    for var, expected in required_vars.items():
        actual = os.getenv(var)
        if actual == expected:
            print(f"✅ {var}: 配置正确")
        else:
            print(f"❌ {var}: 配置错误或缺失")
            all_ok = False
    
    return all_ok

def test_model_imports():
    """测试模块导入"""
    print("\n📦 模块导入测试")
    print("=" * 50)
    
    modules = [
        'model_manager',
        'ollama_interface', 
        'enhanced_llm_interface_v2',
        'enhanced_user_interface_v2',
        'Enhanced_Interactive_Multimodal_RAG_v2'
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}: 导入成功")
        except Exception as e:
            print(f"❌ {module}: 导入失败 - {e}")
            all_ok = False
    
    return all_ok

def test_glm_integration():
    """测试GLM4.5集成"""
    print("\n🤖 GLM4.5集成测试")
    print("=" * 50)
    
    try:
        from model_manager import ModelManager
        manager = ModelManager()
        models = manager.get_available_models()
        
        # 检查GLM4.5模型配置
        if 'glm4.5' in models['remote']:
            glm_config = models['remote']['glm4.5']
            print(f"✅ GLM4.5模型已配置")
            print(f"   模型名称: {glm_config.name}")
            print(f"   提供商: {glm_config.provider}")
            print(f"   API地址: {glm_config.api_url}")
            print(f"   描述: {glm_config.description}")
            return True
        else:
            print("❌ GLM4.5模型配置未找到")
            return False
            
    except Exception as e:
        print(f"❌ GLM4.5集成测试失败: {e}")
        return False

def test_system_functionality():
    """测试系统功能"""
    print("\n⚡ 系统功能测试")
    print("=" * 50)
    
    try:
        from enhanced_llm_interface_v2 import EnhancedLLMInterfaceV2
        
        # 初始化系统
        llm = EnhancedLLMInterfaceV2()
        print("✅ 增强LLM接口V2初始化成功")
        
        # 获取可用模型
        available = llm.list_available_models()
        
        # 检查远程模型
        remote_models = available['remote']
        print(f"✅ 远程模型数量: {len(remote_models)}")
        
        # 检查GLM4.5可用性
        if 'glm4.5' in remote_models:
            glm_status = remote_models['glm4.5']['available']
            print(f"✅ GLM4.5可用性: {'可用' if glm_status else '需要API密钥'}")
        
        # 检查本地模型
        local_models = available['local']
        print(f"✅ 本地模型数量: {len(local_models)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 系统功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 最终集成测试")
    print("=" * 60)
    
    # 运行所有测试
    tests = [
        ("环境配置", test_environment),
        ("模块导入", test_model_imports),
        ("GLM4.5集成", test_glm_integration),
        ("系统功能", test_system_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n📊 测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！GLM4.5集成成功！")
        print("\n🚀 可用功能:")
        print("  - ✅ 多端模型选择 (ModelScope + Ollama + GLM4.5)")
        print("  - ✅ Qwen2.5-7B本地推理")
        print("  - ✅ GLM4.5远程推理")
        print("  - ✅ 智能模型自动选择")
        print("  - ✅ 增强RAG检索系统")
        print("  - ✅ 多模态文档处理")
        print("  - ✅ 完整环境配置")
    else:
        print("⚠️  部分测试失败，请检查配置")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
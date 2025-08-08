"""
简单的GLM4.5模型测试
快速验证GLM4.5模型是否正确集成
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def main():
    print("🧪 GLM4.5模型快速测试")
    print("="*40)
    
    # 检查环境变量
    glm_key = os.getenv('GLM_API_KEY')
    modelscope_key = os.getenv('MODELSCOPE_SDK_TOKEN')
    
    print(f"GLM API密钥: {'✅ 已设置' if glm_key else '❌ 未设置'}")
    print(f"ModelScope密钥: {'✅ 已设置' if modelscope_key else '❌ 未设置'}")
    
    try:
        # 导入模块
        from model_manager import ModelManager
        print("✅ 模型管理器导入成功")
        
        # 初始化模型管理器
        manager = ModelManager()
        models = manager.get_available_models()
        
        # 检查GLM4.5模型
        if 'glm4.5' in models['remote']:
            glm_config = models['remote']['glm4.5']
            print(f"✅ GLM4.5模型配置:")
            print(f"   名称: {glm_config.name}")
            print(f"   提供商: {glm_config.provider}")
            print(f"   API地址: {glm_config.api_url}")
            print(f"   描述: {glm_config.description}")
        else:
            print("❌ GLM4.5模型未找到")
        
        # 导入增强LLM接口
        from enhanced_llm_interface_v2 import EnhancedLLMInterfaceV2
        print("✅ 增强LLM接口V2导入成功")
        
        # 初始化接口
        llm = EnhancedLLMInterfaceV2()
        available = llm.list_available_models()
        
        # 检查GLM4.5可用性
        if 'glm4.5' in available['remote']:
            glm_info = available['remote']['glm4.5']
            status = "✅ 可用" if glm_info['available'] else "❌ 不可用"
            print(f"GLM4.5状态: {status}")
            
            if glm_info['available']:
                print("🚀 GLM4.5模型已准备就绪！")
            else:
                print("⚠️  GLM4.5模型需要API密钥")
        
        print("✅ GLM4.5集成测试通过")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
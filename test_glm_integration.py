"""
测试GLM4.5模型集成
验证新增的GLM4.5模型是否正常工作
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_glm_model():
    """测试GLM4.5模型功能"""
    print("🧪 测试GLM4.5模型集成")
    print("="*50)
    
    try:
        from enhanced_llm_interface_v2 import EnhancedLLMInterfaceV2
        
        # 初始化LLM接口
        llm = EnhancedLLMInterfaceV2()
        
        # 检查GLM API密钥
        glm_api_key = os.getenv('GLM_API_KEY')
        print(f"GLM API密钥: {'已设置' if glm_api_key else '未设置'}")
        
        # 获取可用模型
        available_models = llm.list_available_models()
        
        print("\n可用模型状态:")
        for model_type, models in available_models.items():
            print(f"\n{model_type.upper()} 模型:")
            for key, info in models.items():
                status = "✅ 可用" if info['available'] else "❌ 不可用"
                provider = info['provider']
                print(f"  - {key} ({provider}): {status}")
        
        # 测试GLM4.5模型
        if 'glm4.5' in available_models['remote'] and available_models['remote']['glm4.5']['available']:
            print(f"\n🚀 测试GLM4.5模型...")
            
            # 设置GLM4.5模型
            if llm.set_model('glm4.5'):
                print("✅ 成功设置GLM4.5模型")
                
                # 测试生成
                test_prompt = "请简单介绍一下你自己"
                print(f"测试提示: {test_prompt}")
                
                result = llm.generate(test_prompt, max_tokens=200, temperature=0.7)
                
                if not result.error:
                    print(f"✅ GLM4.5生成成功:")
                    print(f"   模型: {result.model_key}")
                    print(f"   类型: {result.model_type}")
                    print(f"   时间: {result.generation_time:.2f}秒")
                    print(f"   内容: {result.content[:100]}...")
                else:
                    print(f"❌ GLM4.5生成失败: {result.error}")
            else:
                print("❌ 无法设置GLM4.5模型")
        else:
            print("❌ GLM4.5模型不可用，请检查API密钥配置")
        
        # 测试模型切换
        print(f"\n🔄 测试模型切换功能...")
        
        # 尝试切换到本地模型
        local_models = [key for key, info in available_models['local'].items() 
                       if info['available'] and info.get('installed', False)]
        
        if local_models:
            local_model = local_models[0]
            print(f"切换到本地模型: {local_model}")
            
            if llm.set_model(local_model):
                print("✅ 本地模型切换成功")
                
                # 再切换回GLM4.5
                if available_models['remote']['glm4.5']['available']:
                    if llm.set_model('glm4.5'):
                        print("✅ 成功切换回GLM4.5模型")
                    else:
                        print("❌ 切换回GLM4.5失败")
            else:
                print("❌ 本地模型切换失败")
        else:
            print("⚠️  没有可用的本地模型进行切换测试")
        
        # 显示统计信息
        stats = llm.get_generation_stats()
        print(f"\n📊 生成统计:")
        print(f"   总请求数: {stats['total_requests']}")
        print(f"   成功请求: {stats['successful_requests']}")
        print(f"   失败请求: {stats['failed_requests']}")
        if stats['successful_requests'] > 0:
            print(f"   平均时间: {stats['average_time']:.2f}秒")
            print(f"   成功率: {stats['success_rate']:.1%}")
        
        print("\n✅ GLM4.5集成测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_environment_variables():
    """测试环境变量配置"""
    print("🔧 测试环境变量配置")
    print("="*50)
    
    env_vars = [
        ('MODELSCOPE_SDK_TOKEN', 'ModelScope API密钥'),
        ('GLM_API_KEY', 'GLM API密钥'),
        ('GOOGLE_API_KEY', 'Google API密钥'),
        ('OPENAI_API_KEY', 'OpenAI API密钥'),
        ('NEO4J_URL', 'Neo4j数据库URL'),
        ('NEO4J_USERNAME', 'Neo4j用户名'),
        ('NEO4J_PASSWORD', 'Neo4j密码')
    ]
    
    for var_name, description in env_vars:
        value = os.getenv(var_name)
        if value:
            # 隐藏敏感信息
            if 'key' in var_name.lower() or 'password' in var_name.lower():
                display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            else:
                display_value = value
            print(f"✅ {description}: {display_value}")
        else:
            print(f"❌ {description}: 未设置")
    
    print("\n✅ 环境变量检查完成")

def main():
    """主测试函数"""
    print("🚀 GLM4.5模型集成验证")
    print("="*60)
    
    # 测试环境变量
    test_environment_variables()
    print()
    
    # 测试GLM模型
    test_glm_model()
    
    print("\n🎉 所有测试完成!")
    print("="*60)

if __name__ == "__main__":
    main()
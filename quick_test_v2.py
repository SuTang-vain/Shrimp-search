"""
快速测试增强RAG系统V2的核心功能
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_model_selection():
    """测试模型选择功能"""
    print("🧪 测试模型选择功能")
    print("="*50)
    
    try:
        from enhanced_llm_interface_v2 import EnhancedLLMInterfaceV2
        
        # 初始化LLM接口
        llm = EnhancedLLMInterfaceV2()
        
        # 获取可用模型
        available_models = llm.list_available_models()
        
        print("可用模型:")
        for model_type, models in available_models.items():
            print(f"\n{model_type.upper()} 模型:")
            for key, info in models.items():
                status = "✅ 可用" if info['available'] else "❌ 不可用"
                if model_type == 'local':
                    installed = "已安装" if info.get('installed', False) else "未安装"
                    status += f" ({installed})"
                print(f"  - {key}: {status}")
        
        # 尝试自动选择模型
        print("\n尝试自动选择最佳模型...")
        selected_model = llm.auto_select_best_model()
        
        if selected_model:
            print(f"✅ 成功选择模型: {selected_model}")
            
            # 测试模型
            test_result = llm.test_model()
            if test_result['success']:
                print(f"✅ 模型测试成功: {test_result['response'][:50]}...")
                print(f"   生成时间: {test_result['generation_time']:.2f}秒")
            else:
                print(f"❌ 模型测试失败: {test_result['error']}")
        else:
            print("❌ 未找到可用模型")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("\n" + "="*50)

def test_basic_generation():
    """测试基础生成功能"""
    print("🧪 测试基础生成功能")
    print("="*50)
    
    try:
        from enhanced_llm_interface_v2 import EnhancedLLMInterfaceV2
        
        llm = EnhancedLLMInterfaceV2()
        
        # 自动选择模型
        if llm.auto_select_best_model():
            # 测试简单生成
            test_prompt = "请简单介绍一下人工智能"
            print(f"测试提示: {test_prompt}")
            
            result = llm.generate(test_prompt, max_tokens=200, temperature=0.7)
            
            if not result.error:
                print(f"✅ 生成成功:")
                print(f"   模型: {result.model_key} ({result.model_type})")
                print(f"   时间: {result.generation_time:.2f}秒")
                print(f"   内容: {result.content[:200]}...")
            else:
                print(f"❌ 生成失败: {result.error}")
        else:
            print("❌ 无可用模型")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("\n" + "="*50)

def test_model_switching():
    """测试模型切换功能"""
    print("🧪 测试模型切换功能")
    print("="*50)
    
    try:
        from enhanced_llm_interface_v2 import EnhancedLLMInterfaceV2
        
        llm = EnhancedLLMInterfaceV2()
        available_models = llm.list_available_models()
        
        # 找到可用的模型
        available_keys = []
        for model_type, models in available_models.items():
            for key, info in models.items():
                if info['available']:
                    if model_type == 'local' and info.get('installed', False):
                        available_keys.append(key)
                    elif model_type == 'remote':
                        available_keys.append(key)
        
        if len(available_keys) >= 1:
            # 测试切换到第一个可用模型
            test_key = available_keys[0]
            print(f"尝试切换到模型: {test_key}")
            
            if llm.set_model(test_key):
                print(f"✅ 成功切换到: {test_key}")
                
                current_model = llm.get_current_model()
                print(f"   当前模型: {current_model['key']}")
                print(f"   提供商: {current_model['provider']}")
                print(f"   类型: {current_model['type']}")
                
                # 简单测试
                result = llm.generate("你好", max_tokens=50)
                if not result.error:
                    print(f"✅ 测试生成成功: {result.content[:30]}...")
                else:
                    print(f"❌ 测试生成失败: {result.error}")
            else:
                print(f"❌ 切换失败")
        else:
            print("❌ 没有可用模型进行切换测试")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("\n" + "="*50)

def main():
    """主测试函数"""
    print("🚀 增强RAG系统V2 - 快速功能测试")
    print("="*60)
    
    # 检查环境
    api_key = os.getenv('MODELSCOPE_API_KEY')
    print(f"ModelScope API密钥: {'已设置' if api_key else '未设置'}")
    print()
    
    # 运行测试
    test_model_selection()
    test_basic_generation()
    test_model_switching()
    
    print("🎉 测试完成!")
    print("="*60)

if __name__ == "__main__":
    main()
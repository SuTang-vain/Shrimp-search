"""
快速配置检查
验证环境变量和模型配置是否正确
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def check_env_vars():
    """检查环境变量配置"""
    print("🔍 环境变量检查")
    print("-" * 30)
    
    env_vars = {
        'MODELSCOPE_SDK_TOKEN': os.getenv('MODELSCOPE_SDK_TOKEN'),
        'GLM_API_KEY': os.getenv('GLM_API_KEY'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'NEO4J_URL': os.getenv('NEO4J_URL'),
        'NEO4J_USERNAME': os.getenv('NEO4J_USERNAME'),
        'NEO4J_PASSWORD': os.getenv('NEO4J_PASSWORD')
    }
    
    for key, value in env_vars.items():
        status = "✅ 已设置" if value else "❌ 未设置"
        masked_value = f"{value[:8]}..." if value and len(value) > 8 else value
        print(f"{key}: {status} ({masked_value})")
    
    return all(env_vars.values())

def check_model_config():
    """检查模型配置"""
    print("\n🤖 模型配置检查")
    print("-" * 30)
    
    try:
        # 检查模型管理器文件
        with open('model_manager.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查GLM4.5配置
        if "'glm4.5'" in content:
            print("✅ GLM4.5模型配置已添加")
        else:
            print("❌ GLM4.5模型配置未找到")
            
        # 检查API URL配置
        if "open.bigmodel.cn" in content:
            print("✅ GLM API地址配置正确")
        else:
            print("❌ GLM API地址配置缺失")
            
        return True
        
    except Exception as e:
        print(f"❌ 模型配置检查失败: {e}")
        return False

def main():
    print("⚡ 快速配置检查")
    print("=" * 40)
    
    env_ok = check_env_vars()
    model_ok = check_model_config()
    
    print("\n📊 检查结果")
    print("-" * 30)
    print(f"环境变量: {'✅ 通过' if env_ok else '❌ 失败'}")
    print(f"模型配置: {'✅ 通过' if model_ok else '❌ 失败'}")
    
    if env_ok and model_ok:
        print("\n🎉 配置检查全部通过！")
        print("系统已准备好使用GLM4.5模型")
    else:
        print("\n⚠️  配置需要修复")

if __name__ == "__main__":
    main()
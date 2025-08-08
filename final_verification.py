"""
最终验证脚本 - 确保所有模块都能正常导入和运行
"""

import sys
import traceback

def test_import(module_name, description):
    """测试模块导入"""
    try:
        __import__(module_name)
        print(f"✅ {description}: 导入成功")
        return True
    except Exception as e:
        print(f"❌ {description}: 导入失败 - {e}")
        traceback.print_exc()
        return False

def main():
    """主验证函数"""
    print("🔍 最终系统验证")
    print("="*50)
    
    # 测试所有核心模块
    modules_to_test = [
        ("model_manager", "模型管理器"),
        ("ollama_interface", "Ollama接口"),
        ("enhanced_llm_interface_v2", "增强LLM接口V2"),
        ("enhanced_user_interface_v2", "增强用户界面V2"),
        ("Enhanced_Interactive_Multimodal_RAG_v2", "增强RAG系统V2"),
        ("enhanced_document_manager", "文档管理器"),
        ("enhanced_multimodal_processor", "多模态处理器"),
        ("enhanced_web_research", "网页研究系统"),
        ("performance_monitor", "性能监控器")
    ]
    
    success_count = 0
    total_count = len(modules_to_test)
    
    for module_name, description in modules_to_test:
        if test_import(module_name, description):
            success_count += 1
    
    print("\n" + "="*50)
    print(f"验证结果: {success_count}/{total_count} 模块通过")
    
    if success_count == total_count:
        print("🎉 所有模块验证通过！系统可以正常使用")
        
        # 快速功能测试
        print("\n🧪 快速功能测试")
        print("-"*30)
        
        try:
            from enhanced_llm_interface_v2 import EnhancedLLMInterfaceV2
            
            llm = EnhancedLLMInterfaceV2()
            models = llm.list_available_models()
            
            local_available = any(info['available'] and info.get('installed', False) 
                                for info in models['local'].values())
            remote_available = any(info['available'] 
                                 for info in models['remote'].values())
            
            print(f"本地模型可用: {'✅' if local_available else '❌'}")
            print(f"远程模型可用: {'✅' if remote_available else '❌'}")
            
            if local_available or remote_available:
                print("✅ 系统已准备就绪，可以开始使用！")
            else:
                print("⚠️  系统已安装但需要配置模型")
                
        except Exception as e:
            print(f"❌ 功能测试失败: {e}")
    else:
        print("❌ 部分模块验证失败，请检查依赖和配置")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
"""
增强RAG系统V2演示脚本
展示多端模型选择和基础功能
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_model_manager():
    """演示模型管理器功能"""
    print("="*60)
    print("演示1: 模型管理器功能")
    print("="*60)
    
    try:
        from model_manager import ModelManager
        
        manager = ModelManager()
        print("模型管理器初始化成功")
        
        # 显示可用模型
        print("\n可用模型列表:")
        for model_type, models in manager.available_models.items():
            print(f"\n{model_type.upper()} 模型:")
            for key, config in models.items():
                print(f"  - {key}: {config.description}")
                print(f"    提供商: {config.provider}")
                print(f"    最大令牌: {config.max_tokens}")
        
        # 测试获取模型配置
        print("\n测试获取模型配置:")
        result = manager.get_model_config('qwen2.5-7b')
        if result:
            model_type, config = result
            print(f"模型类型: {model_type}")
            print(f"模型名称: {config.name}")
            print(f"提供商: {config.provider}")
        
        print("✅ 模型管理器演示完成")
        
    except Exception as e:
        print(f"❌ 模型管理器演示失败: {e}")

def demo_ollama_interface():
    """演示Ollama接口功能"""
    print("\n" + "="*60)
    print("演示2: Ollama接口功能")
    print("="*60)
    
    try:
        from ollama_interface import OllamaInterface
        
        interface = OllamaInterface()
        print("Ollama接口初始化成功")
        
        # 检查服务可用性
        is_available = interface.is_available()
        print(f"Ollama服务状态: {'可用' if is_available else '不可用'}")
        
        if is_available:
            # 获取已安装模型
            try:
                models = interface.get_installed_models()
                print(f"\n已安装模型数量: {len(models)}")
                for model in models[:3]:  # 只显示前3个
                    size_gb = model.get('size', 0) / (1024**3)
                    print(f"  - {model['name']} ({size_gb:.1f}GB)")
                
                # 检查特定模型
                qwen_exists = interface.check_model_exists('qwen2.5:7b')
                print(f"\nQwen2.5-7B模型状态: {'已安装' if qwen_exists else '未安装'}")
                
            except Exception as e:
                print(f"获取模型列表失败: {e}")
        else:
            print("Ollama服务不可用，请确保:")
            print("1. Ollama已安装并运行")
            print("2. 服务运行在 http://localhost:11434")
            print("3. 防火墙允许连接")
        
        print("✅ Ollama接口演示完成")
        
    except Exception as e:
        print(f"❌ Ollama接口演示失败: {e}")

def demo_llm_interface():
    """演示LLM接口功能"""
    print("\n" + "="*60)
    print("演示3: 增强LLM接口V2功能")
    print("="*60)
    
    try:
        from enhanced_llm_interface_v2 import EnhancedLLMInterfaceV2
        
        # 获取API密钥
        api_key = os.getenv('MODELSCOPE_API_KEY')
        
        llm = EnhancedLLMInterfaceV2(api_key=api_key)
        print("增强LLM接口V2初始化成功")
        
        # 显示可用模型
        available_models = llm.list_available_models()
        print("\n可用模型状态:")
        
        for model_type, models in available_models.items():
            print(f"\n{model_type.upper()} 模型:")
            for key, info in models.items():
                status = "✅ 可用" if info['available'] else "❌ 不可用"
                print(f"  {key}: {status}")
                if not info['available'] and 'reason' in info:
                    print(f"    原因: {info['reason']}")
        
        # 尝试设置模型
        print("\n尝试设置模型:")
        
        # 优先尝试本地模型
        if llm.set_model('qwen2.5-7b'):
            print("✅ 成功设置本地模型: qwen2.5-7b")
            
            # 测试生成
            print("\n测试文本生成:")
            result = llm.generate("你好，请简单介绍一下自己。", max_tokens=100)
            
            if not result.error:
                print(f"生成内容: {result.content[:100]}...")
                print(f"生成时间: {result.generation_time:.2f}秒")
                print(f"模型类型: {result.model_type}")
            else:
                print(f"生成失败: {result.error}")
                
        elif api_key and llm.set_model('qwen2.5-72b'):
            print("✅ 成功设置远程模型: qwen2.5-72b")
            
            # 测试生成
            print("\n测试文本生成:")
            result = llm.generate("你好，请简单介绍一下自己。", max_tokens=100)
            
            if not result.error:
                print(f"生成内容: {result.content[:100]}...")
                print(f"生成时间: {result.generation_time:.2f}秒")
                print(f"模型类型: {result.model_type}")
            else:
                print(f"生成失败: {result.error}")
        else:
            print("❌ 无法设置任何模型")
            print("请确保:")
            print("1. Ollama服务运行且已安装qwen2.5:7b模型")
            print("2. 或者设置MODELSCOPE_API_KEY环境变量")
        
        print("✅ LLM接口演示完成")
        
    except Exception as e:
        print(f"❌ LLM接口演示失败: {e}")
        import traceback
        traceback.print_exc()

def demo_user_interface():
    """演示用户界面功能"""
    print("\n" + "="*60)
    print("演示4: 用户界面功能")
    print("="*60)
    
    try:
        from enhanced_user_interface_v2 import EnhancedUserInterfaceV2
        from enhanced_llm_interface_v2 import EnhancedLLMInterfaceV2
        
        ui = EnhancedUserInterfaceV2()
        print("用户界面V2初始化成功")
        
        # 模拟可用模型数据
        available_models = {
            'remote': {
                'qwen2.5-72b': {
                    'description': 'Qwen2.5-72B大型语言模型',
                    'available': bool(os.getenv('MODELSCOPE_API_KEY')),
                    'reason': '需要API密钥' if not os.getenv('MODELSCOPE_API_KEY') else None
                }
            },
            'local': {
                'qwen2.5-7b': {
                    'description': 'Qwen2.5-7B本地部署模型',
                    'available': True,
                    'reason': None
                }
            }
        }
        
        print("\n模型选择界面预览:")
        print("(实际使用时会等待用户输入)")
        
        # 显示模型选择界面的格式
        print("\n🤖 可用模型选择:")
        print("="*60)
        
        index = 1
        for model_type, models in available_models.items():
            type_name = "远程模型 (ModelScope)" if model_type == 'remote' else "本地模型 (Ollama)"
            print(f"\n📡 {type_name}:")
            
            for key, info in models.items():
                status = "✅ 可用" if info['available'] else "❌ 不可用"
                print(f"  {index}. {key}")
                print(f"     描述: {info['description']}")
                print(f"     状态: {status}")
                if not info['available'] and info.get('reason'):
                    print(f"     原因: {info['reason']}")
                index += 1
        
        print(f"\n  {index}. auto - 自动选择最佳模型")
        
        print("\n检索模式选择预览:")
        modes = ["快速检索", "深度检索", "主题检索", "智能检索"]
        for i, mode in enumerate(modes, 1):
            print(f"  {i}. {mode}")
        
        print("✅ 用户界面演示完成")
        
    except Exception as e:
        print(f"❌ 用户界面演示失败: {e}")

def demo_integration():
    """演示系统集成功能"""
    print("\n" + "="*60)
    print("演示5: 系统集成功能")
    print("="*60)
    
    try:
        # 检查依赖
        missing_deps = []
        
        try:
            import sentence_transformers
        except ImportError:
            missing_deps.append("sentence-transformers")
        
        try:
            import sklearn
        except ImportError:
            missing_deps.append("scikit-learn")
        
        if missing_deps:
            print(f"❌ 缺少依赖包: {', '.join(missing_deps)}")
            print("请运行: pip install sentence-transformers scikit-learn")
            return
        
        from Enhanced_Interactive_Multimodal_RAG_v2 import EnhancedRAGSystemV2
        
        api_key = os.getenv('MODELSCOPE_API_KEY')
        
        print("正在初始化RAG系统V2...")
        rag_system = EnhancedRAGSystemV2(
            api_key=api_key,
            enable_performance_monitoring=True
        )
        print("✅ RAG系统V2初始化成功")
        
        # 显示系统组件状态
        print("\n系统组件状态:")
        print(f"  LLM接口: ✅ 已加载")
        print(f"  嵌入模型: ✅ 已加载")
        print(f"  向量检索器: ✅ 已加载")
        print(f"  文档管理器: ✅ 已加载")
        print(f"  多模态处理器: ✅ 已加载")
        print(f"  网页研究系统: ✅ 已加载")
        print(f"  性能监控: ✅ 已启用")
        
        # 显示可用模型
        available_models = rag_system.list_available_models()
        print(f"\n可用模型数量:")
        for model_type, models in available_models.items():
            available_count = sum(1 for m in models.values() if m.get('available', False))
            print(f"  {model_type}: {available_count}/{len(models)} 个可用")
        
        print("✅ 系统集成演示完成")
        
    except Exception as e:
        print(f"❌ 系统集成演示失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主演示函数"""
    print("增强RAG系统V2 - 功能演示")
    print("支持多端模型选择 (ModelScope + Ollama)")
    print("="*60)
    
    # 加载环境变量
    load_dotenv()
    
    # 检查环境
    api_key = os.getenv('MODELSCOPE_API_KEY')
    print(f"ModelScope API密钥: {'已设置' if api_key else '未设置'}")
    
    # 运行演示
    demo_model_manager()
    demo_ollama_interface()
    demo_llm_interface()
    demo_user_interface()
    demo_integration()
    
    print("\n" + "="*60)
    print("演示完成!")
    print("="*60)
    
    print("\n下一步:")
    print("1. 确保Ollama服务运行: ollama serve")
    print("2. 安装Qwen2.5模型: ollama pull qwen2.5:7b")
    print("3. 设置API密钥: export MODELSCOPE_API_KEY=your_key")
    print("4. 运行完整系统: python Enhanced_Interactive_Multimodal_RAG_v2.py")
    
    print("\n测试系统:")
    print("运行测试: python -m pytest test_rag_system_v2.py -v")

if __name__ == "__main__":
    main()
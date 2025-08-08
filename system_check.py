#!/usr/bin/env python3
"""
交互式多模态RAG系统 - 系统状态检查
检查所有依赖、配置和功能是否正常
"""

import os
import sys
import importlib
from pathlib import Path
from dotenv import load_dotenv

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)

def check_python_environment():
    """检查Python环境"""
    print_header("Python环境检查")
    
    # Python版本
    version = sys.version_info
    print(f"🐍 Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python版本符合要求 (>=3.8)")
    else:
        print("❌ Python版本过低，需要3.8或更高版本")
        return False
    
    # 工作目录
    current_dir = Path.cwd()
    print(f"📁 当前目录: {current_dir}")
    
    # 检查关键文件
    key_files = [
        "Interactive_Multimodal_RAG.py",
        "RAG_WEB_TOPIC_Enhanced.py", 
        "install_dependencies.py",
        "requirements.txt",
        ".env"
    ]
    
    print("\n📋 关键文件检查:")
    missing_files = []
    for file in key_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (缺失)")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️ 缺失 {len(missing_files)} 个关键文件")
        return False
    
    return True

def check_dependencies():
    """检查依赖包"""
    print_header("依赖包检查")
    
    # 核心依赖
    core_deps = [
        ("numpy", "NumPy - 数值计算"),
        ("sklearn", "Scikit-learn - 机器学习"),
        ("requests", "Requests - HTTP请求"),
        ("dotenv", "Python-dotenv - 环境变量"),
        ("colorama", "Colorama - 终端颜色"),
        ("bs4", "BeautifulSoup4 - HTML解析"),
    ]
    
    print("🔧 核心依赖:")
    core_failed = []
    for module, desc in core_deps:
        try:
            importlib.import_module(module)
            print(f"✅ {desc}")
        except ImportError:
            print(f"❌ {desc} (未安装)")
            core_failed.append(module)
    
    # AI和ML依赖
    ai_deps = [
        ("camel", "CAMEL - AI智能体框架"),
        ("sentence_transformers", "Sentence Transformers - 文本嵌入"),
        ("transformers", "Transformers - 预训练模型"),
        ("torch", "PyTorch - 深度学习框架"),
    ]
    
    print("\n🤖 AI/ML依赖:")
    ai_failed = []
    for module, desc in ai_deps:
        try:
            importlib.import_module(module)
            print(f"✅ {desc}")
        except ImportError:
            print(f"❌ {desc} (未安装)")
            ai_failed.append(module)
    
    # 文档处理依赖
    doc_deps = [
        ("pypdf", "PyPDF - PDF处理"),
        ("unstructured", "Unstructured - 文档解析"),
        ("PIL", "Pillow - 图像处理"),
    ]
    
    print("\n📄 文档处理依赖:")
    doc_failed = []
    for module, desc in doc_deps:
        try:
            importlib.import_module(module)
            print(f"✅ {desc}")
        except ImportError:
            print(f"❌ {desc} (未安装)")
            doc_failed.append(module)
    
    # 可选依赖
    optional_deps = [
        ("neo4j", "Neo4j - 知识图谱数据库"),
        ("qdrant_client", "Qdrant - 向量数据库"),
        ("agentops", "AgentOps - 智能体监控"),
        ("firecrawl", "Firecrawl - 网页爬取"),
    ]
    
    print("\n🔧 可选依赖:")
    optional_failed = []
    for module, desc in optional_deps:
        try:
            importlib.import_module(module)
            print(f"✅ {desc}")
        except ImportError:
            print(f"⚠️ {desc} (未安装，不影响核心功能)")
            optional_failed.append(module)
    
    # 总结
    total_failed = len(core_failed) + len(ai_failed) + len(doc_failed)
    if total_failed == 0:
        print(f"\n🎉 所有核心依赖检查通过！")
        if optional_failed:
            print(f"💡 {len(optional_failed)} 个可选依赖未安装，不影响基本功能")
        return True
    else:
        print(f"\n❌ {total_failed} 个核心依赖缺失")
        print("💡 请运行: python install_dependencies.py")
        return False

def check_environment_config():
    """检查环境配置"""
    print_header("环境配置检查")
    
    # 加载.env文件
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env文件不存在")
        print("💡 请运行安装脚本创建配置文件")
        return False
    
    load_dotenv()
    
    # 检查必需配置
    required_configs = [
        ("MODELSCOPE_SDK_TOKEN", "ModelScope API密钥", True),
    ]
    
    # 检查可选配置
    optional_configs = [
        ("OPENAI_API_KEY", "OpenAI API密钥", False),
        ("FIRECRAWL_API_KEY", "Firecrawl API密钥", False),
        ("NEO4J_PASSWORD", "Neo4j数据库密码", False),
        ("AGENTOPS_API_KEY", "AgentOps API密钥", False),
    ]
    
    print("🔑 必需配置:")
    missing_required = []
    for key, desc, required in required_configs:
        value = os.getenv(key)
        if value and value != f"your_{key.lower()}_here":
            masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"✅ {desc}: {masked_value}")
        else:
            print(f"❌ {desc}: 未配置")
            if required:
                missing_required.append(key)
    
    print("\n🔧 可选配置:")
    for key, desc, required in optional_configs:
        value = os.getenv(key)
        if value and value != f"your_{key.lower()}_here":
            masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"✅ {desc}: {masked_value}")
        else:
            print(f"⚠️ {desc}: 未配置")
    
    if missing_required:
        print(f"\n❌ 缺少 {len(missing_required)} 个必需配置")
        print("💡 请编辑.env文件设置API密钥")
        return False
    else:
        print(f"\n✅ 必需配置检查通过")
        return True

def check_system_functionality():
    """检查系统功能"""
    print_header("系统功能检查")
    
    try:
        # 测试导入主要模块
        print("📦 导入主要模块...")
        
        try:
            from Interactive_Multimodal_RAG import InteractiveMultimodalRAG
            print("✅ Interactive_Multimodal_RAG 导入成功")
        except Exception as e:
            print(f"❌ Interactive_Multimodal_RAG 导入失败: {e}")
            return False
        
        try:
            from RAG_WEB_TOPIC_Enhanced import EnhancedInteractiveResearchSystem
            print("✅ RAG_WEB_TOPIC_Enhanced 导入成功")
        except Exception as e:
            print(f"⚠️ RAG_WEB_TOPIC_Enhanced 导入失败: {e}")
        
        # 测试CAMEL框架
        print("\n🤖 测试CAMEL框架...")
        try:
            from camel.models import ModelFactory
            from camel.types import ModelPlatformType
            print("✅ CAMEL框架核心组件可用")
        except Exception as e:
            print(f"❌ CAMEL框架测试失败: {e}")
            return False
        
        # 测试嵌入模型
        print("\n🧠 测试嵌入模型...")
        try:
            from sentence_transformers import SentenceTransformer
            print("✅ Sentence Transformers 可用")
        except Exception as e:
            print(f"❌ Sentence Transformers 测试失败: {e}")
            return False
        
        # 测试PDF处理
        print("\n📄 测试PDF处理...")
        try:
            from pypdf import PdfReader
            from unstructured.partition.auto import partition
            print("✅ PDF处理组件可用")
        except Exception as e:
            print(f"❌ PDF处理测试失败: {e}")
            return False
        
        print("\n🎉 系统功能检查通过！")
        return True
        
    except Exception as e:
        print(f"❌ 系统功能检查失败: {e}")
        return False

def generate_report():
    """生成检查报告"""
    print_header("系统状态报告")
    
    # 执行所有检查
    checks = [
        ("Python环境", check_python_environment),
        ("依赖包", check_dependencies),
        ("环境配置", check_environment_config),
        ("系统功能", check_system_functionality),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ {name}检查异常: {e}")
            results[name] = False
    
    # 生成总结
    print_header("检查总结")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"📊 检查结果: {passed}/{total} 项通过")
    
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {name}: {status}")
    
    if passed == total:
        print("\n🎉 系统状态良好，可以正常使用！")
        print("\n🚀 启动命令:")
        print("   python Interactive_Multimodal_RAG.py")
        return True
    else:
        print(f"\n⚠️ 发现 {total - passed} 个问题，请按照上述提示修复")
        print("\n🔧 修复建议:")
        if not results.get("依赖包", True):
            print("   1. 运行: python install_dependencies.py")
        if not results.get("环境配置", True):
            print("   2. 编辑.env文件，设置API密钥")
        print("   3. 重新运行: python system_check.py")
        return False

def main():
    """主函数"""
    print("🔍 交互式多模态RAG系统 - 状态检查")
    print("=" * 60)
    
    try:
        success = generate_report()
        return success
    except KeyboardInterrupt:
        print("\n\n👋 检查被用户中断")
        return False
    except Exception as e:
        print(f"\n❌ 检查过程出错: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
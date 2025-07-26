"""
增强依赖安装脚本
安装文档管理、缓存和多格式支持所需的依赖包
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """运行命令并处理错误"""
    print(f"⏳ {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description}完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e}")
        if e.stdout:
            print(f"输出: {e.stdout}")
        if e.stderr:
            print(f"错误: {e.stderr}")
        return False

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print(f"🐍 Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    
    print("✅ Python版本符合要求")
    return True

def install_basic_dependencies():
    """安装基础依赖"""
    print("\n📦 安装基础依赖包...")
    
    basic_packages = [
        "requests>=2.28.0",
        "python-dotenv>=0.19.0", 
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0",
        "tqdm>=4.64.0",
        "psutil>=5.9.0"
    ]
    
    for package in basic_packages:
        if not run_command(f"pip install {package}", f"安装 {package.split('>=')[0]}"):
            return False
    
    return True

def install_document_processing():
    """安装文档处理依赖"""
    print("\n📄 安装文档处理依赖...")
    
    doc_packages = [
        "PyMuPDF>=1.20.0",  # PDF处理
        "python-docx>=0.8.11",  # DOCX处理
        "openpyxl>=3.0.9",  # Excel处理
        "pandas>=1.3.0",  # 数据处理
        "python-pptx>=0.6.21",  # PowerPoint处理
        "docx2txt>=0.8",  # DOC文件处理
        "striprtf>=0.0.12"  # RTF文件处理
    ]
    
    for package in doc_packages:
        if not run_command(f"pip install {package}", f"安装 {package.split('>=')[0]}"):
            print(f"⚠️ {package.split('>=')[0]} 安装失败，但可能不影响核心功能")
    
    return True

def install_ml_dependencies():
    """安装机器学习依赖"""
    print("\n🤖 安装机器学习依赖...")
    
    ml_packages = [
        "sentence-transformers>=2.2.0",
        "torch>=1.12.0",
        "transformers>=4.20.0"
    ]
    
    for package in ml_packages:
        if not run_command(f"pip install {package}", f"安装 {package.split('>=')[0]}"):
            print(f"❌ {package.split('>=')[0]} 安装失败，这可能影响核心功能")
            return False
    
    return True

def install_web_dependencies():
    """安装网页处理依赖"""
    print("\n🌐 安装网页处理依赖...")
    
    web_packages = [
        "beautifulsoup4>=4.11.0",
        "lxml>=4.9.0",
        "duckduckgo-search>=3.8.0"
    ]
    
    for package in web_packages:
        if not run_command(f"pip install {package}", f"安装 {package.split('>=')[0]}"):
            print(f"⚠️ {package.split('>=')[0]} 安装失败，网页功能可能受限")
    
    return True

def install_ui_dependencies():
    """安装用户界面依赖"""
    print("\n🎨 安装用户界面依赖...")
    
    ui_packages = [
        "rich>=12.0.0",
        "colorama>=0.4.4"
    ]
    
    for package in ui_packages:
        if not run_command(f"pip install {package}", f"安装 {package.split('>=')[0]}"):
            print(f"⚠️ {package.split('>=')[0]} 安装失败，界面可能不够美观")
    
    return True

def install_optional_dependencies():
    """安装可选依赖"""
    print("\n🔧 安装可选依赖...")
    
    optional_packages = [
        "Pillow>=9.0.0",  # 图像处理
        "pytesseract>=0.3.9",  # OCR
        "streamlit>=1.12.0",  # Web界面
        "selenium>=4.5.0"  # 网页自动化
    ]
    
    for package in optional_packages:
        if not run_command(f"pip install {package}", f"安装 {package.split('>=')[0]}"):
            print(f"⚠️ {package.split('>=')[0]} 安装失败，某些功能可能不可用")
    
    return True

def install_camel_dependencies():
    """安装CAMEL相关依赖"""
    print("\n🐪 安装CAMEL框架依赖...")
    
    camel_packages = [
        "camel-ai>=0.1.0",
        "modelscope>=1.9.0",
        "dashscope>=1.14.0"
    ]
    
    for package in camel_packages:
        if not run_command(f"pip install {package}", f"安装 {package.split('>=')[0]}"):
            print(f"⚠️ {package.split('>=')[0]} 安装失败，CAMEL功能可能受限")
    
    return True

def verify_installation():
    """验证安装"""
    print("\n🔍 验证安装...")
    
    test_imports = [
        ("numpy", "NumPy"),
        ("sklearn", "Scikit-learn"),
        ("sentence_transformers", "Sentence Transformers"),
        ("fitz", "PyMuPDF"),
        ("docx", "python-docx"),
        ("pandas", "Pandas"),
        ("bs4", "BeautifulSoup4"),
        ("rich", "Rich"),
        ("requests", "Requests")
    ]
    
    success_count = 0
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✅ {name} 导入成功")
            success_count += 1
        except ImportError:
            print(f"❌ {name} 导入失败")
    
    print(f"\n📊 验证结果: {success_count}/{len(test_imports)} 个包成功导入")
    
    if success_count >= len(test_imports) * 0.8:
        print("✅ 大部分依赖安装成功，系统应该可以正常运行")
        return True
    else:
        print("⚠️ 多个依赖安装失败，系统可能无法正常运行")
        return False

def create_test_environment():
    """创建测试环境"""
    print("\n🧪 创建测试环境...")
    
    # 创建必要的目录
    directories = ["document_cache", "logs", "temp"]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            print(f"✅ 创建目录: {dir_name}")
    
    # 检查环境变量文件
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️ .env文件不存在，请确保配置了必要的API密钥")
    else:
        print("✅ .env文件存在")
    
    return True

def main():
    """主安装函数"""
    print("🚀 增强文档管理系统依赖安装")
    print("="*60)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 升级pip
    print("\n📦 升级pip...")
    run_command("python -m pip install --upgrade pip", "升级pip")
    
    # 安装各类依赖
    steps = [
        (install_basic_dependencies, "基础依赖"),
        (install_document_processing, "文档处理依赖"),
        (install_ml_dependencies, "机器学习依赖"),
        (install_web_dependencies, "网页处理依赖"),
        (install_ui_dependencies, "用户界面依赖"),
        (install_optional_dependencies, "可选依赖"),
        (install_camel_dependencies, "CAMEL框架依赖")
    ]
    
    failed_steps = []
    for step_func, step_name in steps:
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ {step_name}安装过程中出现异常: {e}")
            failed_steps.append(step_name)
    
    # 验证安装
    verify_installation()
    
    # 创建测试环境
    create_test_environment()
    
    # 总结
    print("\n" + "="*60)
    print("📋 安装总结")
    print("="*60)
    
    if failed_steps:
        print("⚠️ 以下步骤安装失败:")
        for step in failed_steps:
            print(f"  • {step}")
        print("\n建议手动安装失败的依赖包")
    else:
        print("✅ 所有依赖安装完成!")
    
    print("\n🎯 下一步:")
    print("1. 确保.env文件包含必要的API密钥")
    print("2. 运行 python demo_document_management.py 测试功能")
    print("3. 运行 python Enhanced_Interactive_Multimodal_RAG.py 启动系统")
    
    print("\n🎉 安装脚本执行完成!")

if __name__ == "__main__":
    main()
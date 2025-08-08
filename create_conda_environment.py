"""
为增强的交互式多模态RAG系统创建独立的Anaconda环境
确保所有依赖正确安装，避免版本冲突
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class CondaEnvironmentCreator:
    """Conda环境创建器"""
    
    def __init__(self):
        self.env_name = "enhanced_rag_system"
        self.python_version = "3.10"
        self.system_info = self.get_system_info()
        
    def get_system_info(self):
        """获取系统信息"""
        return {
            "platform": platform.system(),
            "architecture": platform.machine(),
            "python_version": platform.python_version()
        }
    
    def check_conda_installation(self):
        """检查Conda是否已安装"""
        try:
            result = subprocess.run(
                ["conda", "--version"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            print(f"✅ 检测到Conda: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ 未检测到Conda安装")
            print("请先安装Anaconda或Miniconda:")
            print("  - Anaconda: https://www.anaconda.com/products/distribution")
            print("  - Miniconda: https://docs.conda.io/en/latest/miniconda.html")
            return False
    
    def create_environment_yaml(self):
        """创建environment.yml文件"""
        yaml_content = f"""
name: {self.env_name}
channels:
  - conda-forge
  - pytorch
  - defaults
dependencies:
  - python={self.python_version}
  - pip
  
  # 基础科学计算
  - numpy>=1.21.0
  - scipy>=1.7.0
  - scikit-learn>=1.0.0
  - pandas>=1.3.0
  
  # 机器学习框架
  - pytorch>=1.12.0
  - torchvision
  - torchaudio
  
  # 文档处理
  - pillow>=9.0.0
  - opencv
  
  # 系统工具
  - psutil>=5.9.0
  
  # 通过pip安装的包
  - pip:
    # CAMEL框架和AI相关
    - camel-ai>=0.1.0
    - sentence-transformers>=2.2.0
    - transformers>=4.20.0
    
    # 文档处理增强
    - pypdf>=3.0.0
    - unstructured[pdf,image,tables,docx]>=0.10.0
    - python-docx>=0.8.11
    - docx2txt>=0.8
    - striprtf>=0.0.12
    - python-pptx>=0.6.21
    - openpyxl>=3.0.9
    - tabula-py>=2.5.0
    
    # 网络请求和爬虫
    - requests>=2.28.0
    - beautifulsoup4>=4.11.0
    - selenium>=4.0.0
    - lxml>=4.9.0
    
    # 环境和配置
    - python-dotenv>=0.19.0
    - colorama>=0.4.4
    - rich>=12.0.0
    
    # 数据处理
    - json5>=0.9.0
    
    # 评估和指标
    - rouge-score>=0.1.2
    - nltk>=3.7
    
    # 向量数据库
    - qdrant-client>=1.0.0
    - chromadb>=0.4.0
    
    # 知识图谱
    - neo4j>=5.0.0
    - networkx>=2.8.0
    
    # 监控和日志
    - agentops>=0.2.0
    - loguru>=0.6.0
    
    # 图像处理和OCR
    - pytesseract>=0.3.10
    - PyMuPDF>=1.23.0
    
    # 可选功能包
    - firecrawl-py>=0.0.5
    - duckduckgo-search>=3.0.0
    - wikipedia>=1.4.0
    - arxiv>=1.4.0
    - youtube-transcript-api>=0.5.0
    
    # 开发和测试工具
    - pytest>=7.0.0
    - black>=22.0.0
    - flake8>=4.0.0
    - tqdm>=4.64.0
"""
        
        with open("environment.yml", "w", encoding="utf-8") as f:
            f.write(yaml_content.strip())
        
        print("✅ 创建environment.yml文件成功")
    
    def create_environment(self):
        """创建Conda环境"""
        print(f"🚀 开始创建Conda环境: {self.env_name}")
        print(f"📋 Python版本: {self.python_version}")
        print(f"💻 系统平台: {self.system_info['platform']}")
        
        try:
            # 检查环境是否已存在
            result = subprocess.run(
                ["conda", "env", "list"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            if self.env_name in result.stdout:
                print(f"⚠️ 环境 {self.env_name} 已存在")
                choice = input("是否删除现有环境并重新创建? (y/n): ").lower()
                if choice == 'y':
                    self.remove_environment()
                else:
                    print("❌ 取消创建环境")
                    return False
            
            # 使用environment.yml创建环境
            print("⏳ 正在创建环境，这可能需要几分钟...")
            subprocess.run(
                ["conda", "env", "create", "-f", "environment.yml"], 
                check=True
            )
            
            print(f"✅ 环境 {self.env_name} 创建成功!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 创建环境失败: {e}")
            return False
    
    def remove_environment(self):
        """删除现有环境"""
        try:
            print(f"🗑️ 删除现有环境: {self.env_name}")
            subprocess.run(
                ["conda", "env", "remove", "-n", self.env_name, "-y"], 
                check=True
            )
            print("✅ 环境删除成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ 删除环境失败: {e}")
    
    def install_additional_packages(self):
        """安装额外的包"""
        print("📦 安装额外的Python包...")
        
        additional_packages = [
            "sentence-transformers[onnx]",
            "transformers[torch]"
        ]
        
        for package in additional_packages:
            try:
                print(f"⏳ 安装 {package}...")
                subprocess.run([
                    "conda", "run", "-n", self.env_name, 
                    "pip", "install", package
                ], check=True)
                print(f"✅ {package} 安装成功")
            except subprocess.CalledProcessError:
                print(f"⚠️ {package} 安装失败，跳过")
    
    def verify_installation(self):
        """验证安装"""
        print("🔍 验证环境安装...")
        
        test_imports = [
            "numpy",
            "pandas", 
            "torch",
            "transformers",
            "sentence_transformers",
            "camel",
            "rich",
            "requests",
            "beautifulsoup4"
        ]
        
        failed_imports = []
        
        for module in test_imports:
            try:
                result = subprocess.run([
                    "conda", "run", "-n", self.env_name,
                    "python", "-c", f"import {module}; print(f'{module}: OK')"
                ], capture_output=True, text=True, check=True)
                print(f"✅ {result.stdout.strip()}")
            except subprocess.CalledProcessError:
                failed_imports.append(module)
                print(f"❌ {module}: 导入失败")
        
        if failed_imports:
            print(f"\n⚠️ 以下模块导入失败: {', '.join(failed_imports)}")
            print("请手动安装这些包或检查版本兼容性")
            return False
        else:
            print("\n✅ 所有核心模块验证通过!")
            return True
    
    def create_activation_script(self):
        """创建环境激活脚本"""
        
        # Windows批处理脚本
        bat_content = f"""@echo off
echo 🚀 激活增强RAG系统环境...
call conda activate {self.env_name}
if %errorlevel% neq 0 (
    echo ❌ 环境激活失败
    pause
    exit /b 1
)

echo ✅ 环境已激活: {self.env_name}
echo 📋 可用命令:
echo   python Enhanced_Interactive_Multimodal_RAG.py  - 启动主程序
echo   python demo_enhanced_features.py              - 运行演示
echo   python quick_test_enhanced_features.py        - 快速测试
echo   python demo_document_management.py            - 文档管理演示
echo.
cmd /k
"""
        
        with open("activate_env.bat", "w", encoding="utf-8") as f:
            f.write(bat_content)
        
        # Linux/Mac shell脚本
        sh_content = f"""#!/bin/bash
echo "🚀 激活增强RAG系统环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate {self.env_name}

if [ $? -ne 0 ]; then
    echo "❌ 环境激活失败"
    exit 1
fi

echo "✅ 环境已激活: {self.env_name}"
echo "📋 可用命令:"
echo "  python Enhanced_Interactive_Multimodal_RAG.py  - 启动主程序"
echo "  python demo_enhanced_features.py              - 运行演示"
echo "  python quick_test_enhanced_features.py        - 快速测试"
echo "  python demo_document_management.py            - 文档管理演示"
echo ""
bash
"""
        
        with open("activate_env.sh", "w", encoding="utf-8") as f:
            f.write(sh_content)
        
        # 设置执行权限 (Linux/Mac)
        if platform.system() != "Windows":
            os.chmod("activate_env.sh", 0o755)
        
        print("✅ 创建环境激活脚本成功")
        print("  Windows: activate_env.bat")
        print("  Linux/Mac: activate_env.sh")
    
    def create_jupyter_kernel(self):
        """为环境创建Jupyter内核"""
        try:
            print("📓 创建Jupyter内核...")
            subprocess.run([
                "conda", "run", "-n", self.env_name,
                "python", "-m", "ipykernel", "install", "--user",
                "--name", self.env_name,
                "--display-name", f"Python ({self.env_name})"
            ], check=True)
            print("✅ Jupyter内核创建成功")
        except subprocess.CalledProcessError:
            print("⚠️ Jupyter内核创建失败，可能需要先安装jupyter")
    
    def print_usage_instructions(self):
        """打印使用说明"""
        print("\n" + "="*60)
        print("🎉 环境创建完成!")
        print("="*60)
        print(f"环境名称: {self.env_name}")
        print(f"Python版本: {self.python_version}")
        print(f"系统平台: {self.system_info['platform']}")
        
        print("\n📋 使用方法:")
        print("1. 激活环境:")
        if platform.system() == "Windows":
            print(f"   conda activate {self.env_name}")
            print("   或双击 activate_env.bat")
        else:
            print(f"   conda activate {self.env_name}")
            print("   或运行 ./activate_env.sh")
        
        print("\n2. 运行程序:")
        print("   python Enhanced_Interactive_Multimodal_RAG.py")
        
        print("\n3. 运行测试:")
        print("   python quick_test_enhanced_features.py")
        
        print("\n4. 退出环境:")
        print("   conda deactivate")
        
        print("\n5. 删除环境 (如需要):")
        print(f"   conda env remove -n {self.env_name}")
        
        print("\n📝 注意事项:")
        print("- 首次运行可能需要下载模型文件")
        print("- 确保.env文件中配置了正确的API密钥")
        print("- 如遇到包冲突，可尝试重新创建环境")

def main():
    """主函数"""
    print("🚀 增强RAG系统 - Conda环境创建器")
    print("="*60)
    
    creator = CondaEnvironmentCreator()
    
    # 检查Conda安装
    if not creator.check_conda_installation():
        return
    
    try:
        # 创建environment.yml
        creator.create_environment_yaml()
        
        # 创建环境
        if not creator.create_environment():
            return
        
        # 安装额外包
        creator.install_additional_packages()
        
        # 验证安装
        if not creator.verify_installation():
            print("⚠️ 部分包验证失败，但环境基本可用")
        
        # 创建激活脚本
        creator.create_activation_script()
        
        # 创建Jupyter内核
        creator.create_jupyter_kernel()
        
        # 打印使用说明
        creator.print_usage_instructions()
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 创建过程中出现错误: {e}")
        print("请检查网络连接和Conda配置")

if __name__ == "__main__":
    main()
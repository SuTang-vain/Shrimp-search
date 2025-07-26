"""
系统健康检查脚本
验证Conda环境和所有依赖是否正确安装
"""

import os
import sys
import subprocess
import importlib
import platform
from pathlib import Path

class SystemHealthChecker:
    """系统健康检查器"""
    
    def __init__(self):
        self.env_name = "enhanced_rag_system"
        self.required_packages = {
            # 核心依赖
            "numpy": "数值计算库",
            "pandas": "数据处理库", 
            "torch": "PyTorch深度学习框架",
            "transformers": "Hugging Face模型库",
            "sentence_transformers": "句子嵌入库",
            
            # CAMEL相关
            "camel": "CAMEL AI框架",
            
            # 文档处理
            "pypdf": "PDF处理库",
            "docx": "Word文档处理",
            "openpyxl": "Excel处理",
            "PyMuPDF": "高级PDF处理",
            
            # 网络和界面
            "requests": "HTTP请求库",
            "beautifulsoup4": "HTML解析库",
            "rich": "终端美化库",
            
            # 系统工具
            "psutil": "系统监控库",
            "dotenv": "环境变量管理"
        }
        
        self.optional_packages = {
            "selenium": "浏览器自动化",
            "qdrant_client": "Qdrant向量数据库",
            "chromadb": "ChromaDB向量数据库",
            "neo4j": "Neo4j图数据库",
            "pytesseract": "OCR文字识别"
        }
        
        self.system_files = [
            "Enhanced_Interactive_Multimodal_RAG.py",
            "enhanced_llm_interface.py",
            "enhanced_multimodal_processor.py",
            "enhanced_web_research.py",
            "performance_monitor.py",
            "enhanced_user_interface.py",
            "enhanced_document_manager.py",
            ".env"
        ]
    
    def print_header(self, title):
        """打印标题"""
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")
    
    def check_system_info(self):
        """检查系统信息"""
        self.print_header("系统信息")
        
        info = {
            "操作系统": platform.system(),
            "系统版本": platform.release(),
            "处理器架构": platform.machine(),
            "Python版本": platform.python_version(),
            "Python路径": sys.executable
        }
        
        for key, value in info.items():
            print(f"📋 {key}: {value}")
        
        return True
    
    def check_conda_environment(self):
        """检查Conda环境"""
        self.print_header("Conda环境检查")
        
        try:
            # 检查conda是否可用
            result = subprocess.run(
                ["conda", "--version"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            print(f"✅ Conda版本: {result.stdout.strip()}")
            
            # 检查环境是否存在
            result = subprocess.run(
                ["conda", "env", "list"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            if self.env_name in result.stdout:
                print(f"✅ 环境 {self.env_name} 已创建")
                
                # 检查当前是否在目标环境中
                current_env = os.environ.get('CONDA_DEFAULT_ENV', '')
                if current_env == self.env_name:
                    print(f"✅ 当前环境: {current_env}")
                    return True
                else:
                    print(f"⚠️ 当前环境: {current_env}")
                    print(f"💡 请激活环境: conda activate {self.env_name}")
                    return False
            else:
                print(f"❌ 环境 {self.env_name} 不存在")
                print(f"💡 请运行: python create_conda_environment.py")
                return False
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Conda未安装或不可用")
            print("💡 请安装Anaconda或Miniconda")
            return False
    
    def check_required_packages(self):
        """检查必需包"""
        self.print_header("必需包检查")
        
        failed_packages = []
        
        for package, description in self.required_packages.items():
            try:
                # 特殊处理某些包名
                import_name = package
                if package == "PyMuPDF":
                    import_name = "fitz"
                elif package == "beautifulsoup4":
                    import_name = "bs4"
                elif package == "dotenv":
                    import_name = "dotenv"
                
                importlib.import_module(import_name)
                print(f"✅ {package}: {description}")
                
            except ImportError:
                print(f"❌ {package}: {description} - 未安装")
                failed_packages.append(package)
        
        if failed_packages:
            print(f"\n⚠️ 缺失的必需包: {', '.join(failed_packages)}")
            print("💡 请运行: pip install " + " ".join(failed_packages))
            return False
        else:
            print(f"\n✅ 所有必需包已安装 ({len(self.required_packages)}个)")
            return True
    
    def check_optional_packages(self):
        """检查可选包"""
        self.print_header("可选包检查")
        
        available_packages = []
        missing_packages = []
        
        for package, description in self.optional_packages.items():
            try:
                importlib.import_module(package)
                print(f"✅ {package}: {description}")
                available_packages.append(package)
                
            except ImportError:
                print(f"⚠️ {package}: {description} - 未安装")
                missing_packages.append(package)
        
        print(f"\n📊 可选包统计:")
        print(f"  已安装: {len(available_packages)}/{len(self.optional_packages)}")
        
        if missing_packages:
            print(f"  缺失包: {', '.join(missing_packages)}")
            print("💡 这些包是可选的，不影响核心功能")
        
        return True
    
    def check_system_files(self):
        """检查系统文件"""
        self.print_header("系统文件检查")
        
        missing_files = []
        
        for file_path in self.system_files:
            if Path(file_path).exists():
                size = Path(file_path).stat().st_size
                print(f"✅ {file_path} ({size:,} bytes)")
            else:
                print(f"❌ {file_path} - 文件不存在")
                missing_files.append(file_path)
        
        if missing_files:
            print(f"\n⚠️ 缺失文件: {', '.join(missing_files)}")
            return False
        else:
            print(f"\n✅ 所有系统文件存在 ({len(self.system_files)}个)")
            return True
    
    def check_environment_variables(self):
        """检查环境变量"""
        self.print_header("环境变量检查")
        
        required_vars = [
            "MODELSCOPE_SDK_TOKEN",
            "OPENAI_API_KEY"
        ]
        
        optional_vars = [
            "GOOGLE_API_KEY",
            "BING_API_KEY",
            "NEO4J_URL",
            "NEO4J_USERNAME",
            "NEO4J_PASSWORD"
        ]
        
        # 尝试加载.env文件
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ .env文件已加载")
        except:
            print("⚠️ 无法加载.env文件")
        
        # 检查必需变量
        missing_required = []
        for var in required_vars:
            value = os.getenv(var)
            if value:
                masked_value = value[:8] + "..." if len(value) > 8 else value
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"❌ {var}: 未设置")
                missing_required.append(var)
        
        # 检查可选变量
        available_optional = []
        for var in optional_vars:
            value = os.getenv(var)
            if value:
                masked_value = value[:8] + "..." if len(value) > 8 else value
                print(f"✅ {var}: {masked_value}")
                available_optional.append(var)
            else:
                print(f"⚠️ {var}: 未设置 (可选)")
        
        if missing_required:
            print(f"\n❌ 缺失必需环境变量: {', '.join(missing_required)}")
            print("💡 请在.env文件中配置这些变量")
            return False
        else:
            print(f"\n✅ 所有必需环境变量已配置")
            return True
    
    def check_model_availability(self):
        """检查模型可用性"""
        self.print_header("模型可用性检查")
        
        try:
            from sentence_transformers import SentenceTransformer
            
            model_name = "intfloat/e5-large-v2"
            print(f"⏳ 检查模型: {model_name}")
            
            # 尝试加载模型
            model = SentenceTransformer(model_name)
            print(f"✅ 模型加载成功")
            
            # 测试编码
            test_text = "这是一个测试句子"
            embedding = model.encode([test_text])
            print(f"✅ 模型编码测试成功 (维度: {embedding.shape[1]})")
            
            return True
            
        except Exception as e:
            print(f"❌ 模型检查失败: {e}")
            print("💡 首次运行时会自动下载模型")
            return False
    
    def run_functionality_test(self):
        """运行功能测试"""
        self.print_header("功能测试")
        
        try:
            # 测试文档管理器
            from enhanced_document_manager import EnhancedDocumentManager
            manager = EnhancedDocumentManager(cache_dir="test_health_check")
            print("✅ 文档管理器初始化成功")
            
            # 测试LLM接口
            from enhanced_llm_interface import EnhancedLLMInterface, LLMConfig
            api_key = os.getenv('MODELSCOPE_SDK_TOKEN')
            if api_key:
                config = LLMConfig(model_name="Qwen/Qwen2.5-72B-Instruct")
                llm = EnhancedLLMInterface(api_key=api_key, config=config)
                print("✅ LLM接口初始化成功")
            else:
                print("⚠️ 跳过LLM接口测试 (无API密钥)")
            
            # 测试用户界面
            from enhanced_user_interface import EnhancedUserInterface
            ui = EnhancedUserInterface()
            print("✅ 用户界面初始化成功")
            
            # 清理测试文件
            import shutil
            test_dir = Path("test_health_check")
            if test_dir.exists():
                shutil.rmtree(test_dir)
            
            return True
            
        except Exception as e:
            print(f"❌ 功能测试失败: {e}")
            return False
    
    def generate_report(self, results):
        """生成检查报告"""
        self.print_header("健康检查报告")
        
        total_checks = len(results)
        passed_checks = sum(results.values())
        
        print(f"📊 检查统计:")
        print(f"  总检查项: {total_checks}")
        print(f"  通过检查: {passed_checks}")
        print(f"  失败检查: {total_checks - passed_checks}")
        print(f"  通过率: {passed_checks/total_checks*100:.1f}%")
        
        print(f"\n📋 详细结果:")
        for check_name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  {check_name}: {status}")
        
        if passed_checks == total_checks:
            print(f"\n🎉 系统健康状况良好！所有检查都通过了。")
            print(f"💡 您可以开始使用增强RAG系统了。")
        elif passed_checks >= total_checks * 0.8:
            print(f"\n✅ 系统基本健康，大部分功能可用。")
            print(f"💡 建议修复失败的检查项以获得最佳体验。")
        else:
            print(f"\n⚠️ 系统存在多个问题，建议修复后再使用。")
            print(f"💡 请参考上述检查结果进行修复。")
    
    def run_all_checks(self):
        """运行所有检查"""
        print("🚀 开始系统健康检查...")
        
        checks = [
            ("系统信息", self.check_system_info),
            ("Conda环境", self.check_conda_environment),
            ("必需包", self.check_required_packages),
            ("可选包", self.check_optional_packages),
            ("系统文件", self.check_system_files),
            ("环境变量", self.check_environment_variables),
            ("模型可用性", self.check_model_availability),
            ("功能测试", self.run_functionality_test)
        ]
        
        results = {}
        
        try:
            for check_name, check_func in checks:
                try:
                    result = check_func()
                    results[check_name] = result
                except Exception as e:
                    print(f"❌ {check_name}检查出错: {e}")
                    results[check_name] = False
            
            # 生成报告
            self.generate_report(results)
            
        except KeyboardInterrupt:
            print("\n⚠️ 检查被用户中断")
        except Exception as e:
            print(f"\n❌ 检查过程中出现严重错误: {e}")

def main():
    """主函数"""
    checker = SystemHealthChecker()
    checker.run_all_checks()

if __name__ == "__main__":
    main()
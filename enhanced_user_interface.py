"""
增强的用户界面模块 - 改进交互体验和错误处理
"""

import os
import sys
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    RICH_AVAILABLE = True
except ImportError:
    print("⚠ rich库未安装，使用基础界面")
    RICH_AVAILABLE = False

try:
    import colorama
    from colorama import Fore, Back, Style
    colorama.init()
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

class EnhancedUserInterface:
    """增强的用户界面"""
    
    def __init__(self, use_rich: bool = True):
        self.use_rich = use_rich and RICH_AVAILABLE
        self.use_colorama = COLORAMA_AVAILABLE
        
        if self.use_rich:
            self.console = Console()
            print("✓ 使用Rich增强界面")
        elif self.use_colorama:
            print("✓ 使用Colorama彩色界面")
        else:
            print("✓ 使用基础文本界面")
    
    def print_welcome(self):
        """打印欢迎信息"""
        if self.use_rich:
            self._print_rich_welcome()
        else:
            self._print_basic_welcome()
    
    def _print_rich_welcome(self):
        """Rich版本的欢迎信息"""
        welcome_text = """
🤖 交互式多模态RAG系统 v2.0

✨ 新功能特性:
• 🔧 增强的CAMEL框架集成和稳定性改进
• 🖼️ 改进的多模态支持 (图像OCR + 表格提取)
• 🌐 真实网页研究和内容分析
• ⚡ 性能监控和优化
• 🎨 增强的用户界面体验

🚀 支持的检索模式:
• 快速检索: 基础向量检索
• 深度检索: 查询重写 + HyDE + RRF融合
• 主题检索: PDF + 网页内容综合分析
        """
        
        panel = Panel(
            welcome_text,
            title="🎯 系统启动",
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(panel)
    
    def _print_basic_welcome(self):
        """基础版本的欢迎信息"""
        if self.use_colorama:
            print(f"{Fore.CYAN}{'='*60}")
            print(f"{Fore.YELLOW}🤖 交互式多模态RAG系统 v2.0")
            print(f"{Fore.CYAN}{'='*60}")
            print(f"{Fore.GREEN}✨ 新功能特性:")
            print(f"{Fore.WHITE}• 增强的CAMEL框架集成和稳定性改进")
            print(f"• 改进的多模态支持 (图像OCR + 表格提取)")
            print(f"• 真实网页研究和内容分析")
            print(f"• 性能监控和优化")
            print(f"• 增强的用户界面体验")
            print(f"{Style.RESET_ALL}")
        else:
            print("="*60)
            print("🤖 交互式多模态RAG系统 v2.0")
            print("="*60)
            print("✨ 新功能特性:")
            print("• 增强的CAMEL框架集成和稳定性改进")
            print("• 改进的多模态支持 (图像OCR + 表格提取)")
            print("• 真实网页研究和内容分析")
            print("• 性能监控和优化")
            print("• 增强的用户界面体验")
    
    def get_pdf_source(self) -> Tuple[str, str]:
        """获取PDF来源"""
        if self.use_rich:
            return self._get_pdf_source_rich()
        else:
            return self._get_pdf_source_basic()
    
    def _get_pdf_source_rich(self) -> Tuple[str, str]:
        """Rich版本的PDF来源选择"""
        self.console.print("\n📚 PDF知识库设置", style="bold blue")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("选项", style="cyan", width=8)
        table.add_column("描述", style="white")
        table.add_row("1", "在线PDF (输入URL)")
        table.add_row("2", "本地PDF (输入文件路径)")
        table.add_row("3", "使用默认示例PDF (CAMEL论文)")
        
        self.console.print(table)
        
        choice = Prompt.ask("\n请选择PDF来源", choices=["1", "2", "3"], default="3")
        
        if choice == "1":
            url = Prompt.ask("请输入PDF的URL")
            return "url", url
        elif choice == "2":
            path = Prompt.ask("请输入PDF文件路径")
            return "path", path
        else:
            return "default", "https://arxiv.org/pdf/2303.17760.pdf"
    
    def _get_pdf_source_basic(self) -> Tuple[str, str]:
        """基础版本的PDF来源选择"""
        print("\n📚 PDF知识库设置")
        print("="*50)
        print("1. 在线PDF (输入URL)")
        print("2. 本地PDF (输入文件路径)")
        print("3. 使用默认示例PDF (CAMEL论文)")
        
        choice = input("\n请选择PDF来源 (1-3, 默认3): ").strip() or "3"
        
        if choice == "1":
            url = input("请输入PDF的URL: ").strip()
            return "url", url
        elif choice == "2":
            path = input("请输入PDF文件路径: ").strip()
            return "path", path
        else:
            return "default", "https://arxiv.org/pdf/2303.17760.pdf"
    
    def get_user_query(self) -> str:
        """获取用户查询"""
        if self.use_rich:
            return Prompt.ask("\n💭 请输入您的问题", default="")
        else:
            return input("\n💭 请输入您的问题: ").strip()
    
    def get_retrieval_mode(self) -> str:
        """获取检索模式"""
        if self.use_rich:
            return self._get_retrieval_mode_rich()
        else:
            return self._get_retrieval_mode_basic()
    
    def _get_retrieval_mode_rich(self) -> str:
        """Rich版本的检索模式选择"""
        self.console.print("\n🔍 选择检索模式", style="bold green")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("模式", style="cyan", width=12)
        table.add_column("描述", style="white")
        table.add_column("特点", style="yellow")
        
        table.add_row(
            "1. 快速检索", 
            "基础向量检索", 
            "速度快，适合简单查询"
        )
        table.add_row(
            "2. 深度检索", 
            "查询重写+HyDE+RRF", 
            "准确度高，适合复杂查询"
        )
        table.add_row(
            "3. 主题检索", 
            "PDF+网页综合分析", 
            "信息全面，适合研究性查询"
        )
        
        self.console.print(table)
        
        choice = Prompt.ask("请选择检索模式", choices=["1", "2", "3"], default="1")
        
        mode_map = {"1": "快速检索", "2": "深度检索", "3": "主题检索"}
        return mode_map[choice]
    
    def _get_retrieval_mode_basic(self) -> str:
        """基础版本的检索模式选择"""
        print("\n🔍 选择检索模式:")
        print("1. 快速检索 (基础向量检索)")
        print("2. 深度检索 (查询重写+HyDE+RRF)")
        print("3. 主题检索 (PDF+网页综合分析)")
        
        choice = input("请选择模式 (1-3, 默认1): ").strip() or "1"
        
        mode_map = {"1": "快速检索", "2": "深度检索", "3": "主题检索"}
        return mode_map.get(choice, "快速检索")
    
    def display_loading(self, message: str):
        """显示加载信息"""
        if self.use_rich:
            self.console.print(f"⏳ {message}", style="yellow")
        else:
            print(f"⏳ {message}")
    
    def display_success(self, message: str):
        """显示成功信息"""
        if self.use_rich:
            self.console.print(f"✅ {message}", style="green")
        else:
            if self.use_colorama:
                print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")
            else:
                print(f"✅ {message}")
    
    def display_warning(self, message: str):
        """显示警告信息"""
        if self.use_rich:
            self.console.print(f"⚠️ {message}", style="yellow")
        else:
            if self.use_colorama:
                print(f"{Fore.YELLOW}⚠️ {message}{Style.RESET_ALL}")
            else:
                print(f"⚠️ {message}")
    
    def display_error(self, message: str):
        """显示错误信息"""
        if self.use_rich:
            self.console.print(f"❌ {message}", style="red")
        else:
            if self.use_colorama:
                print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")
            else:
                print(f"❌ {message}")
    
    def display_results(self, results: Dict[str, Any]):
        """显示查询结果"""
        if 'error' in results:
            self.display_error(f"查询失败: {results['error']}")
            return
        
        if self.use_rich:
            self._display_results_rich(results)
        else:
            self._display_results_basic(results)
    
    def _display_results_rich(self, results: Dict[str, Any]):
        """Rich版本的结果显示"""
        # 创建结果面板
        self.console.print("\n" + "="*80)
        
        # 查询信息
        query_info = f"🔍 查询: {results.get('original_query', 'N/A')}\n"
        query_info += f"🔧 方法: {results.get('retrieval_method', 'N/A')}"
        
        if results.get('rewritten_query'):
            query_info += f"\n📝 重写: {results['rewritten_query']}"
        
        query_panel = Panel(query_info, title="查询信息", border_style="blue")
        self.console.print(query_panel)
        
        # 检索文档
        retrieved_docs = results.get('retrieved_docs', [])
        if retrieved_docs:
            self.console.print(f"\n📄 检索到的文档 (共{len(retrieved_docs)}个):")
            
            for i, doc in enumerate(retrieved_docs, 1):
                score = doc.get('rrf_score', doc.get('similarity', 0))
                text_preview = doc.get('text', '')[:200] + "..." if len(doc.get('text', '')) > 200 else doc.get('text', '')
                
                doc_info = f"相关度分数: {score:.4f}\n内容预览: {text_preview}"
                doc_panel = Panel(doc_info, title=f"文档 {i}", border_style="cyan")
                self.console.print(doc_panel)
        
        # 最终答案
        final_answer = results.get('final_answer', 'N/A')
        answer_panel = Panel(final_answer, title="💡 生成答案", border_style="green")
        self.console.print(answer_panel)
        
        self.console.print("="*80)
    
    def _display_results_basic(self, results: Dict[str, Any]):
        """基础版本的结果显示"""
        print("\n" + "="*80)
        print("📊 查询结果")
        print("="*80)
        
        print(f"🔍 原始查询: {results.get('original_query', 'N/A')}")
        if results.get('rewritten_query'):
            print(f"📝 重写查询: {results['rewritten_query']}")
        print(f"🔧 检索方法: {results.get('retrieval_method', 'N/A')}")
        
        # 显示检索文档
        retrieved_docs = results.get('retrieved_docs', [])
        if retrieved_docs:
            print(f"\n📄 检索到的文档 (共{len(retrieved_docs)}个):")
            print("-" * 60)
            
            for i, doc in enumerate(retrieved_docs, 1):
                score = doc.get('rrf_score', doc.get('similarity', 0))
                text_preview = doc.get('text', '')[:200] + "..." if len(doc.get('text', '')) > 200 else doc.get('text', '')
                
                if self.use_colorama:
                    print(f"{Fore.CYAN}文档 {i}:{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}相关度分数: {score:.4f}{Style.RESET_ALL}")
                    print(f"内容预览: {text_preview}")
                else:
                    print(f"文档 {i}:")
                    print(f"相关度分数: {score:.4f}")
                    print(f"内容预览: {text_preview}")
                print("-" * 60)
        
        # 显示最终答案
        final_answer = results.get('final_answer', 'N/A')
        if self.use_colorama:
            print(f"\n{Fore.GREEN}💡 生成答案:{Style.RESET_ALL}")
        else:
            print(f"\n💡 生成答案:")
        print(final_answer)
        print("="*80)
    
    def ask_save_results(self) -> bool:
        """询问是否保存结果"""
        if self.use_rich:
            return Confirm.ask("💾 是否保存结果到文件?", default=False)
        else:
            choice = input("💾 是否保存结果到文件? (y/n, 默认n): ").strip().lower()
            return choice == 'y'
    
    def ask_continue(self) -> bool:
        """询问是否继续"""
        if self.use_rich:
            return Confirm.ask("🔄 是否继续查询?", default=True)
        else:
            choice = input("🔄 是否继续查询? (y/n, 默认y): ").strip().lower()
            return choice != 'n'
    
    def display_system_status(self, status_info: Dict[str, Any]):
        """显示系统状态"""
        if self.use_rich:
            self._display_system_status_rich(status_info)
        else:
            self._display_system_status_basic(status_info)
    
    def _display_system_status_rich(self, status_info: Dict[str, Any]):
        """Rich版本的系统状态显示"""
        table = Table(title="🔧 系统状态", show_header=True, header_style="bold magenta")
        table.add_column("组件", style="cyan", width=20)
        table.add_column("状态", style="white", width=15)
        table.add_column("详情", style="yellow")
        
        for component, info in status_info.items():
            if isinstance(info, dict):
                status = "✅ 正常" if info.get('available', True) else "❌ 不可用"
                details = info.get('details', '')
            else:
                status = "✅ 正常" if info else "❌ 不可用"
                details = ""
            
            table.add_row(component, status, details)
        
        self.console.print(table)
    
    def _display_system_status_basic(self, status_info: Dict[str, Any]):
        """基础版本的系统状态显示"""
        print("\n🔧 系统状态:")
        print("-" * 50)
        
        for component, info in status_info.items():
            if isinstance(info, dict):
                status = "✅ 正常" if info.get('available', True) else "❌ 不可用"
                details = info.get('details', '')
            else:
                status = "✅ 正常" if info else "❌ 不可用"
                details = ""
            
            if self.use_colorama:
                print(f"{Fore.CYAN}{component}:{Style.RESET_ALL} {status}")
                if details:
                    print(f"  {details}")
            else:
                print(f"{component}: {status}")
                if details:
                    print(f"  {details}")
    
    def display_performance_summary(self, performance_data: Dict[str, Any]):
        """显示性能摘要"""
        if self.use_rich:
            self._display_performance_summary_rich(performance_data)
        else:
            self._display_performance_summary_basic(performance_data)
    
    def _display_performance_summary_rich(self, performance_data: Dict[str, Any]):
        """Rich版本的性能摘要显示"""
        if "message" in performance_data:
            self.console.print(f"📊 {performance_data['message']}", style="yellow")
            return
        
        # 总体统计
        summary_text = f"""
总操作数: {performance_data['total_operations']}
整体成功率: {performance_data['overall_success_rate']:.1%}
总耗时: {performance_data['total_duration']:.2f}秒
平均耗时: {performance_data['avg_duration']:.2f}秒
平均内存使用: {performance_data['avg_memory_usage']:.1f}MB
        """
        
        summary_panel = Panel(summary_text.strip(), title="📊 性能摘要", border_style="green")
        self.console.print(summary_panel)
        
        # 操作详情表格
        if performance_data.get('operations_breakdown'):
            table = Table(title="操作详情", show_header=True, header_style="bold magenta")
            table.add_column("操作", style="cyan")
            table.add_column("次数", style="white")
            table.add_column("成功率", style="green")
            table.add_column("平均耗时", style="yellow")
            table.add_column("平均内存", style="blue")
            
            for op_name, op_data in performance_data['operations_breakdown'].items():
                table.add_row(
                    op_name,
                    str(op_data['count']),
                    f"{op_data['success_rate']:.1%}",
                    f"{op_data['avg_duration']:.2f}s",
                    f"{op_data['avg_memory']:.1f}MB"
                )
            
            self.console.print(table)
    
    def _display_performance_summary_basic(self, performance_data: Dict[str, Any]):
        """基础版本的性能摘要显示"""
        if "message" in performance_data:
            print(f"📊 {performance_data['message']}")
            return
        
        print("\n📊 性能摘要:")
        print("-" * 50)
        print(f"总操作数: {performance_data['total_operations']}")
        print(f"整体成功率: {performance_data['overall_success_rate']:.1%}")
        print(f"总耗时: {performance_data['total_duration']:.2f}秒")
        print(f"平均耗时: {performance_data['avg_duration']:.2f}秒")
        print(f"平均内存使用: {performance_data['avg_memory_usage']:.1f}MB")
        
        if performance_data.get('operations_breakdown'):
            print(f"\n操作详情:")
            print("-" * 50)
            for op_name, op_data in performance_data['operations_breakdown'].items():
                print(f"{op_name}:")
                print(f"  调用次数: {op_data['count']}")
                print(f"  成功率: {op_data['success_rate']:.1%}")
                print(f"  平均耗时: {op_data['avg_duration']:.2f}秒")
                print(f"  平均内存: {op_data['avg_memory']:.1f}MB")
    
    def save_results_to_file(self, results: Dict[str, Any], filename: str = None) -> bool:
        """保存结果到文件"""
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"rag_query_result_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("RAG查询结果报告\n")
                f.write("="*80 + "\n\n")
                f.write(f"查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"原始查询: {results.get('original_query', 'N/A')}\n")
                
                if results.get('rewritten_query'):
                    f.write(f"重写查询: {results['rewritten_query']}\n")
                
                f.write(f"检索方法: {results.get('retrieval_method', 'N/A')}\n\n")
                
                # 保存检索文档
                retrieved_docs = results.get('retrieved_docs', [])
                if retrieved_docs:
                    f.write(f"检索到的文档 (共{len(retrieved_docs)}个):\n")
                    f.write("-" * 60 + "\n")
                    
                    for i, doc in enumerate(retrieved_docs, 1):
                        score = doc.get('rrf_score', doc.get('similarity', 0))
                        f.write(f"\n文档 {i}:\n")
                        f.write(f"相关度分数: {score:.4f}\n")
                        f.write(f"内容: {doc.get('text', '')}\n")
                        f.write("-" * 60 + "\n")
                
                # 保存最终答案
                f.write(f"\n生成答案:\n")
                f.write(results.get('final_answer', 'N/A'))
                f.write("\n\n" + "="*80)
            
            self.display_success(f"结果已保存到: {filename}")
            return True
            
        except Exception as e:
            self.display_error(f"保存失败: {e}")
            return False
    
    def get_input_with_validation(self, prompt: str, validator=None, error_msg: str = "输入无效，请重试") -> str:
        """获取带验证的用户输入"""
        while True:
            try:
                if self.use_rich:
                    user_input = Prompt.ask(prompt)
                else:
                    user_input = input(f"{prompt}: ").strip()
                
                if validator is None or validator(user_input):
                    return user_input
                else:
                    self.display_warning(error_msg)
                    
            except KeyboardInterrupt:
                self.display_warning("用户中断输入")
                return ""
            except Exception as e:
                self.display_error(f"输入错误: {e}")
                continue
    
    def get_document_sources(self) -> Tuple[List[str], str]:
        """获取文档来源 - 支持多文档"""
        if self.use_rich:
            return self._get_document_sources_rich()
        else:
            return self._get_document_sources_basic()
    
    def _get_document_sources_rich(self) -> Tuple[List[str], str]:
        """Rich版本的文档来源选择"""
        self.console.print("\n📚 文档知识库设置", style="bold blue")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("选项", style="cyan", width=8)
        table.add_column("描述", style="white")
        table.add_row("1", "在线文档 (输入URL)")
        table.add_row("2", "本地文档 (输入文件路径)")
        table.add_row("3", "批量本地文档 (输入目录路径)")
        table.add_row("4", "使用默认示例PDF")
        
        self.console.print(table)
        
        choice = Prompt.ask("\n请选择文档来源", choices=["1", "2", "3", "4"], default="4")
        
        if choice == "1":
            urls = []
            while True:
                url = Prompt.ask("请输入文档URL (回车结束)")
                if not url:
                    break
                urls.append(url)
            return urls if urls else ["https://arxiv.org/pdf/2303.17760.pdf"], "url"
        
        elif choice == "2":
            paths = []
            while True:
                path = Prompt.ask("请输入文档文件路径 (回车结束)")
                if not path:
                    break
                if os.path.exists(path):
                    paths.append(path)
                else:
                    self.display_warning(f"文件不存在: {path}")
            return paths, "path"
        
        elif choice == "3":
            dir_path = Prompt.ask("请输入目录路径")
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                # 支持的文档格式
                supported_exts = ['.pdf', '.docx', '.doc', '.txt', '.md', '.csv', '.xlsx', '.xls', '.pptx', '.json']
                files = []
                for ext in supported_exts:
                    files.extend([str(p) for p in Path(dir_path).glob(f"*{ext}")])
                return files, "path"
            else:
                self.display_error("目录不存在")
                return [], "path"
        
        else:
            return ["https://arxiv.org/pdf/2303.17760.pdf"], "url"
    
    def _get_document_sources_basic(self) -> Tuple[List[str], str]:
        """基础版本的文档来源选择"""
        print("\n📚 文档知识库设置")
        print("="*50)
        print("1. 在线文档 (输入URL)")
        print("2. 本地文档 (输入文件路径)")
        print("3. 批量本地文档 (输入目录路径)")
        print("4. 使用默认示例PDF")
        
        choice = input("\n请选择文档来源 (1-4, 默认4): ").strip() or "4"
        
        if choice == "1":
            urls = []
            print("请输入文档URL (输入空行结束):")
            while True:
                url = input("URL: ").strip()
                if not url:
                    break
                urls.append(url)
            return urls if urls else ["https://arxiv.org/pdf/2303.17760.pdf"], "url"
        
        elif choice == "2":
            paths = []
            print("请输入文档文件路径 (输入空行结束):")
            while True:
                path = input("路径: ").strip()
                if not path:
                    break
                if os.path.exists(path):
                    paths.append(path)
                else:
                    print(f"⚠️ 文件不存在: {path}")
            return paths, "path"
        
        elif choice == "3":
            dir_path = input("请输入目录路径: ").strip()
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                from pathlib import Path
                supported_exts = ['.pdf', '.docx', '.doc', '.txt', '.md', '.csv', '.xlsx', '.xls', '.pptx', '.json']
                files = []
                for ext in supported_exts:
                    files.extend([str(p) for p in Path(dir_path).glob(f"*{ext}")])
                return files, "path"
            else:
                print("❌ 目录不存在")
                return [], "path"
        
        else:
            return ["https://arxiv.org/pdf/2303.17760.pdf"], "url"
    
    def get_document_management_action(self) -> str:
        """获取文档管理操作"""
        if self.use_rich:
            return self._get_document_management_action_rich()
        else:
            return self._get_document_management_action_basic()
    
    def _get_document_management_action_rich(self) -> str:
        """Rich版本的文档管理操作选择"""
        self.console.print("\n📁 文档管理", style="bold blue")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("操作", style="cyan", width=12)
        table.add_column("描述", style="white")
        
        table.add_row("1. add", "添加新文档到知识库")
        table.add_row("2. remove", "从知识库中移除文档")
        table.add_row("3. list", "列出知识库中的所有文档")
        table.add_row("4. cache", "缓存管理")
        table.add_row("5. back", "返回主菜单")
        
        self.console.print(table)
        
        choice = Prompt.ask("请选择操作", choices=["1", "2", "3", "4", "5"], default="5")
        
        action_map = {"1": "add", "2": "remove", "3": "list", "4": "cache", "5": "back"}
        return action_map[choice]
    
    def _get_document_management_action_basic(self) -> str:
        """基础版本的文档管理操作选择"""
        print("\n📁 文档管理")
        print("="*50)
        print("1. 添加新文档到知识库")
        print("2. 从知识库中移除文档")
        print("3. 列出知识库中的所有文档")
        print("4. 缓存管理")
        print("5. 返回主菜单")
        
        choice = input("请选择操作 (1-5, 默认5): ").strip() or "5"
        
        action_map = {"1": "add", "2": "remove", "3": "list", "4": "cache", "5": "back"}
        return action_map.get(choice, "back")
    
    def select_documents_to_remove(self, current_sources: List[str]) -> List[str]:
        """选择要移除的文档"""
        if self.use_rich:
            return self._select_documents_to_remove_rich(current_sources)
        else:
            return self._select_documents_to_remove_basic(current_sources)
    
    def _select_documents_to_remove_rich(self, current_sources: List[str]) -> List[str]:
        """Rich版本的文档移除选择"""
        self.console.print("\n🗑️ 选择要移除的文档", style="bold red")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("序号", style="cyan", width=6)
        table.add_column("文档路径", style="white")
        
        for i, source in enumerate(current_sources, 1):
            table.add_row(str(i), source)
        
        self.console.print(table)
        
        indices_str = Prompt.ask("请输入要移除的文档序号 (用逗号分隔, 如: 1,3,5)")
        
        try:
            indices = [int(x.strip()) - 1 for x in indices_str.split(',') if x.strip()]
            return [current_sources[i] for i in indices if 0 <= i < len(current_sources)]
        except:
            self.display_error("输入格式错误")
            return []
    
    def _select_documents_to_remove_basic(self, current_sources: List[str]) -> List[str]:
        """基础版本的文档移除选择"""
        print("\n🗑️ 选择要移除的文档")
        print("="*50)
        
        for i, source in enumerate(current_sources, 1):
            print(f"{i}. {source}")
        
        indices_str = input("请输入要移除的文档序号 (用逗号分隔, 如: 1,3,5): ").strip()
        
        try:
            indices = [int(x.strip()) - 1 for x in indices_str.split(',') if x.strip()]
            return [current_sources[i] for i in indices if 0 <= i < len(current_sources)]
        except:
            print("❌ 输入格式错误")
            return []
    
    def display_document_list(self, sources: List[str]):
        """显示文档列表"""
        if self.use_rich:
            self._display_document_list_rich(sources)
        else:
            self._display_document_list_basic(sources)
    
    def _display_document_list_rich(self, sources: List[str]):
        """Rich版本的文档列表显示"""
        table = Table(title="📚 知识库文档列表", show_header=True, header_style="bold magenta")
        table.add_column("序号", style="cyan", width=6)
        table.add_column("文档路径", style="white")
        table.add_column("类型", style="yellow", width=8)
        
        for i, source in enumerate(sources, 1):
            doc_type = "URL" if source.startswith(('http://', 'https://')) else "本地"
            table.add_row(str(i), source, doc_type)
        
        self.console.print(table)
    
    def _display_document_list_basic(self, sources: List[str]):
        """基础版本的文档列表显示"""
        print("\n📚 知识库文档列表")
        print("="*50)
        
        for i, source in enumerate(sources, 1):
            doc_type = "URL" if source.startswith(('http://', 'https://')) else "本地"
            print(f"{i}. [{doc_type}] {source}")
    
    def display_cache_stats(self, cache_stats: Dict[str, Any]):
        """显示缓存统计"""
        if self.use_rich:
            self._display_cache_stats_rich(cache_stats)
        else:
            self._display_cache_stats_basic(cache_stats)
    
    def _display_cache_stats_rich(self, cache_stats: Dict[str, Any]):
        """Rich版本的缓存统计显示"""
        stats_text = f"""
缓存文档数: {cache_stats['cached_documents']}
缓存文件数: {cache_stats['cache_files']}
总缓存大小: {cache_stats['total_size_mb']:.1f}MB
最大缓存大小: {cache_stats['max_size_mb']}MB
缓存使用率: {cache_stats['cache_usage_percent']:.1f}%
        """
        
        panel = Panel(stats_text.strip(), title="💾 缓存统计", border_style="blue")
        self.console.print(panel)
    
    def _display_cache_stats_basic(self, cache_stats: Dict[str, Any]):
        """基础版本的缓存统计显示"""
        print("\n💾 缓存统计")
        print("="*50)
        print(f"缓存文档数: {cache_stats['cached_documents']}")
        print(f"缓存文件数: {cache_stats['cache_files']}")
        print(f"总缓存大小: {cache_stats['total_size_mb']:.1f}MB")
        print(f"最大缓存大小: {cache_stats['max_size_mb']}MB")
        print(f"缓存使用率: {cache_stats['cache_usage_percent']:.1f}%")
    
    def ask_clear_cache(self) -> bool:
        """询问是否清理缓存"""
        if self.use_rich:
            return Confirm.ask("🗑️ 是否清理所有缓存?", default=False)
        else:
            choice = input("🗑️ 是否清理所有缓存? (y/n, 默认n): ").strip().lower()
            return choice == 'y'

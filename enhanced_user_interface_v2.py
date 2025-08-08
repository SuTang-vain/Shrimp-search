"""
增强的用户界面 V2 - 支持模型选择和管理
"""

import os
import json
from typing import Dict, Any, List, Tuple, Optional
from enhanced_user_interface import EnhancedUserInterface

class EnhancedUserInterfaceV2(EnhancedUserInterface):
    """增强的用户界面V2 - 添加模型管理功能"""
    
    def __init__(self):
        super().__init__()
    
    def get_model_selection(self, available_models: Dict[str, Dict[str, Any]]) -> Optional[str]:
        """获取用户的模型选择"""
        print("\n🤖 可用模型选择:")
        print("="*60)
        
        model_options = []
        index = 1
        
        # 显示远程模型
        if 'remote' in available_models and available_models['remote']:
            print(f"\n📡 远程模型 (ModelScope):")
            for key, info in available_models['remote'].items():
                status = "✅ 可用" if info['available'] else "❌ 需要API密钥"
                print(f"  {index}. {key}")
                print(f"     描述: {info['description']}")
                print(f"     状态: {status}")
                model_options.append(key)
                index += 1
        
        # 显示本地模型
        if 'local' in available_models and available_models['local']:
            print(f"\n💻 本地模型 (Ollama):")
            for key, info in available_models['local'].items():
                if info['available']:
                    if info['installed']:
                        status = "✅ 已安装"
                    else:
                        status = "⬇️ 可安装"
                else:
                    status = "❌ Ollama服务不可用"
                
                print(f"  {index}. {key}")
                print(f"     描述: {info['description']}")
                print(f"     状态: {status}")
                model_options.append(key)
                index += 1
        
        if not model_options:
            print("❌ 没有可用的模型")
            return None
        
        print(f"\n0. 自动选择最佳模型")
        print("q. 返回上级菜单")
        
        while True:
            try:
                choice = input(f"\n请选择模型 (0-{len(model_options)}, q): ").strip().lower()
                
                if choice == 'q':
                    return None
                elif choice == '0':
                    return 'auto'
                else:
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(model_options):
                        selected_model = model_options[choice_idx]
                        print(f"已选择模型: {selected_model}")
                        return selected_model
                    else:
                        print("❌ 无效选择，请重新输入")
            except ValueError:
                print("❌ 请输入数字或 'q'")
    
    def display_model_status(self, status_info: Dict[str, Any]):
        """显示模型状态信息"""
        print("\n📊 模型状态信息:")
        print("="*50)
        
        # 当前模型
        current_model = status_info.get('current_model')
        if current_model:
            print(f"当前模型: {current_model['key']} ({current_model['provider']})")
            print(f"模型类型: {current_model['type']}")
            print(f"模型名称: {current_model['name']}")
            print(f"描述: {current_model['description']}")
        else:
            print("当前模型: 未设置")
        
        # API状态
        api_status = "✅ 已配置" if status_info.get('api_key_available') else "❌ 未配置"
        print(f"API密钥: {api_status}")
        
        # Ollama状态
        ollama_status = "✅ 可用" if status_info.get('ollama_available') else "❌ 不可用"
        ollama_models = status_info.get('ollama_models', 0)
        print(f"Ollama服务: {ollama_status} (已安装模型: {ollama_models}个)")
        
        # 生成统计
        gen_stats = status_info.get('generation_stats', {})
        if gen_stats.get('total_requests', 0) > 0:
            print(f"\n📈 生成统计:")
            print(f"  总请求数: {gen_stats['total_requests']}")
            print(f"  成功请求: {gen_stats['successful_requests']}")
            print(f"  失败请求: {gen_stats['failed_requests']}")
            print(f"  成功率: {gen_stats.get('success_rate', 0):.1%}")
            print(f"  平均响应时间: {gen_stats.get('average_time', 0):.2f}秒")
            
            # 模型使用统计
            model_usage = gen_stats.get('model_usage', {})
            if model_usage:
                print(f"  模型使用次数:")
                for model, count in model_usage.items():
                    print(f"    {model}: {count}次")
    
    def get_model_management_action(self) -> str:
        """获取模型管理操作"""
        print("\n🔧 模型管理:")
        print("="*40)
        print("1. 切换模型")
        print("2. 测试当前模型")
        print("3. 查看模型状态")
        print("4. 查看Ollama模型")
        print("5. 安装本地模型")
        print("6. 删除本地模型")
        print("7. 重置统计信息")
        print("8. 返回主菜单")
        
        while True:
            choice = input("\n请选择操作 (1-8): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
                return {
                    '1': 'switch',
                    '2': 'test',
                    '3': 'status',
                    '4': 'list_ollama',
                    '5': 'install',
                    '6': 'delete',
                    '7': 'reset_stats',
                    '8': 'back'
                }[choice]
            else:
                print("❌ 无效选择，请重新输入")
    
    def display_test_result(self, test_result: Dict[str, Any]):
        """显示模型测试结果"""
        print("\n🧪 模型测试结果:")
        print("="*40)
        
        if test_result['success']:
            print("✅ 测试成功")
            print(f"模型: {test_result['model_key']} ({test_result['model_type']})")
            print(f"响应时间: {test_result['generation_time']:.2f}秒")
            print(f"响应内容: {test_result['response']}")
        else:
            print("❌ 测试失败")
            if test_result.get('model_key'):
                print(f"模型: {test_result['model_key']}")
            print(f"错误信息: {test_result['error']}")
    
    def display_ollama_models(self, models: List[Dict[str, Any]]):
        """显示Ollama模型列表"""
        print("\n💻 Ollama已安装模型:")
        print("="*50)
        
        if not models:
            print("没有已安装的模型")
            return
        
        for i, model in enumerate(models, 1):
            size_mb = model.get('size', 0) / (1024 * 1024)
            print(f"{i}. {model['name']}")
            print(f"   大小: {size_mb:.1f}MB")
            if model.get('modified_at'):
                print(f"   修改时间: {model['modified_at']}")
    
    def get_model_name_input(self, prompt: str = "请输入模型名称") -> Optional[str]:
        """获取模型名称输入"""
        model_name = input(f"{prompt}: ").strip()
        if not model_name:
            print("❌ 模型名称不能为空")
            return None
        return model_name
    
    def confirm_action(self, action: str, target: str = "") -> bool:
        """确认操作"""
        message = f"确认{action}"
        if target:
            message += f" {target}"
        message += "? (y/N): "
        
        response = input(message).strip().lower()
        return response in ['y', 'yes', '是', 'Y']
    
    def display_operation_progress(self, operation: str, status: str):
        """显示操作进度"""
        print(f"⏳ {operation}: {status}")
    
    def display_operation_result(self, operation: str, success: bool, message: str = ""):
        """显示操作结果"""
        if success:
            print(f"✅ {operation}成功")
        else:
            print(f"❌ {operation}失败")
        
        if message:
            print(f"   {message}")
    
    def get_retrieval_mode_v2(self) -> str:
        """获取检索模式 - V2版本支持更多选项"""
        print("\n🔍 选择检索模式:")
        print("="*40)
        print("1. 快速检索 - 基础向量检索")
        print("2. 深度检索 - 查询重写+HyDE+RRF融合")
        print("3. 主题检索 - PDF+网页综合分析")
        print("4. 智能检索 - 自适应选择最佳策略")
        
        mode_map = {
            '1': '快速检索',
            '2': '深度检索', 
            '3': '主题检索',
            '4': '智能检索'
        }
        
        while True:
            choice = input("\n请选择检索模式 (1-4): ").strip()
            if choice in mode_map:
                selected_mode = mode_map[choice]
                print(f"已选择: {selected_mode}")
                return selected_mode
            else:
                print("❌ 无效选择，请重新输入")
    
    def display_model_comparison(self, comparison_data: Dict[str, Any]):
        """显示模型性能对比"""
        print("\n📊 模型性能对比:")
        print("="*60)
        
        for model_key, data in comparison_data.items():
            print(f"\n{model_key}:")
            print(f"  平均响应时间: {data.get('avg_time', 0):.2f}秒")
            print(f"  成功率: {data.get('success_rate', 0):.1%}")
            print(f"  使用次数: {data.get('usage_count', 0)}")
            print(f"  模型类型: {data.get('model_type', 'unknown')}")
    
    def get_generation_settings(self) -> Dict[str, Any]:
        """获取生成设置"""
        print("\n⚙️ 生成设置")
        print("是否自定义生成参数? (y/n): ", end="")
        
        choice = input().strip().lower()
        if choice != 'y':
            return {}
        
        settings = {}
        
        # 温度设置
        print("设置生成温度 (0.0-1.0, 默认0.7): ", end="")
        temp_input = input().strip()
        if temp_input:
            try:
                temp_value = float(temp_input)
                if 0.0 <= temp_value <= 1.0:
                    settings['temperature'] = temp_value
                else:
                    print("温度值应在0.0-1.0之间，使用默认值")
            except ValueError:
                print("无效温度值，使用默认值")
        
        # 最大token设置
        print("设置最大token数 (100-2000, 默认800): ", end="")
        token_input = input().strip()
        if token_input:
            try:
                token_value = int(token_input)
                if 100 <= token_value <= 2000:
                    settings['max_tokens'] = token_value
                else:
                    print("token数应在100-2000之间，使用默认值")
            except ValueError:
                print("无效token数，使用默认值")
        
        return settings

    def display_query_result_v2(self, result: Dict[str, Any]):
        """显示查询结果V2"""
        if 'error' in result:
            print(f"\n❌ 查询失败: {result['error']}")
            return
        
        print(f"\n📋 查询结果")
        print("="*60)
        
        # 显示基本信息
        print(f"原始问题: {result.get('original_query', 'N/A')}")
        print(f"检索方法: {result.get('retrieval_method', 'N/A')}")
        
        # 显示模型信息
        model_info = result.get('model_info', {})
        if model_info:
            print(f"使用模型: {model_info.get('key', 'N/A')} ({model_info.get('type', 'N/A')})")
            print(f"生成时间: {model_info.get('generation_time', 0):.2f}秒")
        
        # 显示检索到的文档数量
        retrieved_docs = result.get('retrieved_docs', [])
        if retrieved_docs:
            print(f"检索文档: {len(retrieved_docs)} 个")
        
        # 显示最终答案
        final_answer = result.get('final_answer', '')
        if final_answer:
            print(f"\n💡 答案:")
            print("-"*40)
            print(final_answer)
            print("-"*40)
        
        # 显示额外信息
        if 'rewritten_query' in result:
            print(f"\n🔄 重写查询: {result['rewritten_query']}")
        
        if 'web_research' in result:
            web_result = result['web_research']
            if web_result.get('success'):
                print(f"\n🌐 网页研究: 成功检索 {len(web_result.get('results', []))} 个网页")

    def get_advanced_settings(self) -> Dict[str, Any]:
        """获取高级设置"""
        print("\n⚙️ 高级设置:")
        print("="*30)
        
        settings = {}
        
        # 最大令牌数
        try:
            max_tokens = input("最大令牌数 (默认1000): ").strip()
            settings['max_tokens'] = int(max_tokens) if max_tokens else 1000
        except ValueError:
            settings['max_tokens'] = 1000
        
        # 温度参数
        try:
            temperature = input("温度参数 0.0-1.0 (默认0.7): ").strip()
            temp_val = float(temperature) if temperature else 0.7
            settings['temperature'] = max(0.0, min(1.0, temp_val))
        except ValueError:
            settings['temperature'] = 0.7
        
        # 是否启用流式输出
        stream = input("启用流式输出? (y/N): ").strip().lower()
        settings['stream'] = stream in ['y', 'yes', '是']
        
        return settings
    
    def display_generation_result(self, result: Any):
        """显示生成结果 - 支持新的结果格式"""
        if hasattr(result, 'error') and result.error:
            print(f"❌ 生成失败: {result.error}")
            return
        
        print("\n💡 生成结果:")
        print("="*50)
        
        if hasattr(result, 'content'):
            print(result.content)
            print(f"\n📊 生成信息:")
            print(f"  模型: {getattr(result, 'model_key', 'unknown')}")
            print(f"  类型: {getattr(result, 'model_type', 'unknown')}")
            print(f"  耗时: {getattr(result, 'generation_time', 0):.2f}秒")
        else:
            # 兼容旧格式
            if isinstance(result, dict):
                if 'error' in result:
                    print(f"❌ 错误: {result['error']}")
                elif 'final_answer' in result:
                    print(result['final_answer'])
                    print(f"\n📊 检索信息:")
                    print(f"  检索方法: {result.get('retrieval_method', 'unknown')}")
                    if 'retrieved_docs' in result:
                        print(f"  相关文档: {len(result['retrieved_docs'])}个")
            else:
                print(str(result))
"""
增强的LLM接口 V2 - 支持多端模型选择
集成ModelScope远程API和Ollama本地部署
"""

import os
import time
import requests
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

from model_manager import ModelManager, ModelConfig
from ollama_interface import OllamaInterface

class ContentFilterException(Exception):
    """内容过滤异常"""
    pass

@dataclass
class GenerationResult:
    """生成结果数据类"""
    content: str
    model_key: str
    model_type: str
    generation_time: float
    token_count: Optional[int] = None
    error: Optional[str] = None

class EnhancedLLMInterfaceV2:
    """增强的LLM接口V2 - 统一管理多种模型后端"""
    
    def __init__(self, api_key: Optional[str] = None):
        # 从环境变量获取API密钥
        from dotenv import load_dotenv
        load_dotenv()
        
        self.api_key = api_key or os.getenv('MODELSCOPE_SDK_TOKEN')
        self.glm_api_key = os.getenv('GLM_API_KEY')
        self.model_manager = ModelManager()
        self.ollama_interface = OllamaInterface()
        
        # 当前使用的模型信息
        self.current_backend = None
        
        # 性能统计
        self.generation_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_time': 0.0,
            'model_usage': {},
            'content_filter_errors': 0,
            'auto_fallbacks': 0
        }
        
        # 敏感词替换映射
        self.sensitive_word_replacements = {
            'camel': 'CAMEL框架',
            'CAMEL': 'CAMEL框架',
            'rag': 'RAG技术',
            'RAG': 'RAG技术',
            '系统': '技术架构',
            '实现': '技术实现方案'
        }
        
        print("增强LLM接口V2初始化完成")
        self._print_available_models()
    
    def _print_available_models(self):
        """打印可用模型信息"""
        print("\n可用模型:")
        
        # 远程模型
        remote_models = self.model_manager.list_models_by_type('remote')
        if remote_models:
            print("  远程模型 (ModelScope):")
            for key, config in remote_models.items():
                print(f"    - {key}: {config.description}")
        
        # 本地模型
        local_models = self.model_manager.list_models_by_type('local')
        if local_models:
            print("  本地模型 (Ollama):")
            ollama_status = "可用" if self.ollama_interface.is_available() else "不可用"
            print(f"    Ollama服务状态: {ollama_status}")
            
            if self.ollama_interface.is_available():
                installed_models = self.ollama_interface.get_installed_models()
                for key, config in local_models.items():
                    model_installed = any(m['name'] == config.name for m in installed_models)
                    status = "已安装" if model_installed else "未安装"
                    print(f"    - {key}: {config.description} ({status})")
            else:
                for key, config in local_models.items():
                    print(f"    - {key}: {config.description} (服务不可用)")
    
    def set_model(self, model_key: str) -> bool:
        """设置当前使用的模型"""
        result = self.model_manager.get_model_config(model_key)
        if not result:
            print(f"未找到模型: {model_key}")
            return False
        
        model_type, model_config = result
        
        # 验证模型可用性
        if model_type == 'remote':
            if model_config.provider == 'GLM':
                if not self.glm_api_key:
                    print("使用GLM模型需要GLM_API_KEY")
                    return False
            else:
                if not self.api_key:
                    print("使用ModelScope模型需要MODELSCOPE_SDK_TOKEN")
                    return False
        elif model_type == 'local':
            if not self.ollama_interface.is_available():
                print("Ollama服务不可用")
                return False
            
            # 检查模型是否已安装
            if not self.ollama_interface.check_model_exists(model_config.name):
                print(f"本地模型 {model_config.name} 未安装，尝试自动拉取...")
                if not self.ollama_interface.pull_model(model_config.name):
                    print(f"模型 {model_config.name} 拉取失败")
                    return False
        
        # 设置当前后端
        self.current_backend = {
            'type': model_type,
            'key': model_key,
            'config': model_config
        }
        
        # 更新模型管理器
        self.model_manager.set_current_model(model_key)
        
        print(f"已切换到模型: {model_key} ({model_config.provider})")
        return True
    
    def get_current_model(self) -> Optional[Dict[str, Any]]:
        """获取当前模型信息"""
        if self.current_backend:
            return {
                'key': self.current_backend['key'],
                'type': self.current_backend['type'],
                'name': self.current_backend['config'].name,
                'provider': self.current_backend['config'].provider,
                'description': self.current_backend['config'].description
            }
        return None
    
    def _optimize_query_for_content_filter(self, text: str) -> str:
        """优化查询文本以避免内容过滤"""
        optimized_text = text
        
        # 替换可能的敏感词
        for sensitive_word, replacement in self.sensitive_word_replacements.items():
            optimized_text = optimized_text.replace(sensitive_word, replacement)
        
        # 添加技术性前缀，使查询更加学术化
        if any(word in text.lower() for word in ['camel', 'rag', '系统', '实现']):
            optimized_text = f"请从技术角度分析：{optimized_text}"
        
        return optimized_text

    def _try_fallback_model(self, original_prompt: str, max_tokens: int, temperature: float, **kwargs) -> str:
        """尝试备用模型"""
        print("🔄 尝试切换到备用模型...")
        
        # 保存当前模型
        original_backend = self.current_backend
        
        # 尝试切换到ModelScope模型
        available_models = self.list_available_models()
        fallback_models = []
        
        # 优先选择ModelScope模型作为备用
        for key, info in available_models['remote'].items():
            if info['available'] and info['provider'] != 'GLM' and key != original_backend['key']:
                fallback_models.append(key)
        
        # 然后选择本地模型
        for key, info in available_models['local'].items():
            if info['available'] and info['installed'] and key != original_backend['key']:
                fallback_models.append(key)
        
        for fallback_key in fallback_models:
            try:
                print(f"🔄 尝试切换到模型: {fallback_key}")
                if self.set_model(fallback_key):
                    # 使用优化后的查询
                    optimized_prompt = self._optimize_query_for_content_filter(original_prompt)
                    
                    if self.current_backend['type'] == 'local':
                        result = self._generate_local(optimized_prompt, max_tokens, temperature, **kwargs)
                    else:
                        result = self._generate_remote(optimized_prompt, max_tokens, temperature, **kwargs)
                    
                    self.generation_stats['auto_fallbacks'] += 1
                    print(f"✅ 备用模型 {fallback_key} 生成成功")
                    return result
                    
            except Exception as e:
                print(f"❌ 备用模型 {fallback_key} 也失败: {str(e)}")
                continue
        
        # 恢复原模型
        self.current_backend = original_backend
        raise Exception("所有备用模型都失败了")

    def generate(self, prompt: str, max_tokens: Optional[int] = None, 
                temperature: Optional[float] = None, **kwargs) -> GenerationResult:
        """统一的文本生成接口"""
        if not self.current_backend:
            return GenerationResult(
                content="",
                model_key="",
                model_type="",
                generation_time=0.0,
                error="未设置模型，请先选择模型"
            )
        
        # 使用配置的默认值或传入的参数
        config = self.current_backend['config']
        max_tokens = max_tokens or config.max_tokens
        temperature = temperature or config.temperature
        
        # 记录开始时间
        start_time = time.time()
        
        # 更新统计
        self.generation_stats['total_requests'] += 1
        model_key = self.current_backend['key']
        if model_key not in self.generation_stats['model_usage']:
            self.generation_stats['model_usage'][model_key] = 0
        self.generation_stats['model_usage'][model_key] += 1
        
        try:
            # 根据模型类型选择生成方法
            if self.current_backend['type'] == 'local':
                content = self._generate_local(prompt, max_tokens, temperature, **kwargs)
            else:
                content = self._generate_remote(prompt, max_tokens, temperature, **kwargs)
            
            # 计算生成时间
            generation_time = time.time() - start_time
            self.generation_stats['successful_requests'] += 1
            self.generation_stats['total_time'] += generation_time
            
            return GenerationResult(
                content=content,
                model_key=model_key,
                model_type=self.current_backend['type'],
                generation_time=generation_time
            )
            
        except ContentFilterException as e:
            print(f"⚠️ 内容过滤错误: {str(e)}")
            self.generation_stats['content_filter_errors'] += 1
            
            try:
                # 尝试备用模型
                content = self._try_fallback_model(prompt, max_tokens, temperature, **kwargs)
                generation_time = time.time() - start_time
                self.generation_stats['successful_requests'] += 1
                self.generation_stats['total_time'] += generation_time
                
                return GenerationResult(
                    content=content,
                    model_key=self.current_backend['key'],
                    model_type=self.current_backend['type'],
                    generation_time=generation_time
                )
                
            except Exception as fallback_error:
                generation_time = time.time() - start_time
                self.generation_stats['failed_requests'] += 1
                
                error_msg = f"内容过滤错误，备用模型也失败: {str(fallback_error)}"
                print(f"❌ {error_msg}")
                
                return GenerationResult(
                    content="",
                    model_key=model_key,
                    model_type=self.current_backend['type'],
                    generation_time=generation_time,
                    error=error_msg
                )
            
        except Exception as e:
            generation_time = time.time() - start_time
            self.generation_stats['failed_requests'] += 1
            
            error_msg = f"生成失败: {str(e)}"
            print(f"模型生成错误: {error_msg}")
            
            return GenerationResult(
                content="",
                model_key=model_key,
                model_type=self.current_backend['type'],
                generation_time=generation_time,
                error=error_msg
            )
    
    def _generate_local(self, prompt: str, max_tokens: int, temperature: float, **kwargs) -> str:
        """本地模型生成"""
        model_name = self.current_backend['config'].name
        
        # 支持聊天模式
        if 'messages' in kwargs:
            return self.ollama_interface.generate_chat(
                model_name=model_name,
                messages=kwargs['messages'],
                max_tokens=max_tokens,
                temperature=temperature
            )
        else:
            return self.ollama_interface.generate(
                model_name=model_name,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=kwargs.get('stream', False)
            )
    
    def _generate_remote(self, prompt: str, max_tokens: int, temperature: float, **kwargs) -> str:
        """远程模型生成"""
        config = self.current_backend['config']
        
        # 根据提供商选择API密钥和请求格式
        if config.provider == 'GLM':
            if not self.glm_api_key:
                raise Exception("GLM模型需要GLM_API_KEY")
            api_key = self.glm_api_key
        else:
            if not self.api_key:
                raise Exception("ModelScope模型需要MODELSCOPE_SDK_TOKEN")
            api_key = self.api_key
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 支持聊天格式
        if 'messages' in kwargs:
            messages = kwargs['messages']
        else:
            messages = [{"role": "user", "content": prompt}]
        
        data = {
            "model": config.name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # 重试机制
        max_retries = 3
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    config.api_url,
                    headers=headers,
                    json=data,
                    timeout=config.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content']
                    else:
                        raise Exception(f"API响应格式错误: {result}")
                else:
                    # 检查是否是内容过滤错误
                    if response.status_code == 400:
                        try:
                            error_data = response.json()
                            if 'error' in error_data and 'code' in error_data['error']:
                                error_code = error_data['error']['code']
                                if error_code == '1301':  # GLM内容过滤错误
                                    raise ContentFilterException(f"内容过滤错误: {error_data['error']['message']}")
                        except (ValueError, KeyError):
                            pass
                    
                    raise Exception(f"API调用失败 (状态码: {response.status_code}): {response.text}")
                    
            except ContentFilterException:
                # 内容过滤错误不重试，直接抛出
                raise
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"请求超时，重试中... ({attempt + 1}/{max_retries})")
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    raise Exception("请求超时")
            except requests.exceptions.ConnectionError:
                if attempt < max_retries - 1:
                    print(f"连接错误，重试中... ({attempt + 1}/{max_retries})")
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    raise Exception("连接错误")
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"请求失败，重试中... ({attempt + 1}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    raise e
        
        raise Exception("所有重试都失败了")
    
    def generate_chat(self, messages: list, max_tokens: Optional[int] = None,
                     temperature: Optional[float] = None) -> GenerationResult:
        """聊天模式生成"""
        return self.generate("", max_tokens, temperature, messages=messages)
    
    def list_available_models(self) -> Dict[str, Any]:
        """列出所有可用模型"""
        result = {
            'remote': {},
            'local': {}
        }
        
        # 远程模型
        remote_models = self.model_manager.list_models_by_type('remote')
        for key, config in remote_models.items():
            # 根据提供商检查对应的API密钥
            if config.provider == 'GLM':
                available = bool(self.glm_api_key)
            else:
                available = bool(self.api_key)
            
            result['remote'][key] = {
                'name': config.name,
                'provider': config.provider,
                'description': config.description,
                'available': available
            }
        
        # 本地模型
        local_models = self.model_manager.list_models_by_type('local')
        ollama_available = self.ollama_interface.is_available()
        installed_models = []
        
        if ollama_available:
            installed_models = [m['name'] for m in self.ollama_interface.get_installed_models()]
        
        for key, config in local_models.items():
            result['local'][key] = {
                'name': config.name,
                'provider': config.provider,
                'description': config.description,
                'available': ollama_available,
                'installed': config.name in installed_models
            }
        
        return result
    
    def switch_model(self, model_key: str) -> bool:
        """切换模型（set_model的别名）"""
        return self.set_model(model_key)
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """获取生成统计信息"""
        stats = self.generation_stats.copy()
        
        # 计算平均响应时间
        if stats['successful_requests'] > 0:
            stats['average_time'] = stats['total_time'] / stats['successful_requests']
        else:
            stats['average_time'] = 0.0
        
        # 计算成功率
        if stats['total_requests'] > 0:
            stats['success_rate'] = stats['successful_requests'] / stats['total_requests']
        else:
            stats['success_rate'] = 0.0
        
        return stats
    
    def reset_stats(self):
        """重置统计信息"""
        self.generation_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_time': 0.0,
            'model_usage': {}
        }
        print("统计信息已重置")
    
    def get_status(self) -> Dict[str, Any]:
        """获取接口状态"""
        current_model = self.get_current_model()
        stats = self.get_generation_stats()
        
        return {
            'current_model': current_model,
            'api_key_available': bool(self.api_key),
            'ollama_available': self.ollama_interface.is_available(),
            'ollama_models': len(self.ollama_interface.get_installed_models()),
            'generation_stats': stats,
            'model_manager_stats': self.model_manager.get_model_statistics()
        }
    
    def test_model(self, model_key: Optional[str] = None) -> Dict[str, Any]:
        """测试模型是否正常工作"""
        if model_key:
            # 临时切换到指定模型进行测试
            original_backend = self.current_backend
            if not self.set_model(model_key):
                return {
                    'success': False,
                    'error': f'无法切换到模型: {model_key}',
                    'model_key': model_key
                }
        
        if not self.current_backend:
            return {
                'success': False,
                'error': '未设置模型',
                'model_key': None
            }
        
        test_prompt = "请回复'测试成功'"
        
        try:
            result = self.generate(test_prompt, max_tokens=50, temperature=0.1)
            
            success = not result.error and len(result.content.strip()) > 0
            
            test_result = {
                'success': success,
                'model_key': result.model_key,
                'model_type': result.model_type,
                'response': result.content,
                'generation_time': result.generation_time,
                'error': result.error
            }
            
            # 如果是临时测试，恢复原来的模型
            if model_key and original_backend:
                self.current_backend = original_backend
            
            return test_result
            
        except Exception as e:
            # 如果是临时测试，恢复原来的模型
            if model_key and original_backend:
                self.current_backend = original_backend
            
            return {
                'success': False,
                'error': str(e),
                'model_key': self.current_backend['key'] if self.current_backend else None
            }
    
    def auto_select_best_model(self) -> Optional[str]:
        """自动选择最佳可用模型"""
        available_models = self.list_available_models()
        
        # 优先级：本地已安装模型 > 远程模型 > 本地未安装模型
        
        # 1. 检查本地已安装模型
        for key, info in available_models['local'].items():
            if info['available'] and info['installed']:
                if self.set_model(key):
                    print(f"自动选择本地模型: {key}")
                    return key
        
        # 2. 检查远程模型
        if self.api_key:
            for key, info in available_models['remote'].items():
                if info['available']:
                    if self.set_model(key):
                        print(f"自动选择远程模型: {key}")
                        return key
        
        # 3. 尝试本地未安装模型（会自动拉取）
        for key, info in available_models['local'].items():
            if info['available'] and not info['installed']:
                if self.set_model(key):
                    print(f"自动选择并安装本地模型: {key}")
                    return key
        
        print("未找到可用模型")
        return None
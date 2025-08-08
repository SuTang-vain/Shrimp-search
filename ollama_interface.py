"""
Ollama接口 - 与本地部署的Ollama服务通信
支持流式和非流式响应
"""

import requests
import json
import time
from typing import Optional, Dict, Any, Generator
from dataclasses import dataclass

@dataclass
class OllamaResponse:
    """Ollama响应数据类"""
    content: str
    model: str
    done: bool
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    eval_count: Optional[int] = None

class OllamaInterface:
    """Ollama本地模型接口"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip('/')
        self.available = False
        self.installed_models = []
        self._check_availability()
    
    def _check_availability(self) -> bool:
        """检查Ollama服务是否可用"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.available = True
                data = response.json()
                self.installed_models = [model['name'] for model in data.get('models', [])]
                print(f"Ollama服务可用，已安装模型: {len(self.installed_models)}个")
                return True
            else:
                print(f"Ollama服务响应异常: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("Ollama服务连接失败，请确保Ollama已启动")
            return False
        except requests.exceptions.Timeout:
            print("Ollama服务连接超时")
            return False
        except Exception as e:
            print(f"检查Ollama服务时出错: {e}")
            return False
    
    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self.available
    
    def get_installed_models(self) -> list:
        """获取已安装的模型列表"""
        if not self.available:
            return []
        
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data.get('models', []):
                    models.append({
                        'name': model['name'],
                        'size': model.get('size', 0),
                        'modified_at': model.get('modified_at', '')
                    })
                self.installed_models = [m['name'] for m in models]
                return models
            return []
        except Exception as e:
            print(f"获取模型列表失败: {e}")
            return []
    
    def check_model_exists(self, model_name: str) -> bool:
        """检查指定模型是否已安装"""
        if not self.available:
            return False
        
        models = self.get_installed_models()
        return any(model['name'] == model_name for model in models)
    
    def pull_model(self, model_name: str) -> bool:
        """拉取模型"""
        if not self.available:
            print("Ollama服务不可用")
            return False
        
        try:
            print(f"正在拉取模型: {model_name}")
            data = {"name": model_name}
            
            response = requests.post(
                f"{self.base_url}/api/pull",
                json=data,
                stream=True,
                timeout=300  # 5分钟超时
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            json_response = json.loads(line)
                            status = json_response.get('status', '')
                            if 'pulling' in status.lower():
                                print(f"拉取进度: {status}")
                            elif json_response.get('error'):
                                print(f"拉取错误: {json_response['error']}")
                                return False
                        except json.JSONDecodeError:
                            continue
                
                print(f"模型 {model_name} 拉取完成")
                self._check_availability()  # 更新模型列表
                return True
            else:
                print(f"拉取模型失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"拉取模型时出错: {e}")
            return False
    
    def generate(self, model_name: str, prompt: str, max_tokens: int = 1000, 
                temperature: float = 0.7, stream: bool = False) -> str:
        """生成文本响应"""
        if not self.available:
            raise Exception("Ollama服务不可用，请确保Ollama已启动")
        
        # 检查模型是否存在
        if not self.check_model_exists(model_name):
            print(f"模型 {model_name} 未安装，尝试自动拉取...")
            if not self.pull_model(model_name):
                raise Exception(f"模型 {model_name} 不可用且拉取失败")
        
        data = {
            "model": model_name,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "top_p": 0.9,
                "top_k": 40
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                stream=stream,
                timeout=120
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API调用失败: {response.status_code} - {response.text}")
            
            if stream:
                return self._handle_stream_response(response)
            else:
                return self._handle_single_response(response)
                
        except requests.exceptions.Timeout:
            raise Exception("Ollama请求超时")
        except requests.exceptions.ConnectionError:
            raise Exception("无法连接到Ollama服务")
        except Exception as e:
            raise Exception(f"Ollama生成失败: {e}")
    
    def _handle_stream_response(self, response) -> str:
        """处理流式响应"""
        result = ""
        try:
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    if 'response' in json_response:
                        result += json_response['response']
                    if json_response.get('done', False):
                        break
            return result
        except Exception as e:
            raise Exception(f"处理流式响应失败: {e}")
    
    def _handle_single_response(self, response) -> str:
        """处理单次响应"""
        try:
            data = response.json()
            if 'response' in data:
                return data['response']
            else:
                raise Exception("响应格式错误")
        except json.JSONDecodeError:
            raise Exception("响应不是有效的JSON格式")
    
    def generate_chat(self, model_name: str, messages: list, max_tokens: int = 1000,
                     temperature: float = 0.7) -> str:
        """聊天模式生成（支持多轮对话）"""
        if not self.available:
            raise Exception("Ollama服务不可用")
        
        # 检查模型是否存在
        if not self.check_model_exists(model_name):
            print(f"模型 {model_name} 未安装，尝试自动拉取...")
            if not self.pull_model(model_name):
                raise Exception(f"模型 {model_name} 不可用且拉取失败")
        
        data = {
            "model": model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'message' in result and 'content' in result['message']:
                    return result['message']['content']
                else:
                    raise Exception("聊天响应格式错误")
            else:
                raise Exception(f"聊天API调用失败: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Ollama聊天生成失败: {e}")
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """获取模型详细信息"""
        if not self.available:
            return None
        
        try:
            data = {"name": model_name}
            response = requests.post(f"{self.base_url}/api/show", json=data, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"获取模型信息失败: {e}")
            return None
    
    def delete_model(self, model_name: str) -> bool:
        """删除模型"""
        if not self.available:
            return False
        
        try:
            data = {"name": model_name}
            response = requests.delete(f"{self.base_url}/api/delete", json=data, timeout=30)
            
            if response.status_code == 200:
                print(f"模型 {model_name} 已删除")
                self._check_availability()  # 更新模型列表
                return True
            else:
                print(f"删除模型失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"删除模型时出错: {e}")
            return False
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            'available': self.available,
            'base_url': self.base_url,
            'installed_models': len(self.installed_models),
            'model_list': self.installed_models
        }
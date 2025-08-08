"""
模型管理器 - 统一管理本地和远程模型
支持ModelScope远程API和Ollama本地部署
"""

import os
import json
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """模型配置类"""
    name: str
    provider: str
    api_url: str
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 60
    description: str = ""

class ModelManager:
    """模型管理器 - 统一管理不同类型的模型"""
    
    def __init__(self):
        self.available_models = self._initialize_models()
        self.current_model_key = None
        self.current_model_type = None
        
    def _initialize_models(self) -> Dict[str, Dict[str, ModelConfig]]:
        """初始化可用模型配置"""
        return {
            'remote': {
                'qwen2.5-72b': ModelConfig(
                    name='Qwen/Qwen2.5-72B-Instruct',
                    provider='ModelScope',
                    api_url='https://api-inference.modelscope.cn/v1/chat/completions',
                    max_tokens=1000,
                    temperature=0.7,
                    description='通义千问2.5-72B模型，适合复杂推理任务'
                ),
                'qwen2.5-14b': ModelConfig(
                    name='Qwen/Qwen2.5-14B-Instruct',
                    provider='ModelScope', 
                    api_url='https://api-inference.modelscope.cn/v1/chat/completions',
                    max_tokens=1000,
                    temperature=0.7,
                    description='通义千问2.5-14B模型，平衡性能和速度'
                ),
                'qwen2.5-7b': ModelConfig(
                    name='Qwen/Qwen2.5-7B-Instruct',
                    provider='ModelScope',
                    api_url='https://api-inference.modelscope.cn/v1/chat/completions',
                    max_tokens=1000,
                    temperature=0.7,
                    description='通义千问2.5-7B模型，快速响应'
                ),
                'glm4.5': ModelConfig(
                    name='glm-4-plus',
                    provider='GLM',
                    api_url='https://open.bigmodel.cn/api/paas/v4/chat/completions',
                    max_tokens=1000,
                    temperature=0.7,
                    description='GLM4.5模型，智谱AI提供的高性能语言模型'
                )
            },
            'local': {
                'qwen2.5-7b-local': ModelConfig(
                    name='qwen2.5:7b',
                    provider='Ollama',
                    api_url='http://localhost:11434',
                    max_tokens=1000,
                    temperature=0.7,
                    description='本地部署的通义千问2.5-7B模型，数据隐私保护'
                ),
                'qwen2.5-14b-local': ModelConfig(
                    name='qwen2.5:14b',
                    provider='Ollama',
                    api_url='http://localhost:11434',
                    max_tokens=1000,
                    temperature=0.7,
                    description='本地部署的通义千问2.5-14B模型'
                )
            }
        }
    
    def get_available_models(self) -> Dict[str, Dict[str, ModelConfig]]:
        """获取所有可用模型"""
        return self.available_models
    
    def get_model_config(self, model_key: str) -> Optional[Tuple[str, ModelConfig]]:
        """根据模型键获取模型配置"""
        for model_type, models in self.available_models.items():
            if model_key in models:
                return model_type, models[model_key]
        return None
    
    def set_current_model(self, model_key: str) -> bool:
        """设置当前使用的模型"""
        result = self.get_model_config(model_key)
        if result:
            model_type, model_config = result
            self.current_model_key = model_key
            self.current_model_type = model_type
            print(f"已设置当前模型: {model_key} ({model_config.provider})")
            return True
        else:
            print(f"未找到模型: {model_key}")
            return False
    
    def get_current_model(self) -> Optional[Tuple[str, str, ModelConfig]]:
        """获取当前模型信息"""
        if self.current_model_key and self.current_model_type:
            model_config = self.available_models[self.current_model_type][self.current_model_key]
            return self.current_model_type, self.current_model_key, model_config
        return None
    
    def list_models_by_type(self, model_type: str) -> Dict[str, ModelConfig]:
        """按类型列出模型"""
        return self.available_models.get(model_type, {})
    
    def add_custom_model(self, model_type: str, model_key: str, config: ModelConfig) -> bool:
        """添加自定义模型配置"""
        try:
            if model_type not in self.available_models:
                self.available_models[model_type] = {}
            
            self.available_models[model_type][model_key] = config
            print(f"已添加自定义模型: {model_key}")
            return True
        except Exception as e:
            print(f"添加自定义模型失败: {e}")
            return False
    
    def remove_model(self, model_key: str) -> bool:
        """移除模型配置"""
        try:
            for model_type, models in self.available_models.items():
                if model_key in models:
                    del models[model_key]
                    if self.current_model_key == model_key:
                        self.current_model_key = None
                        self.current_model_type = None
                    print(f"已移除模型: {model_key}")
                    return True
            print(f"未找到要移除的模型: {model_key}")
            return False
        except Exception as e:
            print(f"移除模型失败: {e}")
            return False
    
    def get_model_statistics(self) -> Dict[str, Any]:
        """获取模型统计信息"""
        stats = {
            'total_models': 0,
            'remote_models': 0,
            'local_models': 0,
            'current_model': self.current_model_key,
            'current_type': self.current_model_type
        }
        
        for model_type, models in self.available_models.items():
            count = len(models)
            stats['total_models'] += count
            if model_type == 'remote':
                stats['remote_models'] = count
            elif model_type == 'local':
                stats['local_models'] = count
        
        return stats
    
    def save_config(self, config_path: str = "model_config.json") -> bool:
        """保存模型配置到文件"""
        try:
            config_data = {
                'current_model_key': self.current_model_key,
                'current_model_type': self.current_model_type,
                'available_models': {}
            }
            
            # 转换ModelConfig对象为字典
            for model_type, models in self.available_models.items():
                config_data['available_models'][model_type] = {}
                for key, config in models.items():
                    config_data['available_models'][model_type][key] = {
                        'name': config.name,
                        'provider': config.provider,
                        'api_url': config.api_url,
                        'max_tokens': config.max_tokens,
                        'temperature': config.temperature,
                        'timeout': config.timeout,
                        'description': config.description
                    }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            print(f"模型配置已保存到: {config_path}")
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def load_config(self, config_path: str = "model_config.json") -> bool:
        """从文件加载模型配置"""
        try:
            if not os.path.exists(config_path):
                print(f"配置文件不存在: {config_path}")
                return False
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 重建ModelConfig对象
            self.available_models = {}
            for model_type, models in config_data['available_models'].items():
                self.available_models[model_type] = {}
                for key, config_dict in models.items():
                    self.available_models[model_type][key] = ModelConfig(**config_dict)
            
            self.current_model_key = config_data.get('current_model_key')
            self.current_model_type = config_data.get('current_model_type')
            
            print(f"模型配置已从 {config_path} 加载")
            return True
        except Exception as e:
            print(f"加载配置失败: {e}")
            return False
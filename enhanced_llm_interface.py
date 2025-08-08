"""
增强的LLM接口 - 改进CAMEL稳定性和错误处理
"""

import os
import time
import requests
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class LLMConfig:
    """LLM配置类"""
    model_name: str = "Qwen/Qwen2.5-72B-Instruct"
    api_url: str = "https://api-inference.modelscope.cn/v1/chat/completions"
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0

class EnhancedLLMInterface:
    """增强的LLM接口 - 提供更稳定的CAMEL集成和降级机制"""
    
    def __init__(self, api_key: str, config: Optional[LLMConfig] = None):
        if not api_key:
            raise ValueError("API密钥不能为空")
        
        self.api_key = api_key
        self.config = config or LLMConfig()
        self.camel_model = None
        self.camel_available = False
        
        # 尝试初始化CAMEL模型
        self._initialize_camel()
        
    def _initialize_camel(self):
        """初始化CAMEL模型 - 增强错误处理"""
        try:
            from camel.models import ModelFactory
            from camel.types import ModelPlatformType
            
            print("正在初始化CAMEL模型...")
            
            # 使用更稳定的配置
            self.camel_model = ModelFactory.create(
                model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
                model_type=self.config.model_name,
                url=self.config.api_url.replace('/chat/completions', ''),
                api_key=self.api_key,
                model_config_dict={
                    'temperature': self.config.temperature,
                    'max_tokens': self.config.max_tokens
                }
            )
            
            # 测试CAMEL模型是否可用
            test_result = self._test_camel_model()
            if test_result:
                self.camel_available = True
                print("✓ CAMEL模型初始化成功并通过测试")
            else:
                print("⚠ CAMEL模型初始化成功但测试失败，将使用直接API调用")
                self.camel_available = False
                
        except ImportError:
            print("⚠ CAMEL库未安装，使用直接API调用")
            self.camel_available = False
        except Exception as e:
            print(f"⚠ CAMEL模型初始化失败: {str(e)[:100]}...")
            print("将使用直接API调用作为备用方案")
            self.camel_available = False
    
    def _test_camel_model(self) -> bool:
        """测试CAMEL模型是否正常工作"""
        try:
            from camel.messages import BaseMessage
            
            test_message = BaseMessage.make_user_message(
                role_name="user",
                content="测试消息，请回复'测试成功'"
            )
            
            response = self.camel_model.run([test_message])
            
            # 检查响应是否有效
            if response and (
                (hasattr(response, 'content') and response.content) or
                (isinstance(response, list) and len(response) > 0) or
                isinstance(response, str)
            ):
                return True
            return False
            
        except Exception as e:
            print(f"CAMEL模型测试失败: {str(e)[:50]}...")
            return False
    
    def generate(self, prompt: str, max_tokens: Optional[int] = None, 
                temperature: Optional[float] = None) -> str:
        """生成文本 - 智能选择CAMEL或直接API"""
        
        # 使用提供的参数或默认配置
        max_tokens = max_tokens or self.config.max_tokens
        temperature = temperature or self.config.temperature
        
        # 优先尝试CAMEL模型
        if self.camel_available:
            try:
                return self._generate_with_camel(prompt, max_tokens, temperature)
            except Exception as e:
                print(f"⚠ CAMEL生成失败，切换到直接API: {str(e)[:50]}...")
                # 标记CAMEL不可用，避免后续重复尝试
                self.camel_available = False
        
        # 使用直接API调用
        return self._generate_with_api(prompt, max_tokens, temperature)
    
    def _generate_with_camel(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """使用CAMEL模型生成"""
        from camel.messages import BaseMessage
        
        user_message = BaseMessage.make_user_message(
            role_name="user",
            content=prompt
        )
        
        response = self.camel_model.run([user_message])
        
        # 改进的响应处理
        if hasattr(response, 'content'):
            return response.content
        elif isinstance(response, list) and len(response) > 0:
            first_response = response[0]
            if hasattr(first_response, 'content'):
                return first_response.content
            else:
                return str(first_response)
        elif isinstance(response, str):
            return response
        else:
            raise Exception("CAMEL模型返回了无效响应格式")
    
    def _generate_with_api(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """使用直接API调用生成 - 增强重试机制"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                print(f"API调用尝试 {attempt + 1}/{self.config.max_retries}")
                
                response = requests.post(
                    self.config.api_url,
                    headers=headers,
                    json=data,
                    timeout=self.config.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        content = result['choices'][0]['message']['content']
                        print("✓ API调用成功")
                        return content
                    else:
                        raise Exception(f"API响应格式错误: {result}")
                else:
                    raise Exception(f"API调用失败 (状态码: {response.status_code}): {response.text}")
                    
            except requests.exceptions.Timeout:
                last_error = f"API调用超时 (尝试 {attempt + 1})"
                print(last_error)
            except requests.exceptions.ConnectionError:
                last_error = f"网络连接错误 (尝试 {attempt + 1})"
                print(last_error)
            except Exception as e:
                last_error = f"API调用失败: {str(e)}"
                print(f"{last_error} (尝试 {attempt + 1})")
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < self.config.max_retries - 1:
                time.sleep(self.config.retry_delay * (attempt + 1))  # 递增延迟
        
        # 所有重试都失败了
        return f"抱歉，经过{self.config.max_retries}次尝试后仍无法生成回答。最后错误: {last_error}"
    
    def get_status(self) -> Dict[str, Any]:
        """获取LLM接口状态"""
        return {
            "camel_available": self.camel_available,
            "model_name": self.config.model_name,
            "api_url": self.config.api_url,
            "max_retries": self.config.max_retries
        }
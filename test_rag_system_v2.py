"""
增强RAG系统V2测试文件
测试多端模型选择和基础功能
"""

import os
import sys
import pytest
import tempfile
from unittest.mock import Mock, patch, MagicMock

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model_manager import ModelManager, ModelConfig
from ollama_interface import OllamaInterface
from enhanced_llm_interface_v2 import EnhancedLLMInterfaceV2, GenerationResult

class TestModelManager:
    """测试模型管理器"""
    
    def test_model_manager_initialization(self):
        """测试模型管理器初始化"""
        manager = ModelManager()
        
        # 检查默认模型配置
        assert 'remote' in manager.available_models
        assert 'local' in manager.available_models
        assert 'qwen2.5-72b' in manager.available_models['remote']
        assert 'qwen2.5-7b' in manager.available_models['local']
    
    def test_get_model_config(self):
        """测试获取模型配置"""
        manager = ModelManager()
        
        # 测试远程模型
        result = manager.get_model_config('qwen2.5-72b')
        assert result is not None
        model_type, config = result
        assert model_type == 'remote'
        assert isinstance(config, ModelConfig)
        assert config.provider == 'ModelScope'
        
        # 测试本地模型
        result = manager.get_model_config('qwen2.5-7b')
        assert result is not None
        model_type, config = result
        assert model_type == 'local'
        assert config.provider == 'Ollama'
        
        # 测试不存在的模型
        result = manager.get_model_config('nonexistent-model')
        assert result is None

class TestOllamaInterface:
    """测试Ollama接口"""
    
    @patch('requests.get')
    def test_ollama_availability_check(self, mock_get):
        """测试Ollama可用性检查"""
        # 测试服务可用
        mock_get.return_value.status_code = 200
        interface = OllamaInterface()
        assert interface.is_available() == True
        
        # 测试服务不可用
        mock_get.side_effect = Exception("连接失败")
        interface = OllamaInterface()
        assert interface.is_available() == False
    
    @patch('requests.get')
    def test_get_installed_models(self, mock_get):
        """测试获取已安装模型"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "qwen2.5:7b", "size": 4000000000},
                {"name": "llama2:7b", "size": 3800000000}
            ]
        }
        mock_get.return_value = mock_response
        
        interface = OllamaInterface()
        models = interface.get_installed_models()
        
        assert len(models) == 2
        assert models[0]['name'] == 'qwen2.5:7b'
        assert models[1]['name'] == 'llama2:7b'
    
    @patch('requests.post')
    def test_generate_text(self, mock_post):
        """测试文本生成"""
        # 模拟流式响应
        mock_response = Mock()
        mock_response.iter_lines.return_value = [
            b'{"response": "Hello", "done": false}',
            b'{"response": " world", "done": false}',
            b'{"response": "!", "done": true}'
        ]
        mock_post.return_value = mock_response
        
        interface = OllamaInterface()
        result = interface.generate("qwen2.5:7b", "Hello", max_tokens=100)
        
        assert result == "Hello world!"

class TestEnhancedLLMInterfaceV2:
    """测试增强LLM接口V2"""
    
    @patch('ollama_interface.OllamaInterface')
    def test_llm_interface_initialization(self, mock_ollama):
        """测试LLM接口初始化"""
        mock_ollama_instance = Mock()
        mock_ollama_instance.is_available.return_value = True
        mock_ollama.return_value = mock_ollama_instance
        
        llm = EnhancedLLMInterfaceV2(api_key="test_key")
        
        assert llm.api_key == "test_key"
        assert llm.model_manager is not None
        assert llm.ollama_interface is not None
        assert llm.current_backend is None
    
    @patch('ollama_interface.OllamaInterface')
    def test_set_local_model(self, mock_ollama):
        """测试设置本地模型"""
        mock_ollama_instance = Mock()
        mock_ollama_instance.is_available.return_value = True
        mock_ollama_instance.check_model_exists.return_value = True
        mock_ollama.return_value = mock_ollama_instance
        
        llm = EnhancedLLMInterfaceV2()
        result = llm.set_model('qwen2.5-7b')
        
        assert result == True
        assert llm.current_backend is not None
        assert llm.current_backend['type'] == 'local'
        assert llm.current_backend['key'] == 'qwen2.5-7b'
    
    def test_set_remote_model(self):
        """测试设置远程模型"""
        llm = EnhancedLLMInterfaceV2(api_key="test_key")
        result = llm.set_model('qwen2.5-72b')
        
        assert result == True
        assert llm.current_backend is not None
        assert llm.current_backend['type'] == 'remote'
        assert llm.current_backend['key'] == 'qwen2.5-72b'
    
    def test_set_model_without_api_key(self):
        """测试无API密钥时设置远程模型"""
        llm = EnhancedLLMInterfaceV2()
        result = llm.set_model('qwen2.5-72b')
        
        assert result == False
    
    @patch('ollama_interface.OllamaInterface')
    def test_generate_with_local_model(self, mock_ollama):
        """测试本地模型生成"""
        mock_ollama_instance = Mock()
        mock_ollama_instance.is_available.return_value = True
        mock_ollama_instance.check_model_exists.return_value = True
        mock_ollama_instance.generate.return_value = "测试响应"
        mock_ollama.return_value = mock_ollama_instance
        
        llm = EnhancedLLMInterfaceV2()
        llm.set_model('qwen2.5-7b')
        
        result = llm.generate("测试提示")
        
        assert isinstance(result, GenerationResult)
        assert result.content == "测试响应"
        assert result.model_key == 'qwen2.5-7b'
        assert result.model_type == 'local'
        assert result.error is None
    
    @patch('requests.post')
    def test_generate_with_remote_model(self, mock_post):
        """测试远程模型生成"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "远程模型响应"}}
            ]
        }
        mock_post.return_value = mock_response
        
        llm = EnhancedLLMInterfaceV2(api_key="test_key")
        llm.set_model('qwen2.5-72b')
        
        result = llm.generate("测试提示")
        
        assert isinstance(result, GenerationResult)
        assert result.content == "远程模型响应"
        assert result.model_key == 'qwen2.5-72b'
        assert result.model_type == 'remote'
        assert result.error is None
    
    def test_generate_without_model(self):
        """测试未设置模型时生成"""
        llm = EnhancedLLMInterfaceV2()
        result = llm.generate("测试提示")
        
        assert isinstance(result, GenerationResult)
        assert result.content == ""
        assert result.error is not None
        assert "未设置模型" in result.error

class TestRAGSystemV2Integration:
    """测试RAG系统V2集成功能"""
    
    @patch('sentence_transformers.SentenceTransformer')
    @patch('enhanced_llm_interface_v2.EnhancedLLMInterfaceV2')
    def test_rag_system_initialization(self, mock_llm, mock_embedding):
        """测试RAG系统初始化"""
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance
        
        mock_embedding_instance = Mock()
        mock_embedding.return_value = mock_embedding_instance
        
        try:
            from Enhanced_Interactive_Multimodal_RAG_v2 import EnhancedRAGSystemV2
            rag_system = EnhancedRAGSystemV2(api_key="test_key")
            
            assert rag_system.llm is not None
            assert rag_system.embedding_model is not None
            assert rag_system.vector_retriever is not None
            assert rag_system.knowledge_base_initialized == False
            
        except ImportError as e:
            pytest.skip(f"跳过集成测试，缺少依赖: {e}")

def test_model_config_creation():
    """测试模型配置创建"""
    config = ModelConfig(
        name="test-model",
        provider="TestProvider",
        api_url="http://test.com",
        description="测试模型",
        max_tokens=1000,
        temperature=0.7,
        timeout=30
    )
    
    assert config.name == "test-model"
    assert config.provider == "TestProvider"
    assert config.api_url == "http://test.com"
    assert config.description == "测试模型"
    assert config.max_tokens == 1000
    assert config.temperature == 0.7
    assert config.timeout == 30

def test_generation_result_creation():
    """测试生成结果创建"""
    result = GenerationResult(
        content="测试内容",
        model_key="test-model",
        model_type="local",
        generation_time=1.5,
        token_count=100
    )
    
    assert result.content == "测试内容"
    assert result.model_key == "test-model"
    assert result.model_type == "local"
    assert result.generation_time == 1.5
    assert result.token_count == 100
    assert result.error is None

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
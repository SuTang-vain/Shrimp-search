# Shrimp Agent 项目主程序结构文档

## 项目概述

Shrimp Agent 是一个增强的交互式多模态RAG（检索增强生成）系统，支持多端模型选择、文档处理、网页研究和智能问答功能。项目采用前后端分离架构，支持本地部署和远程API调用。

### 核心特性
- 多模态文档处理（PDF、Word、Excel、PPT等）
- 智能网页研究和内容提取
- 多端模型支持（ModelScope远程API + Ollama本地部署）
- 向量检索和语义搜索
- 性能监控和缓存优化
- Web界面和API服务

## 项目架构

```
Shrimp Agent 系统架构
┌─────────────────────────────────────────────────────────────┐
│                    前端层 (Frontend)                        │
├─────────────────────────────────────────────────────────────┤
│  frontend/                                                  │
│  ├── server.py          # 前端HTTP服务器                    │
│  ├── index.html         # 主界面                           │
│  ├── script.js          # 前端逻辑                         │
│  └── style.css          # 样式文件                         │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼ HTTP API
┌─────────────────────────────────────────────────────────────┐
│                    API服务层 (API Layer)                    │
├─────────────────────────────────────────────────────────────┤
│  api_server_v2.py       # Flask API服务器                   │
│  ├── /api/health        # 健康检查                         │
│  ├── /api/models        # 模型管理                         │
│  ├── /api/search        # 智能搜索                         │
│  ├── /api/upload        # 文件上传                         │
│  └── /api/knowledge     # 知识库管理                       │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   核心业务层 (Core Layer)                   │
├─────────────────────────────────────────────────────────────┤
│  Enhanced_Interactive_Multimodal_RAG_v2.py                 │
│  ├── EnhancedRAGSystemV2     # 主系统类                    │
│  ├── EnhancedVectorRetrieverV2 # 向量检索器                │
│  └── 集成所有核心模块                                       │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   功能模块层 (Module Layer)                 │
├─────────────────────────────────────────────────────────────┤
│  ├── enhanced_llm_interface_v2.py    # LLM接口管理          │
│  ├── model_manager.py               # 模型管理器           │
│  ├── ollama_interface.py            # Ollama本地接口       │
│  ├── enhanced_multimodal_processor.py # 多模态处理器        │
│  ├── enhanced_web_research.py       # 网页研究系统         │
│  ├── enhanced_document_manager.py   # 文档管理器           │
│  ├── performance_monitor.py         # 性能监控             │
│  └── enhanced_user_interface_v2.py  # 用户界面             │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   数据存储层 (Storage Layer)                │
├─────────────────────────────────────────────────────────────┤
│  ├── document_cache/            # 文档缓存目录              │
│  ├── uploaded_documents/        # 上传文档目录              │
│  ├── .env                       # 环境配置文件              │
│  └── 向量数据库 (内存)           # 嵌入向量存储              │
└─────────────────────────────────────────────────────────────┘
```

## 主程序入口文件分析

### 1. API服务器入口 - `api_server_v2.py`

**功能**: Flask API服务器，为前端提供RESTful接口

**核心依赖**:
```python
from Enhanced_Interactive_Multimodal_RAG_v2 import EnhancedRAGSystemV2
from enhanced_llm_interface_v2 import EnhancedLLMInterfaceV2
from model_manager import ModelManager
from ollama_interface import OllamaInterface
```

**主要功能**:
- 初始化RAG系统
- 提供健康检查接口
- 处理文件上传和知识库管理
- 异步搜索任务处理
- 模型管理和切换

### 2. 核心RAG系统 - `Enhanced_Interactive_Multimodal_RAG_v2.py`

**功能**: 系统核心，集成所有功能模块

**核心依赖**:
```python
from enhanced_llm_interface_v2 import EnhancedLLMInterfaceV2
from enhanced_user_interface_v2 import EnhancedUserInterfaceV2
from model_manager import ModelManager
from ollama_interface import OllamaInterface
from enhanced_multimodal_processor import EnhancedMultimodalProcessor
from enhanced_web_research import EnhancedWebResearchSystem
from performance_monitor import PerformanceMonitor
from enhanced_document_manager import EnhancedDocumentManager
```

**主要类**:
- `EnhancedRAGSystemV2`: 主系统类
- `EnhancedVectorRetrieverV2`: 向量检索器

### 3. 前端服务器 - `frontend/server.py`

**功能**: 简单的HTTP服务器，提供Web界面

**特性**:
- 自动端口检测
- CORS支持
- 自动打开浏览器
- 静态文件服务

### 4. 传统主程序 - `Enhanced_Interactive_Multimodal_RAG.py`

**功能**: V1版本的主程序，提供命令行界面

**核心依赖**:
```python
from enhanced_llm_interface import EnhancedLLMInterface
from enhanced_multimodal_processor import EnhancedMultimodalProcessor
from enhanced_web_research import EnhancedWebResearchSystem
from performance_monitor import PerformanceMonitor
from enhanced_user_interface import EnhancedUserInterface
from enhanced_document_manager import EnhancedDocumentManager
```

## 核心模块依赖关系图

```
Enhanced_Interactive_Multimodal_RAG_v2.py (主程序)
├── enhanced_llm_interface_v2.py
│   ├── model_manager.py
│   └── ollama_interface.py
├── enhanced_user_interface_v2.py
│   └── enhanced_user_interface.py (继承)
├── enhanced_multimodal_processor.py
├── enhanced_web_research.py
├── enhanced_document_manager.py
└── performance_monitor.py

api_server_v2.py (API服务器)
├── Enhanced_Interactive_Multimodal_RAG_v2.py
├── enhanced_llm_interface_v2.py
├── model_manager.py
└── ollama_interface.py

frontend/server.py (前端服务器)
└── 独立运行，通过HTTP API与后端通信
```

## 文件功能详细说明

### 核心系统文件

| 文件名 | 功能描述 | 主要类/函数 |
|--------|----------|-------------|
| `Enhanced_Interactive_Multimodal_RAG_v2.py` | 主系统V2，集成所有功能 | `EnhancedRAGSystemV2`, `EnhancedVectorRetrieverV2` |
| `Enhanced_Interactive_Multimodal_RAG.py` | 主系统V1，命令行版本 | `EnhancedRAGSystem`, `EnhancedVectorRetriever` |
| `api_server_v2.py` | Flask API服务器 | `SearchTask`, `initialize_rag_system()` |

### LLM接口模块

| 文件名 | 功能描述 | 主要类/函数 |
|--------|----------|-------------|
| `enhanced_llm_interface_v2.py` | V2 LLM接口，支持多端模型 | `EnhancedLLMInterfaceV2`, `GenerationResult` |
| `enhanced_llm_interface.py` | V1 LLM接口，CAMEL集成 | `EnhancedLLMInterface`, `LLMConfig` |
| `model_manager.py` | 模型配置管理 | `ModelManager`, `ModelConfig` |
| `ollama_interface.py` | Ollama本地模型接口 | `OllamaInterface`, `OllamaResponse` |

### 处理模块

| 文件名 | 功能描述 | 主要类/函数 |
|--------|----------|-------------|
| `enhanced_multimodal_processor.py` | 多模态文档处理 | `EnhancedMultimodalProcessor` |
| `enhanced_web_research.py` | 网页研究和内容提取 | `EnhancedWebResearchSystem`, `WebSearchResult` |
| `enhanced_document_manager.py` | 文档管理和缓存 | `EnhancedDocumentManager`, `DocumentMetadata` |

### 界面和监控模块

| 文件名 | 功能描述 | 主要类/函数 |
|--------|----------|-------------|
| `enhanced_user_interface_v2.py` | V2用户界面，模型管理 | `EnhancedUserInterfaceV2` |
| `enhanced_user_interface.py` | V1用户界面，基础功能 | `EnhancedUserInterface` |
| `performance_monitor.py` | 性能监控和统计 | `PerformanceMonitor`, `PerformanceMetrics` |

### 前端文件

| 文件名 | 功能描述 | 技术栈 |
|--------|----------|--------|
| `frontend/server.py` | 前端HTTP服务器 | Python http.server |
| `frontend/index.html` | 主界面 | HTML5 |
| `frontend/script.js` | 前端逻辑 | JavaScript ES6+ |
| `frontend/style.css` | 样式文件 | CSS3 |

## 启动流程分析

### 1. 完整系统启动流程

```
启动脚本: start_shrimp_agent_v1.0.bat
├── 1. 显示版本信息
├── 2. 停止现有Python进程
├── 3. 启动后端API服务器 (api_server_v2.py:5000)
│   ├── 加载环境变量 (.env)
│   ├── 初始化RAG系统
│   │   ├── 加载嵌入模型 (sentence-transformers)
│   │   ├── 初始化LLM接口
│   │   ├── 初始化各功能模块
│   │   └── 创建向量检索器
│   ├── 配置Flask路由
│   └── 启动API服务
├── 4. 启动前端服务器 (frontend/server.py:8080)
│   ├── 检测端口可用性
│   ├── 启动HTTP服务器
│   └── 自动打开浏览器
└── 5. 显示访问地址和使用说明
```

### 2. API服务器初始化流程

```python
# api_server_v2.py 启动流程
1. 加载环境变量
   ├── MODELSCOPE_SDK_TOKEN
   ├── GLM_API_KEY
   └── 其他配置参数

2. 初始化RAG系统
   ├── EnhancedRAGSystemV2()
   │   ├── 加载嵌入模型 (intfloat/e5-large-v2)
   │   ├── 初始化LLM接口 (EnhancedLLMInterfaceV2)
   │   ├── 初始化文档管理器
   │   ├── 初始化多模态处理器
   │   ├── 初始化网页研究系统
   │   └── 创建向量检索器
   └── 设置默认模型

3. 配置Flask应用
   ├── 设置CORS
   ├── 配置路由
   └── 设置错误处理

4. 启动服务器
   └── app.run(host='0.0.0.0', port=5000)
```

### 3. 核心RAG系统初始化流程

```python
# Enhanced_Interactive_Multimodal_RAG_v2.py 初始化
1. 性能监控初始化
   └── PerformanceMonitor()

2. LLM接口初始化
   ├── EnhancedLLMInterfaceV2()
   │   ├── ModelManager() # 模型配置管理
   │   ├── OllamaInterface() # 本地模型接口
   │   └── 模型可用性检测
   └── 打印可用模型列表

3. 嵌入模型加载
   └── SentenceTransformer('intfloat/e5-large-v2')

4. 功能模块初始化
   ├── EnhancedVectorRetrieverV2() # 向量检索器
   ├── EnhancedDocumentManager() # 文档管理器
   ├── EnhancedMultimodalProcessor() # 多模态处理器
   └── EnhancedWebResearchSystem() # 网页研究系统

5. 系统状态初始化
   ├── knowledge_base_initialized = False
   ├── multimodal_content_store = {}
   ├── current_sources = []
   └── document_chunks_store = {}
```

## 模块间调用关系

### 1. API请求处理流程

```
前端请求 → api_server_v2.py → Enhanced_Interactive_Multimodal_RAG_v2.py
                                ↓
                        根据请求类型分发到相应模块:
                        ├── 搜索请求 → vector_retriever + llm_interface
                        ├── 文件上传 → document_manager + multimodal_processor
                        ├── 网页研究 → web_research_system
                        └── 模型管理 → model_manager + ollama_interface
```

### 2. 搜索处理流程

```
用户搜索查询
├── 1. 向量检索 (EnhancedVectorRetrieverV2)
│   ├── 计算查询嵌入
│   ├── 相似度计算
│   └── 返回相关文档
├── 2. 网页研究 (可选)
│   ├── 并发搜索
│   ├── 内容提取
│   └── 结果整合
├── 3. 上下文构建
│   ├── 合并检索结果
│   ├── 格式化上下文
│   └── 生成提示词
└── 4. LLM生成回答
    ├── 模型选择
    ├── 生成回答
    └── 返回结果
```

### 3. 文档处理流程

```
文档上传
├── 1. 文件验证 (api_server_v2.py)
├── 2. 多模态处理 (EnhancedMultimodalProcessor)
│   ├── 格式检测
│   ├── 内容提取 (文本/图像/表格)
│   └── 结构化处理
├── 3. 文档管理 (EnhancedDocumentManager)
│   ├── 缓存检查
│   ├── 分块处理
│   └── 元数据存储
├── 4. 向量化 (EnhancedVectorRetrieverV2)
│   ├── 嵌入计算
│   ├── 向量存储
│   └── 索引更新
└── 5. 知识库更新
    └── 状态同步
```

## 配置文件和环境要求

### 1. 环境配置文件 (`.env`)

```bash
# ModelScope API配置
MODELSCOPE_SDK_TOKEN=your_modelscope_token

# GLM API配置
GLM_API_KEY=your_glm_api_key

# 系统配置
CACHE_DIR=document_cache
UPLOAD_DIR=uploaded_documents
MAX_CACHE_SIZE_MB=1000

# 性能配置
ENABLE_PERFORMANCE_MONITORING=true
MAX_WORKERS=3
TIMEOUT=60
```

### 2. Python依赖 (`requirements.txt`)

```
# 核心依赖
flask>=2.0.0
flask-cors>=3.0.0
requests>=2.25.0
numpy>=1.21.0
scikit-learn>=1.0.0

# 嵌入模型
sentence-transformers>=2.2.0
torch>=1.9.0

# 文档处理
unstructured>=0.10.0
PyMuPDF>=1.20.0
python-docx>=0.8.11
openpyxl>=3.0.9
python-pptx>=0.6.21
pandas>=1.3.0
tabula-py>=2.5.0

# 图像处理
Pillow>=8.3.0
pytesseract>=0.3.8

# 网页处理
beautifulsoup4>=4.10.0
duckduckgo-search>=3.8.0
aiohttp>=3.8.0

# 系统监控
psutil>=5.8.0

# 环境管理
python-dotenv>=0.19.0

# 可选依赖
camel-ai>=0.1.0  # CAMEL框架支持
```

### 3. 系统要求

**硬件要求**:
- CPU: 4核心以上推荐
- 内存: 8GB以上推荐 (嵌入模型需要较大内存)
- 存储: 10GB以上可用空间
- 网络: 稳定的互联网连接 (用于远程API调用)

**软件要求**:
- Python 3.8+
- Conda环境管理器
- Ollama (可选，用于本地模型部署)
- Tesseract OCR (可选，用于图像文字识别)

**环境配置**:
```bash
# 创建Conda环境
conda create -n enhanced_rag_system python=3.9
conda activate enhanced_rag_system

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，填入API密钥
```

## 数据流向分析

### 1. 用户查询数据流

```
用户输入查询
    ↓
前端 (script.js)
    ↓ HTTP POST /api/search
API服务器 (api_server_v2.py)
    ↓
RAG系统 (Enhanced_Interactive_Multimodal_RAG_v2.py)
    ↓
并行处理:
├── 向量检索 (EnhancedVectorRetrieverV2)
│   ├── 查询嵌入计算
│   ├── 相似度搜索
│   └── 相关文档返回
└── 网页研究 (EnhancedWebResearchSystem)
    ├── 搜索引擎查询
    ├── 网页内容提取
    └── 相关信息返回
    ↓
上下文整合
    ↓
LLM接口 (EnhancedLLMInterfaceV2)
├── 模型选择 (ModelManager)
├── 提示词构建
└── 生成回答
    ↓
结果返回
    ↓
前端显示
```

### 2. 文档上传数据流

```
用户上传文件
    ↓
前端文件选择 (index.html)
    ↓ HTTP POST /api/upload
API服务器文件处理 (api_server_v2.py)
    ↓
文件保存 (uploaded_documents/)
    ↓
多模态处理器 (EnhancedMultimodalProcessor)
├── 文件格式检测
├── 内容提取
│   ├── 文本提取
│   ├── 图像OCR
│   └── 表格解析
└── 结构化数据输出
    ↓
文档管理器 (EnhancedDocumentManager)
├── 缓存检查
├── 文档分块
├── 元数据生成
└── 缓存存储 (document_cache/)
    ↓
向量化处理 (EnhancedVectorRetrieverV2)
├── 嵌入计算
├── 向量存储
└── 索引更新
    ↓
知识库状态更新
    ↓
处理结果返回前端
```

### 3. 模型管理数据流

```
模型切换请求
    ↓
前端模型选择
    ↓ HTTP POST /api/models/switch
API服务器 (api_server_v2.py)
    ↓
LLM接口 (EnhancedLLMInterfaceV2)
    ↓
模型管理器 (ModelManager)
├── 模型配置查询
├── 可用性验证
└── 模型切换
    ↓
本地模型处理 (如果是Ollama模型)
├── Ollama接口 (OllamaInterface)
├── 模型存在检查
├── 自动下载 (如需要)
└── 模型加载
    ↓
状态更新
    ↓
结果返回
```

### 4. 性能监控数据流

```
系统操作执行
    ↓
性能监控器 (PerformanceMonitor)
├── 操作开始记录
├── 资源使用监控
│   ├── CPU使用率
│   ├── 内存使用量
│   └── 执行时间
├── 操作结束记录
└── 统计数据更新
    ↓
性能指标存储 (PerformanceMetrics)
    ↓
报告生成 (可选)
    ↓
性能优化建议
```

## 缓存和存储机制

### 1. 文档缓存结构

```
document_cache/
├── metadata/
│   └── document_index.json     # 文档索引
├── chunks/
│   └── {file_hash}.pkl         # 文档块缓存
└── embeddings/
    └── {file_hash}_embeddings.pkl # 嵌入向量缓存
```

### 2. 上传文件存储

```
uploaded_documents/
├── {timestamp}_{filename}      # 上传的原始文件
└── 按时间戳组织的文件结构
```

### 3. 内存数据结构

```python
# 向量检索器内存结构
vector_retriever = {
    'documents': List[str],           # 文档文本列表
    'doc_metadata': List[Dict],       # 文档元数据
    'document_ids': List[str],        # 文档ID列表
    'doc_embeddings': np.ndarray      # 嵌入向量矩阵
}

# 多模态内容存储
multimodal_content_store = {
    'multimodal_id': {
        'type': str,                  # 内容类型
        'data': str,                  # 内容数据
        'page': int,                  # 页码
        'metadata': Dict              # 额外元数据
    }
}
```

## 错误处理和日志机制

### 1. 错误处理层级

```
1. API层错误处理 (api_server_v2.py)
   ├── HTTP状态码返回
   ├── 错误信息格式化
   └── 异常日志记录

2. 业务层错误处理 (Enhanced_Interactive_Multimodal_RAG_v2.py)
   ├── 模块初始化失败处理
   ├── 操作异常恢复
   └── 降级策略执行

3. 模块层错误处理 (各enhanced_模块)
   ├── 依赖库缺失处理
   ├── 资源不可用处理
   └── 功能降级实现
```

### 2. 日志记录机制

```python
# 日志级别和输出
INFO:  系统状态和操作进度
WARN:  非致命错误和降级操作
ERROR: 严重错误和异常情况
DEBUG: 详细调试信息 (开发模式)
```

## 扩展和维护指南

### 1. 添加新的文档格式支持

1. 在 `enhanced_multimodal_processor.py` 中添加处理函数
2. 更新 `supported_formats` 字典
3. 实现格式特定的内容提取逻辑
4. 添加相应的依赖库

### 2. 集成新的LLM模型

1. 在 `model_manager.py` 中添加模型配置
2. 如需要，扩展 `enhanced_llm_interface_v2.py` 的接口
3. 实现模型特定的调用逻辑
4. 更新模型选择界面

### 3. 添加新的搜索引擎

1. 在 `enhanced_web_research.py` 中添加搜索函数
2. 实现搜索结果解析逻辑
3. 集成到并发搜索框架中
4. 添加相应的配置选项

### 4. 性能优化建议

1. **嵌入模型优化**: 考虑使用更小的模型或量化版本
2. **缓存策略**: 实现更智能的缓存淘汰机制
3. **并发处理**: 增加异步处理能力
4. **内存管理**: 实现大文档的流式处理
5. **网络优化**: 添加请求重试和超时控制

---

**文档版本**: v1.0  
**最后更新**: 2024年1月  
**维护者**: Shrimp Agent 开发团队  

本文档详细描述了 Shrimp Agent 项目的完整架构和实现细节，为开发者提供了全面的技术参考。
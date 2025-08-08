# 增强RAG系统V2 - 多端模型选择版本

## 🚀 项目概述

本项目是一个增强的检索增强生成(RAG)系统，支持多端模型选择，包括ModelScope远程API和Ollama本地部署。系统具备完整的多模态处理、智能检索和用户交互功能。

## ✨ 核心特性

### 🤖 多端模型支持
- **远程模型**: 支持ModelScope API (Qwen2.5-7B/14B/72B)
- **本地模型**: 支持Ollama本地部署 (Qwen2.5-7B/14B)
- **自动选择**: 智能选择最佳可用模型
- **无缝切换**: 运行时动态切换模型

### 🔍 智能检索系统
- **快速检索**: 基础向量相似度检索
- **深度检索**: 查询重写 + HyDE + RRF融合
- **主题检索**: PDF文档 + 网页研究结合
- **智能检索**: 自适应选择最佳检索策略

### 📚 多模态文档处理
- **文档类型**: PDF、Word、TXT、图片、表格
- **智能分块**: 基于内容类型的智能分块
- **缓存机制**: 高效的文档缓存和增量更新
- **元数据管理**: 丰富的文档元数据支持

### 🎨 增强用户界面
- **Rich界面**: 美观的终端界面
- **交互式选择**: 模型和检索模式选择
- **实时反馈**: 处理进度和状态显示
- **错误处理**: 友好的错误提示

## 📁 项目结构

```
Shrimp_Agent0.2/
├── 核心模块/
│   ├── model_manager.py              # 模型管理器
│   ├── ollama_interface.py           # Ollama接口
│   ├── enhanced_llm_interface_v2.py  # 增强LLM接口V2
│   └── enhanced_user_interface_v2.py # 增强用户界面V2
├── RAG系统/
│   ├── Enhanced_Interactive_Multimodal_RAG_v2.py  # 主RAG系统V2
│   ├── enhanced_document_manager.py               # 文档管理器
│   ├── enhanced_multimodal_processor.py          # 多模态处理器
│   └── enhanced_web_research.py                  # 网页研究系统
├── 工具模块/
│   ├── performance_monitor.py        # 性能监控
│   └── vector_store.py              # 向量存储
├── 测试文件/
│   ├── demo_rag_v2.py               # 完整演示
│   ├── quick_test_v2.py             # 快速测试
│   └── test_rag_system_v2.py        # 单元测试
└── 配置文件/
    ├── .env                         # 环境变量
    └── requirements.txt             # 依赖包
```

## 🛠️ 安装配置

### 1. 环境准备

```bash
# 克隆项目
git clone <repository_url>
cd Shrimp_Agent0.2

# 安装依赖
pip install -r requirements.txt
```

### 2. 模型配置

#### 远程模型 (ModelScope)
```bash
# 设置API密钥
export MODELSCOPE_API_KEY="your_api_key_here"
```

#### 本地模型 (Ollama)
```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 启动Ollama服务
ollama serve

# 拉取模型
ollama pull qwen2.5:7b
ollama pull qwen2.5:14b
```

### 3. 依赖包安装

```bash
pip install sentence-transformers
pip install rich
pip install requests
pip install python-dotenv
pip install numpy
pip install scikit-learn
```

## 🚀 快速开始

### 1. 基础使用

```python
from Enhanced_Interactive_Multimodal_RAG_v2 import EnhancedRAGSystemV2

# 初始化系统
rag_system = EnhancedRAGSystemV2()

# 设置模型
rag_system.setup_model()

# 设置知识库
documents = ["path/to/document1.pdf", "path/to/document2.docx"]
rag_system.setup_knowledge_base(documents, source_type="path")

# 执行查询
result = rag_system.enhanced_query_v2(
    query="你的问题",
    retrieval_mode="智能检索"
)

print(result['final_answer'])
```

### 2. 模型选择示例

```python
from enhanced_llm_interface_v2 import EnhancedLLMInterfaceV2

# 初始化LLM接口
llm = EnhancedLLMInterfaceV2(api_key="your_api_key")

# 查看可用模型
models = llm.list_available_models()
print(models)

# 自动选择最佳模型
best_model = llm.auto_select_best_model()

# 手动设置模型
llm.set_model("qwen2.5-7b-local")  # 本地模型
# 或
llm.set_model("qwen2.5-72b")       # 远程模型

# 生成文本
result = llm.generate("你好，请介绍一下自己")
print(result.content)
```

### 3. 运行演示

```bash
# 完整功能演示
python demo_rag_v2.py

# 快速功能测试
python quick_test_v2.py

# 单元测试
python -m pytest test_rag_system_v2.py -v
```

## 🔧 配置选项

### 模型配置

在 `model_manager.py` 中可以配置：
- 模型列表和描述
- API端点和超时设置
- 默认参数 (max_tokens, temperature)

### 检索配置

在 `Enhanced_Interactive_Multimodal_RAG_v2.py` 中可以配置：
- 向量检索参数 (top_k, similarity_threshold)
- 文档分块大小和重叠
- 缓存设置

### 界面配置

在 `enhanced_user_interface_v2.py` 中可以配置：
- 界面主题和颜色
- 显示选项
- 交互方式

## 📊 性能监控

系统内置性能监控功能：

```python
# 获取性能统计
stats = rag_system.performance_monitor.get_performance_summary()
print(f"平均查询时间: {stats['average_query_time']:.2f}秒")
print(f"成功率: {stats['success_rate']:.1%}")

# 获取模型使用统计
model_stats = llm.get_generation_stats()
print(f"总请求数: {model_stats['total_requests']}")
print(f"平均响应时间: {model_stats['average_time']:.2f}秒")
```

## 🐛 故障排除

### 常见问题

1. **Ollama连接失败**
   ```bash
   # 检查Ollama服务状态
   ollama list
   
   # 重启Ollama服务
   ollama serve
   ```

2. **模型未安装**
   ```bash
   # 拉取所需模型
   ollama pull qwen2.5:7b
   ```

3. **API密钥问题**
   ```bash
   # 检查环境变量
   echo $MODELSCOPE_API_KEY
   
   # 设置环境变量
   export MODELSCOPE_API_KEY="your_key"
   ```

4. **依赖包问题**
   ```bash
   # 重新安装依赖
   pip install --upgrade -r requirements.txt
   ```

### 调试模式

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 启用性能监控
rag_system = EnhancedRAGSystemV2(enable_performance_monitoring=True)
```

## 🔄 版本更新

### V2.0 新特性
- ✅ 多端模型选择支持
- ✅ Ollama本地部署集成
- ✅ 增强的用户界面
- ✅ 智能模型自动选择
- ✅ 性能监控和统计
- ✅ 改进的错误处理

### 从V1升级
1. 更新代码文件
2. 安装新依赖包
3. 配置模型选择
4. 测试功能正常

## 📝 开发计划

### 短期计划
- [ ] 支持更多本地模型 (LLaMA, ChatGLM)
- [ ] 添加模型性能基准测试
- [ ] 优化内存使用和缓存策略
- [ ] 增加批量处理功能

### 长期计划
- [ ] 支持分布式部署
- [ ] 添加Web界面
- [ ] 集成更多向量数据库
- [ ] 支持实时学习和更新

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 参与讨论

---

**注意**: 本系统需要适当的硬件资源来运行本地模型，建议至少8GB内存和现代CPU。对于大型模型(14B+)，建议使用GPU加速。
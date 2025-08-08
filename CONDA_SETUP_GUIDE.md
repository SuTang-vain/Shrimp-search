# Conda环境设置指南

## 🎯 概述

为增强的交互式多模态RAG系统创建独立的Anaconda环境，确保所有依赖正确安装，避免版本冲突。

## 📋 环境信息

- **环境名称**: `enhanced_rag_system`
- **Python版本**: 3.10
- **主要依赖**: PyTorch, Transformers, CAMEL-AI, Sentence-Transformers
- **支持平台**: Windows, Linux, macOS

## 🚀 快速开始

### 方法1: 自动创建环境

```bash
# 运行自动创建脚本
python create_conda_environment.py
```

### 方法2: 手动创建环境

```bash
# 使用environment.yml创建环境
conda env create -f environment.yml

# 激活环境
conda activate enhanced_rag_system
```

## 📦 环境激活

### Windows系统
```cmd
# 命令行激活
conda activate enhanced_rag_system

# 或双击批处理文件
activate_env.bat
```

### Linux/macOS系统
```bash
# 命令行激活
conda activate enhanced_rag_system

# 或运行shell脚本
./activate_env.sh
```

## 🔧 环境验证

激活环境后运行测试：

```bash
# 快速功能测试
python quick_test_enhanced_features.py

# 系统完整测试
python demo_enhanced_features.py
```

## 📋 核心依赖包

### AI和机器学习
- `camel-ai>=0.1.0` - CAMEL框架
- `sentence-transformers>=2.2.0` - 句子嵌入
- `transformers>=4.20.0` - Hugging Face模型
- `torch>=1.12.0` - PyTorch深度学习框架

### 文档处理
- `pypdf>=3.0.0` - PDF处理
- `python-docx>=0.8.11` - Word文档
- `python-pptx>=0.6.21` - PowerPoint文档
- `openpyxl>=3.0.9` - Excel文档
- `PyMuPDF>=1.23.0` - 高级PDF处理

### 网络和爬虫
- `requests>=2.28.0` - HTTP请求
- `beautifulsoup4>=4.11.0` - HTML解析
- `selenium>=4.0.0` - 浏览器自动化

### 用户界面
- `rich>=12.0.0` - 美化终端输出
- `colorama>=0.4.4` - 跨平台颜色支持

### 向量数据库
- `qdrant-client>=1.0.0` - Qdrant向量数据库
- `chromadb>=0.4.0` - ChromaDB向量数据库

## ⚠️ 常见问题

### 1. 环境创建失败
```bash
# 清理conda缓存
conda clean --all

# 更新conda
conda update conda

# 重新创建环境
conda env remove -n enhanced_rag_system
python create_conda_environment.py
```

### 2. 包安装失败
```bash
# 使用conda-forge频道
conda install -c conda-forge package_name

# 或使用pip安装
pip install package_name
```

### 3. CUDA支持问题
```bash
# 检查CUDA版本
nvidia-smi

# 安装对应的PyTorch版本
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
```

### 4. 内存不足
```bash
# 设置conda并发下载数
conda config --set default_threads 1

# 或分批安装包
pip install --no-cache-dir package_name
```

## 🔍 环境管理

### 查看环境列表
```bash
conda env list
```

### 导出环境配置
```bash
conda env export -n enhanced_rag_system > my_environment.yml
```

### 更新环境
```bash
conda env update -f environment.yml --prune
```

### 删除环境
```bash
conda env remove -n enhanced_rag_system
```

## 📊 性能优化

### 1. 设置环境变量
```bash
# 设置PyTorch线程数
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4

# 设置CUDA设备
export CUDA_VISIBLE_DEVICES=0
```

### 2. 配置pip镜像源
```bash
# 使用清华镜像源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 配置conda镜像源
```bash
# 添加清华镜像源
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/pro
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2
```

## 🎮 使用示例

### 启动主程序
```bash
# 激活环境
conda activate enhanced_rag_system

# 启动系统
python Enhanced_Interactive_Multimodal_RAG.py
```

### 运行演示
```bash
# 功能演示
python demo_enhanced_features.py

# 文档管理演示
python demo_document_management.py
```

### 快速测试
```bash
# 运行所有测试
python quick_test_enhanced_features.py

# 单独测试某个功能
python -c "from quick_test_enhanced_features import test_document_manager; test_document_manager()"
```

## 📝 注意事项

1. **首次运行**: 可能需要下载大型模型文件（如sentence-transformers模型）
2. **API密钥**: 确保`.env`文件中配置了正确的API密钥
3. **网络连接**: 某些功能需要稳定的网络连接
4. **系统资源**: 建议至少8GB RAM和2GB可用磁盘空间
5. **权限问题**: 在某些系统上可能需要管理员权限

## 🆘 获取帮助

如果遇到问题，请：

1. 检查错误日志
2. 查看[ENHANCED_FEATURES_SUMMARY.md](ENHANCED_FEATURES_SUMMARY.md)
3. 运行系统诊断：`python quick_test_enhanced_features.py`
4. 重新创建环境：`python create_conda_environment.py`

## 🎉 完成

环境设置完成后，您就可以享受增强的RAG系统带来的强大功能了！

- 📚 智能文档处理和缓存
- 🔄 增量文档更新
- 📄 13种文档格式支持
- 🚀 高性能向量检索
- 🎨 美观的用户界面
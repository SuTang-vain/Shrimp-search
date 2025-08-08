# Shrimp Agent v1.0 启动指南

## 版本信息
- **版本名称**: Shrimp_Agent1.0
- **系统类型**: 智能多模态RAG系统
- **架构**: 前后端分离架构
- **开发团队**: Shrimp Agent Team

## 系统概述

Shrimp Agent v1.0 是一个基于RAG（检索增强生成）技术的智能多模态系统，支持文档处理、知识检索、智能问答等功能。系统采用前后端分离架构，提供Web界面和API接口。

## 系统要求

### 环境依赖
- **Python**: 3.8+
- **Conda**: 推荐使用Anaconda或Miniconda
- **操作系统**: Windows 10/11
- **内存**: 建议8GB以上
- **存储**: 至少5GB可用空间

### 必需组件
- Flask (后端API框架)
- 各种AI模型依赖包
- 前端静态文件服务器

## 快速启动

### 方法一：使用启动脚本（推荐）

1. **双击运行启动文件**
   ```
   start_shrimp_agent_v1.0.bat
   ```

2. **等待系统启动**
   - 系统会自动清理现有Python进程
   - 依次启动API服务器（5000端口）
   - 启动前端服务器（8080端口）
   - 自动打开浏览器访问系统

### 方法二：手动启动

1. **启动API服务器**
   ```bash
   python api_server_v2.py
   ```

2. **启动前端服务器**
   ```bash
   python frontend/server.py
   ```

## 启动文件功能特性

### 核心功能
- ✅ **自动进程清理**: 启动前自动停止现有Python进程
- ✅ **顺序启动**: 按照依赖关系依次启动后端和前端服务
- ✅ **状态监控**: 实时显示启动进度和状态信息
- ✅ **错误处理**: 启动失败时提供错误信息和处理建议
- ✅ **自动打开浏览器**: 启动完成后自动打开系统界面
- ✅ **用户友好界面**: 提供清晰的启动日志和操作提示

### 启动流程
1. **[1/4] 进程清理**: 停止现有Python进程，避免端口冲突
2. **[2/4] 等待缓冲**: 等待3秒确保进程完全停止
3. **[3/4] 启动后端**: 启动API服务器，监听5000端口
4. **[4/4] 启动前端**: 启动前端服务器，监听8080端口

## 端口配置

| 服务 | 端口 | 用途 | 访问地址 |
|------|------|------|----------|
| API服务器 | 5000 | 后端API接口 | http://localhost:5000 |
| 前端服务器 | 8080 | Web界面 | http://localhost:8080 |

## 系统架构

```
┌─────────────────┐    HTTP请求    ┌─────────────────┐
│   前端服务器     │ ──────────────→ │   API服务器      │
│  (Port: 8080)   │                │  (Port: 5000)   │
│                 │ ←────────────── │                 │
│  - 静态文件服务  │    JSON响应     │  - RAG处理      │
│  - 用户界面     │                │  - 文档管理     │
│  - 文件上传     │                │  - 模型调用     │
└─────────────────┘                └─────────────────┘
```

## 主要功能模块

### 后端API服务器 (api_server_v2.py)
- **健康检查**: `/api/health` - 系统状态检查
- **模型管理**: `/api/models` - 获取可用AI模型列表
- **智能搜索**: `/api/search` - 执行RAG检索和问答
- **进度跟踪**: `/api/search/<id>/progress` - 查询搜索进度
- **结果获取**: `/api/search/<id>/results` - 获取搜索结果
- **文件上传**: `/api/upload` - 上传文档到知识库
- **系统统计**: `/api/stats` - 获取系统运行统计

### 前端服务器 (frontend/server.py)
- **静态文件服务**: 提供HTML、CSS、JS文件
- **CORS支持**: 支持跨域请求
- **自动打开浏览器**: 启动后自动打开系统界面
- **端口检查**: 自动检测端口占用情况

## 故障排除

### 常见问题

#### 1. 端口被占用
**现象**: 启动时提示端口5000或8080被占用

**解决方案**:
```bash
# 查看端口占用
netstat -ano | findstr :5000
netstat -ano | findstr :8080

# 结束占用进程
taskkill /f /pid <进程ID>
```

#### 2. Python环境问题
**现象**: 提示找不到Python或模块导入错误

**解决方案**:
```bash
# 激活conda环境
conda activate enhanced_rag_system

# 安装依赖
pip install -r requirements.txt
```

#### 3. API服务器启动失败
**现象**: API服务器无法启动或返回500错误

**解决方案**:
- 检查.env文件配置
- 确认AI模型文件存在
- 查看终端错误日志
- 检查知识库初始化状态

#### 4. 前端无法访问后端
**现象**: 前端页面显示API连接错误

**解决方案**:
- 确认API服务器正在运行
- 检查防火墙设置
- 验证端口配置是否正确
- 查看浏览器控制台错误信息

### 日志查看

启动后会打开两个终端窗口：
- **API服务器终端**: 显示后端运行日志和错误信息
- **前端服务器终端**: 显示前端访问日志

### 系统检查命令

```bash
# 检查系统健康状态
python system_health_check.py

# 快速配置检查
python quick_config_check.py

# 验证系统功能
python final_verification.py
```

## 配置说明

### 环境变量配置 (.env)
```env
# AI模型配置
OLLAMA_HOST=http://localhost:11434
OPENAI_API_KEY=your_openai_key

# 系统配置
DEBUG=False
LOG_LEVEL=INFO
```

### 模型配置
系统支持多种AI模型：
- **本地模型**: qwen2.5-7b, qwen2.5-14b, glm4.5
- **远程模型**: OpenAI GPT系列
- **优先级**: 系统会按优先级自动选择可用模型

## 开发和调试

### 开发模式启动
```bash
# 启动API服务器（调试模式）
python api_server_v2.py --debug

# 启动前端服务器（开发模式）
python frontend/server.py --dev
```

### 测试命令
```bash
# 运行系统测试
python test_rag_system_v2.py

# 快速功能测试
python quick_test_v2.py

# API接口测试
python final_integration_test.py
```

## 性能优化建议

1. **内存优化**: 建议分配至少8GB内存给系统
2. **存储优化**: 使用SSD存储提高文档检索速度
3. **网络优化**: 确保网络连接稳定，特别是使用远程模型时
4. **模型选择**: 根据硬件配置选择合适的AI模型

## 更新和维护

### 版本更新
```bash
# 备份当前配置
cp .env .env.backup

# 更新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade
```

### 数据备份
- **知识库**: 定期备份 `document_cache/` 目录
- **上传文件**: 备份 `uploaded_documents/` 目录
- **配置文件**: 备份 `.env` 文件

## 技术支持

### 联系方式
- **项目地址**: https://github.com/shrimp-agent
- **问题反馈**: 通过GitHub Issues提交
- **文档更新**: 查看项目Wiki页面

### 社区资源
- **用户手册**: 详细的功能使用说明
- **开发文档**: API接口和架构说明
- **常见问题**: FAQ和解决方案集合

---

**感谢使用 Shrimp Agent v1.0！**

如有任何问题，请参考本文档或联系技术支持团队。
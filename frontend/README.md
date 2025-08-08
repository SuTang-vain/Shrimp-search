# Shrimp Search 前端界面

基于您的Shrimp Agent项目创建的现代化前端界面，采用棕红色/白色主题设计。

## 功能特性

### 🎨 界面设计
- **主题色彩**: 棕红色(#B85450)为主色调，白色为背景，黑色为文字
- **字体**: 标题使用Orbitron非常规英文字体，正文使用微软雅黑
- **响应式设计**: 支持桌面端和移动端适配

### 🔍 搜索功能
- **多模型支持**: GLM-4、Ollama、OpenAI模型选择
- **多检索模式**: 
  - 快速检索: 基础向量检索
  - 深度检索: 查询重写+HyDE+RRF融合
  - 主题检索: PDF+网页综合分析
  - 智能检索: 自适应选择最佳策略
- **语音输入**: 支持语音转文字搜索
- **实时搜索过程**: 可视化显示搜索步骤

### 📱 界面布局

#### 主页面
- **右侧导航**: Chat/Task/History三个标签
- **中央标题**: "Shrimp Search" 使用特殊字体
- **搜索栏**: 主搜索输入框，支持语音输入
- **选择器**: 模型选择和检索模式选择
- **快捷功能**: 上传文档、图像分析、最新资讯、设置

#### 搜索结果页面
- **左侧**: 可折叠的历史记录面板
- **中间**: 实时搜索过程显示
- **右侧**: 搜索结果输出和继续对话

### 🚀 快速开始

#### 方法1: 使用Python服务器
```bash
cd frontend
python server.py
```

#### 方法2: 使用Node.js服务器
```bash
cd frontend
npx http-server -p 8080 -o
```

#### 方法3: 直接打开文件
在浏览器中直接打开 `index.html` 文件

### 📁 文件结构
```
frontend/
├── index.html          # 主HTML文件
├── styles.css          # CSS样式文件
├── script.js           # JavaScript交互脚本
├── server.py           # Python开发服务器
└── README.md           # 说明文档
```

### 🎯 主要功能

#### 搜索功能
- 输入查询内容
- 选择AI模型(GLM-4/Ollama/OpenAI)
- 选择检索模式(快速/深度/主题/智能)
- 点击搜索或按回车键执行

#### 文档上传
- 点击"上传文档"按钮
- 支持拖拽上传
- 支持多文件上传
- 支持PDF、DOC、DOCX、TXT、MD格式

#### 历史记录
- 自动保存搜索历史
- 按日期分组显示
- 点击历史记录可重新搜索
- 支持侧边栏折叠

#### 语音输入
- 点击麦克风图标
- 支持中文语音识别
- 自动填入搜索框

### 🔧 技术特性

#### 前端技术
- **HTML5**: 语义化标签，无障碍访问
- **CSS3**: Flexbox/Grid布局，CSS变量，动画效果
- **JavaScript ES6+**: 模块化设计，异步处理
- **响应式设计**: 移动端适配

#### 浏览器兼容性
- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

#### 本地存储
- 使用localStorage保存搜索历史
- 自动清理过期数据
- 支持数据导出

### 🎨 设计规范

#### 颜色规范
```css
--primary-color: #B85450;      /* 主色调-棕红色 */
--primary-dark: #9A4A46;       /* 深色调 */
--primary-light: #D4706C;      /* 浅色调 */
--secondary-color: #FFFFFF;     /* 白色背景 */
--text-color: #000000;         /* 黑色文字 */
--text-secondary: #666666;     /* 灰色辅助文字 */
```

#### 字体规范
- **标题**: Orbitron (非常规英文字体)
- **正文**: Arial, Microsoft YaHei (中英文混合)
- **代码**: Monaco, Consolas (等宽字体)

#### 间距规范
- **基础间距**: 8px的倍数
- **组件间距**: 16px, 24px, 32px
- **页面边距**: 32px, 48px

### 🔌 后端集成

前端设计为与您的Python后端系统集成：

#### API接口设计
```javascript
// 搜索接口
POST /api/search
{
    "query": "用户查询",
    "model": "glm-4",
    "mode": "深度检索",
    "settings": {
        "max_tokens": 800,
        "temperature": 0.7
    }
}

// 文档上传接口
POST /api/upload
FormData: files[]

// 历史记录接口
GET /api/history
POST /api/history (保存)
```

#### WebSocket支持
```javascript
// 实时搜索过程
ws://localhost:8080/ws/search
{
    "type": "search_progress",
    "step": "step-1",
    "status": "正在分析查询..."
}
```

### 📱 移动端适配

#### 响应式断点
- **桌面端**: > 1200px
- **平板端**: 768px - 1200px  
- **手机端**: < 768px

#### 移动端优化
- 触摸友好的按钮尺寸
- 侧边栏自动折叠
- 简化的导航界面
- 优化的输入体验

### 🚀 部署建议

#### 开发环境
```bash
# 使用Python服务器
python frontend/server.py

# 或使用Node.js
cd frontend && npx http-server
```

#### 生产环境
- 使用Nginx作为静态文件服务器
- 配置HTTPS证书
- 启用Gzip压缩
- 配置缓存策略

### 🔍 调试和测试

#### 浏览器开发者工具
- Console: 查看JavaScript错误和日志
- Network: 监控API请求
- Elements: 调试CSS样式
- Application: 检查localStorage数据

#### 测试功能
- 搜索功能测试
- 文件上传测试
- 响应式布局测试
- 语音输入测试

### 📝 更新日志

#### v1.0.0 (2024-01-XX)
- ✅ 基础界面设计完成
- ✅ 搜索功能实现
- ✅ 历史记录功能
- ✅ 文件上传功能
- ✅ 响应式设计
- ✅ 语音输入支持

### 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

### 📞 技术支持

如果您在使用过程中遇到问题，请：

1. 查看浏览器控制台错误信息
2. 检查网络连接和API配置
3. 确认浏览器版本兼容性
4. 提交Issue到项目仓库

### 🔮 未来规划

#### 即将推出的功能
- [ ] 多语言支持 (英文/中文切换)
- [ ] 深色模式主题
- [ ] 更多AI模型集成
- [ ] 高级搜索过滤器
- [ ] 搜索结果导出为PDF
- [ ] 用户偏好设置保存
- [ ] 搜索结果分享功能增强

#### 性能优化
- [ ] 虚拟滚动优化长列表
- [ ] 图片懒加载
- [ ] 代码分割和按需加载
- [ ] Service Worker缓存策略

### 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](../LICENSE) 文件了解详情

### 🙏 致谢

- 感谢所有为Shrimp Agent项目贡献的开发者
- 特别感谢提供设计灵感的参考界面
- 感谢开源社区提供的优秀工具和库

---

**Shrimp Search** - 让AI搜索更智能，让知识获取更简单 🦐✨

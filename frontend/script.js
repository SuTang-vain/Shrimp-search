// Shrimp Search 前端交互脚本
class ShrimpSearch {
    constructor() {
        this.currentPage = 'main';
        this.searchHistory = this.loadSearchHistory();
        this.currentQuery = '';
        this.isSearching = false;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadHistoryItems();
        this.updateNavigation();
        
        // 初始化时检查API服务器状态
        this.checkApiHealth();
        
        // 加载可用模型列表
        this.loadAvailableModels();
    }
    
    bindEvents() {
        // 搜索相关事件
        document.getElementById('search-btn').addEventListener('click', () => this.performSearch());
        document.getElementById('search-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.performSearch();
        });
        
        // 语音输入
        document.getElementById('voice-btn').addEventListener('click', () => this.startVoiceInput());
        
        // 导航事件
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => this.handleNavigation(e));
        });
        
        // 返回主页
        document.getElementById('back-to-main').addEventListener('click', () => this.showMainPage());
        
        // 侧边栏切换
        document.getElementById('toggle-sidebar').addEventListener('click', () => this.toggleSidebar());
        
        // 快捷功能
        console.log('绑定快捷功能按钮事件');
        const actionBtns = document.querySelectorAll('.action-btn');
        console.log('找到快捷功能按钮数量:', actionBtns.length);
        actionBtns.forEach((btn, index) => {
            console.log(`绑定按钮 ${index + 1}:`, btn.dataset.action);
            btn.addEventListener('click', (e) => {
                console.log('快捷功能按钮被点击:', e.currentTarget.dataset.action);
                this.handleQuickAction(e);
            });
        });
        
        // 继续提问
        document.getElementById('send-follow-up').addEventListener('click', () => this.sendFollowUp());
        document.getElementById('follow-up-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendFollowUp();
        });
        
        // 模态框事件
        document.getElementById('close-document-modal').addEventListener('click', () => this.closeModal('document-management-modal'));
        
        // 文件上传
        document.getElementById('upload-area').addEventListener('click', () => {
            document.getElementById('file-input').click();
        });
        
        document.getElementById('file-input').addEventListener('change', (e) => this.handleFileUpload(e));
        
        // 拖拽上传
        const uploadArea = document.getElementById('upload-area');
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = 'var(--primary-color)';
            uploadArea.style.background = 'var(--background-light)';
        });
        
        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = 'var(--border-color)';
            uploadArea.style.background = 'transparent';
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = 'var(--border-color)';
            uploadArea.style.background = 'transparent';
            this.handleFileDrop(e);
        });
        
        // 结果操作
        document.getElementById('export-btn').addEventListener('click', () => this.exportResults());
        document.getElementById('share-btn').addEventListener('click', () => this.shareResults());
        
        // 文档管理相关事件
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.currentTarget.dataset.tab));
        });
        
        // 刷新文档列表按钮
        document.getElementById('refresh-documents').addEventListener('click', () => this.loadDocuments());
    }
    
    async performSearch() {
        const query = document.getElementById('search-input').value.trim();
        if (!query || this.isSearching) return;
        
        this.currentQuery = query;
        this.isSearching = true;
        
        // 切换到搜索页面
        this.showSearchPage();
        
        // 更新查询显示
        document.getElementById('current-query').textContent = query;
        
        // 添加到历史记录
        this.addToHistory(query);
        
        // 开始真实搜索流程
        await this.startRealSearchProcess();
    }
    
    async startRealSearchProcess() {
        try {
            // 获取选择的模型和搜索模式
            const selectedModel = document.getElementById('model-select').value;
            const selectedMode = document.getElementById('search-mode').value;
            
            // 重置搜索步骤显示
            this.resetSearchSteps();
            
            // 开始搜索请求
            const searchData = {
                query: this.currentQuery,
                model: selectedModel,
                mode: selectedMode,
                max_results: 5
            };
            
            console.log('发起搜索请求:', searchData);
            
            const response = await fetch('http://localhost:5000/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(searchData)
            });
            
            if (!response.ok) {
                throw new Error(`搜索请求失败: ${response.status} ${response.statusText}`);
            }
            
            const result = await response.json();
            console.log('搜索响应:', result);
            
            if (result.success) {
                // 开始监控搜索进度
                this.monitorSearchProgress(result.search_id);
            } else {
                throw new Error(result.error || '搜索请求失败');
            }
            
        } catch (error) {
            console.error('搜索过程出错:', error);
            this.handleSearchError(error);
        }
    }
    
    async monitorSearchProgress(searchId) {
        const maxAttempts = 120; // 最多监控2分钟
        let attempts = 0;
        
        const checkProgress = async () => {
            try {
                attempts++;
                
                const response = await fetch(`http://localhost:5000/api/search/${searchId}/progress`);
                if (!response.ok) {
                    throw new Error(`获取进度失败: ${response.status}`);
                }
                
                const progress = await response.json();
                console.log('搜索进度:', progress);
                
                // 更新进度显示
                this.updateSearchProgress(progress);
                
                if (progress.status === 'completed') {
                    // 搜索完成，获取结果
                    await this.getSearchResults(searchId);
                    return;
                } else if (progress.status === 'failed') {
                    throw new Error(progress.error || '搜索失败');
                } else if (attempts >= maxAttempts) {
                    throw new Error('搜索超时');
                } else {
                    // 继续监控
                    setTimeout(checkProgress, 1000);
                }
                
            } catch (error) {
                console.error('监控进度出错:', error);
                this.handleSearchError(error);
            }
        };
        
        // 开始监控
        checkProgress();
    }
    
    async getSearchResults(searchId) {
        try {
            const response = await fetch(`http://localhost:5000/api/search/${searchId}/results`);
            if (!response.ok) {
                throw new Error(`获取结果失败: ${response.status}`);
            }
            
            const results = await response.json();
            console.log('搜索结果:', results);
            
            if (results.success) {
                this.displaySearchResults(results.data);
            } else {
                throw new Error(results.error || '获取结果失败');
            }
            
        } catch (error) {
            console.error('获取结果出错:', error);
            this.handleSearchError(error);
        }
    }
    
    resetSearchSteps() {
        const steps = ['step-1', 'step-2', 'step-3', 'step-4'];
        steps.forEach(stepId => {
            const step = document.getElementById(stepId);
            step.classList.remove('active', 'completed');
        });
        
        // 重置结果显示
        document.getElementById('results-content').innerHTML = `
            <div class="result-placeholder">
                <i class="fas fa-hourglass-half"></i>
                <p>正在为您搜索相关信息...</p>
            </div>
        `;
    }
    
    updateSearchProgress(progress) {
        const steps = ['step-1', 'step-2', 'step-3', 'step-4'];
        const stepTexts = [
            '解析用户意图...',
            '搜索知识库...',
            '获取最新信息...',
            '生成回答...'
        ];
        
        // 根据进度状态更新步骤显示
        let currentStepIndex = 0;
        
        if (progress.current_step) {
            switch (progress.current_step) {
                case 'parsing':
                    currentStepIndex = 0;
                    break;
                case 'searching':
                    currentStepIndex = 1;
                    break;
                case 'retrieving':
                    currentStepIndex = 2;
                    break;
                case 'generating':
                    currentStepIndex = 3;
                    break;
            }
        }
        
        // 更新步骤状态
        steps.forEach((stepId, index) => {
            const step = document.getElementById(stepId);
            const statusElement = step.querySelector('.step-status');
            
            if (index < currentStepIndex) {
                step.classList.remove('active');
                step.classList.add('completed');
                statusElement.textContent = '已完成';
            } else if (index === currentStepIndex) {
                step.classList.add('active');
                step.classList.remove('completed');
                statusElement.textContent = progress.message || stepTexts[index];
            } else {
                step.classList.remove('active', 'completed');
                statusElement.textContent = stepTexts[index];
            }
        });
    }
    
    displaySearchResults(results) {
        this.isSearching = false;
        
        const resultsContent = document.getElementById('results-content');
        let html = '';
        
        if (results.answer) {
            html += `
                <div class="result-item">
                    <h4>AI回答</h4>
                    <div class="result-content">${this.formatAnswer(results.answer)}</div>
                    <div class="result-source">
                        模型：${results.model || '未知'} | 
                        模式：${results.mode || '未知'} | 
                        用时：${results.processing_time || '未知'}秒
                    </div>
                </div>
            `;
        }
        
        if (results.sources && results.sources.length > 0) {
            html += `
                <div class="result-item">
                    <h4>相关文档 (${results.sources.length}个)</h4>
                    <div class="sources-list">
            `;
            
            results.sources.forEach((source, index) => {
                html += `
                    <div class="source-item">
                        <div class="source-title">${source.title || `文档 ${index + 1}`}</div>
                        <div class="source-content">${this.truncateText(source.content, 200)}</div>
                        <div class="source-meta">
                            相似度: ${(source.similarity * 100).toFixed(1)}% | 
                            来源: ${source.source || '知识库'}
                        </div>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
        
        if (results.web_results && results.web_results.length > 0) {
            html += `
                <div class="result-item">
                    <h4>网络搜索结果 (${results.web_results.length}个)</h4>
                    <div class="web-results-list">
            `;
            
            results.web_results.forEach(webResult => {
                html += `
                    <div class="web-result-item">
                        <div class="web-result-title">
                            <a href="${webResult.url}" target="_blank">${webResult.title}</a>
                        </div>
                        <div class="web-result-snippet">${webResult.snippet}</div>
                        <div class="web-result-url">${webResult.url}</div>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
        
        if (!html) {
            html = `
                <div class="result-item">
                    <h4>搜索完成</h4>
                    <p>抱歉，没有找到相关的结果。请尝试使用不同的关键词或搜索模式。</p>
                </div>
            `;
        }
        
        resultsContent.innerHTML = html;
        
        // 标记所有步骤为完成
        const steps = ['step-1', 'step-2', 'step-3', 'step-4'];
        steps.forEach(stepId => {
            const step = document.getElementById(stepId);
            step.classList.remove('active');
            step.classList.add('completed');
            step.querySelector('.step-status').textContent = '已完成';
        });
    }
    
    handleSearchError(error) {
        this.isSearching = false;
        
        console.error('搜索错误:', error);
        
        const resultsContent = document.getElementById('results-content');
        resultsContent.innerHTML = `
            <div class="result-item error">
                <h4><i class="fas fa-exclamation-triangle"></i> 搜索出错</h4>
                <p><strong>错误信息：</strong>${error.message}</p>
                <p><strong>可能的原因：</strong></p>
                <ul>
                    <li>后端服务未启动 (请确保 api_server.py 正在运行)</li>
                    <li>网络连接问题</li>
                    <li>服务器内部错误</li>
                    <li>请求参数错误</li>
                </ul>
                <p><strong>解决建议：</strong></p>
                <ul>
                    <li>检查后端服务状态</li>
                    <li>查看浏览器控制台错误信息</li>
                    <li>尝试刷新页面重新搜索</li>
                </ul>
                <button onclick="location.reload()" class="retry-btn">刷新页面重试</button>
            </div>
        `;
        
        // 重置所有步骤
        const steps = ['step-1', 'step-2', 'step-3', 'step-4'];
        steps.forEach(stepId => {
            const step = document.getElementById(stepId);
            step.classList.remove('active', 'completed');
            step.querySelector('.step-status').textContent = '等待开始';
        });
    }
    
    formatAnswer(answer) {
        // 简单的文本格式化
        return answer
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^/, '<p>')
            .replace(/$/, '</p>');
    }
    
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
    
    // 检查API服务器状态
    async checkApiHealth() {
        try {
            const response = await fetch('http://localhost:5000/api/health');
            const health = await response.json();
            console.log('API服务器状态:', health);
            return health.status === 'healthy';
        } catch (error) {
            console.error('API服务器连接失败:', error);
            return false;
        }
    }
    
    // 获取可用模型列表
    async loadAvailableModels() {
        try {
            const response = await fetch('http://localhost:5000/api/models');
            if (response.ok) {
                const models = await response.json();
                this.updateModelSelect(models.data);
            }
        } catch (error) {
            console.error('获取模型列表失败:', error);
        }
    }
    
    updateModelSelect(models) {
        const modelSelect = document.getElementById('model-select');
        modelSelect.innerHTML = '';
        
        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model.id;
            option.textContent = model.name;
            if (model.default) {
                option.selected = true;
            }
            modelSelect.appendChild(option);
        });
    }
    
    showSearchPage() {
        document.getElementById('main-page').classList.remove('active');
        document.getElementById('search-page').classList.add('active');
        this.currentPage = 'search';
        this.updateNavigation();
    }
    
    showMainPage() {
        document.getElementById('search-page').classList.remove('active');
        document.getElementById('main-page').classList.add('active');
        this.currentPage = 'main';
        this.updateNavigation();
        
        // 重置搜索状态
        this.resetSearchState();
    }
    
    resetSearchState() {
        this.isSearching = false;
        this.currentQuery = '';
        
        // 重置步骤状态
        const steps = ['step-1', 'step-2', 'step-3', 'step-4'];
        steps.forEach(stepId => {
            const step = document.getElementById(stepId);
            step.classList.remove('active', 'completed');
        });
        
        // 重置结果显示
        document.getElementById('results-content').innerHTML = `
            <div class="result-placeholder">
                <i class="fas fa-hourglass-half"></i>
                <p>正在为您搜索相关信息...</p>
            </div>
        `;
        
        // 清空输入框
        document.getElementById('search-input').value = '';
        document.getElementById('follow-up-input').value = '';
    }
    
    handleNavigation(e) {
        const tab = e.currentTarget.dataset.tab;
        
        // 更新导航状态
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        e.currentTarget.classList.add('active');
        
        // 这里可以添加不同标签页的逻辑
        console.log(`切换到标签页: ${tab}`);
    }
    
    updateNavigation() {
        // 根据当前页面更新导航状态
        const chatTab = document.querySelector('[data-tab="chat"]');
        if (this.currentPage === 'main') {
            chatTab.classList.add('active');
        }
    }
    
    toggleSidebar() {
        const sidebar = document.getElementById('history-sidebar');
        sidebar.classList.toggle('collapsed');
    }
    
    handleQuickAction(e) {
        const action = e.currentTarget.dataset.action;
        console.log('handleQuickAction called with action:', action);
        
        switch(action) {
            case 'document-management':
                console.log('调用 showDocumentManagement');
                this.showDocumentManagement();
                break;
            case 'image':
                this.showImageAnalysis();
                break;
            case 'latest':
                this.showLatestNews();
                break;
            case 'settings':
                this.showSettings();
                break;
        }
    }
    
    showModal(modalId) {
        console.log('showModal 被调用，modalId:', modalId);
        const modal = document.getElementById(modalId);
        console.log('找到模态框元素:', !!modal);
        if (modal) {
            modal.classList.add('active');
            console.log('模态框类名:', modal.className);
        } else {
            console.error('未找到模态框元素:', modalId);
        }
    }
    
    closeModal(modalId) {
        document.getElementById(modalId).classList.remove('active');
    }
    
    handleFileUpload(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.uploadFiles(files);
        }
    }
    
    handleFileDrop(e) {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.uploadFiles(files);
        }
    }
    
    async uploadFiles(files) {
        const progressElement = document.getElementById('upload-progress');
        const progressFill = progressElement.querySelector('.progress-fill');
        const progressText = progressElement.querySelector('.progress-text');
        
        progressElement.style.display = 'block';
        
        try {
            const formData = new FormData();
            Array.from(files).forEach(file => {
                formData.append('files', file);
            });
            
            const response = await fetch('http://localhost:5000/api/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`上传失败: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                progressFill.style.width = '100%';
                progressText.textContent = '上传完成！';
                
                setTimeout(() => {
                    progressElement.style.display = 'none';
                    progressFill.style.width = '0%';
                    progressText.textContent = '上传中...';
                    
                    // 显示上传成功消息
                    alert(`成功上传 ${result.uploaded_files.length} 个文件`);
                    
                    // 切换到文档列表选项卡并刷新
                    this.switchTab('list');
                }, 1000);
            } else {
                throw new Error(result.error || '上传失败');
            }
            
        } catch (error) {
            console.error('文件上传错误:', error);
            progressText.textContent = '上传失败！';
            progressFill.style.backgroundColor = '#ff4444';
            
            setTimeout(() => {
                progressElement.style.display = 'none';
                progressFill.style.width = '0%';
                progressFill.style.backgroundColor = '';
                progressText.textContent = '上传中...';
            }, 2000);
            
            alert(`上传失败: ${error.message}`);
        }
    }
    
    async sendFollowUp() {
        const input = document.getElementById('follow-up-input');
        const query = input.value.trim();
        
        if (!query) return;
        
        // 添加用户消息到结果区域
        const resultsContent = document.getElementById('results-content');
        const userMessage = document.createElement('div');
        userMessage.className = 'result-item';
        userMessage.innerHTML = `
            <h4>继续提问</h4>
            <p><strong>您：</strong>${query}</p>
        `;
        resultsContent.appendChild(userMessage);
        
        // 添加到历史记录
        this.addToHistory(query);
        
        // 清空输入框
        input.value = '';
        
        // 发起真实的追问请求
        try {
            const response = await fetch('http://localhost:5000/api/followup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    context: this.currentQuery
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    const aiResponse = document.createElement('div');
                    aiResponse.className = 'result-item';
                    aiResponse.innerHTML = `
                        <h4>AI回复</h4>
                        <div class="result-content">${this.formatAnswer(result.answer)}</div>
                        <div class="result-source">来源：AI助手</div>
                    `;
                    resultsContent.appendChild(aiResponse);
                } else {
                    throw new Error(result.error);
                }
            } else {
                throw new Error('追问请求失败');
            }
        } catch (error) {
            console.error('追问失败:', error);
            const errorResponse = document.createElement('div');
            errorResponse.className = 'result-item error';
            errorResponse.innerHTML = `
                <h4>追问失败</h4>
                <p>抱歉，无法处理您的追问。错误信息：${error.message}</p>
            `;
            resultsContent.appendChild(errorResponse);
        }
        
        resultsContent.scrollTop = resultsContent.scrollHeight;
    }
    
    addToHistory(query) {
        const historyItem = {
            id: Date.now(),
            query: query,
            timestamp: new Date(),
            preview: query.length > 50 ? query.substring(0, 50) + '...' : query
        };
        
        this.searchHistory.unshift(historyItem);
        
        // 限制历史记录数量
        if (this.searchHistory.length > 50) {
            this.searchHistory = this.searchHistory.slice(0, 50);
        }
        
        this.saveSearchHistory();
        this.loadHistoryItems();
    }
    
    loadHistoryItems() {
        const todayHistory = document.getElementById('today-history');
        const yesterdayHistory = document.getElementById('yesterday-history');
        
        todayHistory.innerHTML = '';
        yesterdayHistory.innerHTML = '';
        
        const today = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        
        this.searchHistory.forEach(item => {
            const itemDate = new Date(item.timestamp);
            const historyElement = this.createHistoryElement(item);
            
            if (this.isSameDay(itemDate, today)) {
                todayHistory.appendChild(historyElement);
            } else if (this.isSameDay(itemDate, yesterday)) {
                yesterdayHistory.appendChild(historyElement);
            }
        });
    }
    
    createHistoryElement(item) {
        const element = document.createElement('div');
        element.className = 'history-item';
        element.innerHTML = `
            <div class="history-item-title">${item.query}</div>
            <div class="history-item-preview">${this.formatTime(item.timestamp)}</div>
        `;
        
        element.addEventListener('click', () => {
            document.getElementById('search-input').value = item.query;
            if (this.currentPage === 'search') {
                this.performSearch();
            }
        });
        
        return element;
    }
    
    isSameDay(date1, date2) {
        return date1.getFullYear() === date2.getFullYear() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getDate() === date2.getDate();
    }
    
    formatTime(date) {
        return new Date(date).toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    loadSearchHistory() {
        try {
            const history = localStorage.getItem('shrimpSearchHistory');
            return history ? JSON.parse(history) : [];
        } catch (e) {
            console.error('加载搜索历史失败:', e);
            return [];
        }
    }
    
    saveSearchHistory() {
        try {
            localStorage.setItem('shrimpSearchHistory', JSON.stringify(this.searchHistory));
        } catch (e) {
            console.error('保存搜索历史失败:', e);
        }
    }
    
    startVoiceInput() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('您的浏览器不支持语音识别功能');
            return;
        }
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.lang = 'zh-CN';
        recognition.continuous = false;
        recognition.interimResults = false;
        
        const voiceBtn = document.getElementById('voice-btn');
        const originalIcon = voiceBtn.innerHTML;
        
        voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
        voiceBtn.style.color = 'var(--primary-color)';
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            document.getElementById('search-input').value = transcript;
        };
        
        recognition.onerror = (event) => {
            console.error('语音识别错误:', event.error);
            alert('语音识别失败，请重试');
        };
        
        recognition.onend = () => {
            voiceBtn.innerHTML = originalIcon;
            voiceBtn.style.color = '';
        };
        
        recognition.start();
    }
    
    showImageAnalysis() {
        alert('图像分析功能开发中...');
    }
    
    showLatestNews() {
        alert('最新资讯功能开发中...');
    }
    
    showSettings() {
        alert('设置功能开发中...');
    }
    
    exportResults() {
        const resultsContent = document.getElementById('results-content');
        const content = resultsContent.innerText;
        
        const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `搜索结果_${new Date().toISOString().slice(0, 10)}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    shareResults() {
        if (navigator.share) {
            const resultsContent = document.getElementById('results-content');
            const content = resultsContent.innerText;
            
            navigator.share({
                title: 'Shrimp Search 搜索结果',
                text: content,
                url: window.location.href
            }).catch(console.error);
        } else {
            // 复制到剪贴板
            const resultsContent = document.getElementById('results-content');
            const content = resultsContent.innerText;
            
            navigator.clipboard.writeText(content).then(() => {
                alert('搜索结果已复制到剪贴板');
            }).catch(() => {
                alert('复制失败，请手动复制');
            });
        }
    }
    
    showDocumentManagement() {
        console.log('showDocumentManagement 被调用');
        console.log('模态框元素存在:', !!document.getElementById('document-management-modal'));
        this.showModal('document-management-modal');
        // 默认显示上传选项卡
        this.switchTab('upload');
        // 加载文档列表
        this.loadDocuments();
    }
    
    switchTab(tabName) {
        // 移除所有活动状态
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        
        // 激活选中的选项卡
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        document.getElementById(`${tabName}-tab`).classList.add('active');
        
        // 如果切换到文档列表，加载文档
        if (tabName === 'list') {
            this.loadDocuments();
        }
    }
    
    async loadDocuments() {
        const documentList = document.getElementById('document-list');
        
        // 显示加载状态
        documentList.innerHTML = `
            <div class="loading-placeholder">
                <i class="fas fa-spinner fa-spin"></i>
                <p>加载文档列表中...</p>
            </div>
        `;
        
        try {
            const response = await fetch('http://localhost:5000/api/documents');
            if (!response.ok) {
                throw new Error(`获取文档列表失败: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.renderDocumentList(result.documents);
            } else {
                throw new Error(result.error || '获取文档列表失败');
            }
            
        } catch (error) {
            console.error('加载文档列表失败:', error);
            documentList.innerHTML = `
                <div class="empty-placeholder">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>加载失败: ${error.message}</p>
                    <button class="refresh-btn" onclick="shrimpSearch.loadDocuments()">
                        <i class="fas fa-sync-alt"></i>
                        重试
                    </button>
                </div>
            `;
        }
    }
    
    renderDocumentList(documents) {
        const documentList = document.getElementById('document-list');
        
        if (documents.length === 0) {
            documentList.innerHTML = `
                <div class="empty-placeholder">
                    <i class="fas fa-folder-open"></i>
                    <p>暂无文档</p>
                    <p>点击上传文档选项卡开始上传文件</p>
                </div>
            `;
            return;
        }
        
        const documentsHtml = documents.map(doc => {
            const fileExtension = doc.filename.split('.').pop().toLowerCase();
            const iconClass = this.getFileIcon(fileExtension);
            
            return `
                <div class="document-item">
                    <div class="document-icon">
                        <i class="${iconClass}"></i>
                    </div>
                    <div class="document-info">
                        <div class="document-name">${doc.filename}</div>
                        <div class="document-meta">
                            <span>${doc.formatted_size}</span>
                            <span>${doc.formatted_time}</span>
                        </div>
                    </div>
                    <div class="document-actions">
                        <button class="action-btn-small" onclick="shrimpSearch.previewDocument('${doc.filename}')" title="预览">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="action-btn-small delete" onclick="shrimpSearch.deleteDocument('${doc.filename}')" title="删除">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');
        
        documentList.innerHTML = documentsHtml;
    }
    
    getFileIcon(extension) {
        const iconMap = {
            'pdf': 'fas fa-file-pdf',
            'doc': 'fas fa-file-word',
            'docx': 'fas fa-file-word',
            'txt': 'fas fa-file-alt',
            'md': 'fas fa-file-code',
            'default': 'fas fa-file'
        };
        
        return iconMap[extension] || iconMap.default;
    }
    
    async deleteDocument(filename) {
        if (!confirm(`确定要删除文档 "${filename}" 吗？此操作不可撤销。`)) {
            return;
        }
        
        try {
            const response = await fetch('http://localhost:5000/api/documents/delete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ filename: filename })
            });
            
            if (!response.ok) {
                throw new Error(`删除失败: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                alert(`文档 "${filename}" 删除成功`);
                // 重新加载文档列表
                this.loadDocuments();
            } else {
                throw new Error(result.error || '删除失败');
            }
            
        } catch (error) {
            console.error('删除文档失败:', error);
            alert(`删除失败: ${error.message}`);
        }
    }
    
    previewDocument(filename) {
        // 简单的预览功能，显示文档信息
        alert(`文档预览功能开发中...\n文档名称: ${filename}`);
    }
}

// 初始化应用
let shrimpSearch;
document.addEventListener('DOMContentLoaded', () => {
    shrimpSearch = new ShrimpSearch();
    
    // 如果没有历史记录，添加一些示例
    if (shrimpSearch.searchHistory.length === 0) {
        const sampleQueries = [
            'Python解释器无效解决方法',
            'AI IDE Troubleshooting Steps',
            '存储库索引问题及解决方法',
            '获取国外手机号的多种方法',
            'Claude Code 安装与使用指南'
        ];
        
        sampleQueries.forEach((query, index) => {
            const timestamp = new Date();
            timestamp.setHours(timestamp.getHours() - index);
            
            shrimpSearch.addToHistory(query);
        });
    }
});

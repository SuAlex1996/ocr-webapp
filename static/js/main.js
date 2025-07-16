class OCRApp {
    constructor() {
        this.initializeElements();
        this.attachEventListeners();
        this.currentResult = null;
    }

    initializeElements() {
        this.fileInput = document.getElementById('fileInput');
        this.uploadArea = document.getElementById('uploadArea');
        this.uploadBtn = document.getElementById('uploadBtn');
        this.previewSection = document.getElementById('previewSection');
        this.previewImage = document.getElementById('previewImage');
        this.loadingSection = document.getElementById('loadingSection');
        this.resultSection = document.getElementById('resultSection');
        this.errorSection = document.getElementById('errorSection');
        this.errorText = document.getElementById('errorText');
        this.retryBtn = document.getElementById('retryBtn');
        this.copyBtn = document.getElementById('copyBtn');
        
        // 结果显示元素
        this.structuredData = document.getElementById('structuredData');
        this.rawText = document.getElementById('rawText');
        this.visualAnalysis = document.getElementById('visualAnalysis');
        this.jsonOutput = document.getElementById('jsonOutput');
        
        // 标签页按钮
        this.tabBtns = document.querySelectorAll('.tab-btn');
    }

    attachEventListeners() {
        // 文件选择
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // 上传区域点击
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        
        // 拖拽事件
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        
        // 上传按钮
        this.uploadBtn.addEventListener('click', () => this.uploadFile());
        
        // 重试按钮
        this.retryBtn.addEventListener('click', () => this.resetApp());
        
        // 复制按钮
        this.copyBtn.addEventListener('click', () => this.copyJSON());
        
        // 标签页切换
        this.tabBtns.forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            this.processFile(file);
        }
    }

    handleDragOver(event) {
        event.preventDefault();
        this.uploadArea.classList.add('dragover');
    }

    handleDragLeave(event) {
        event.preventDefault();
        this.uploadArea.classList.remove('dragover');
    }

    handleDrop(event) {
        event.preventDefault();
        this.uploadArea.classList.remove('dragover');
        
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    processFile(file) {
        // 验证文件类型
        const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/tiff'];
        if (!allowedTypes.includes(file.type)) {
            this.showError('不支持的文件格式。请选择图片文件。');
            return;
        }

        // 验证文件大小（16MB）
        if (file.size > 16 * 1024 * 1024) {
            this.showError('文件太大。请选择小于16MB的图片。');
            return;
        }

        // 显示预览
        this.showPreview(file);
        
        // 启用上传按钮
        this.uploadBtn.disabled = false;
        this.selectedFile = file;
    }

    showPreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            this.previewImage.src = e.target.result;
            this.previewSection.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }

    async uploadFile() {
        if (!this.selectedFile) {
            this.showError('请先选择文件');
            return;
        }

        this.showLoading();

        const formData = new FormData();
        formData.append('file', this.selectedFile);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.showResult(result);
            } else {
                this.showError(result.error || '处理失败');
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
        }
    }

    showLoading() {
        this.hideAllSections();
        this.loadingSection.style.display = 'block';
    }

    showResult(result) {
        this.hideAllSections();
        this.currentResult = result;
        
        // 显示结构化数据
        this.displayStructuredData(result.data.structured_data);
        
        // 显示原始文本
        this.rawText.textContent = result.data.extracted_text || '未识别到文本';
        
        // 显示视觉分析
        this.displayVisualAnalysis(result.data.visual_analysis);
        
        // 显示JSON输出
        this.jsonOutput.textContent = JSON.stringify(result, null, 2);
        
        this.resultSection.style.display = 'block';
    }

    displayStructuredData(data) {
        let html = '';
        
        // 网络信息
        if (data.network_info) {
            html += this.createStructuredItem('网络信息', data.network_info);
        }
        
        // 速度测试
        if (data.speed_test) {
            html += this.createStructuredItem('速度测试', data.speed_test);
        }
        
        this.structuredData.innerHTML = html || '<p>未提取到结构化数据</p>';
    }

    createStructuredItem(title, data) {
        let html = `<div class="structured-item">
            <h4>${title}</h4>
            <div class="data-grid">`;
        
        for (const [key, value] of Object.entries(data)) {
            if (key === 'available_operators') {
                html += this.createOperatorsList(value);
            } else if (key === 'signal_strength' && typeof value === 'object') {
                html += this.createSignalStrengthDisplay(value);
            } else if (typeof value === 'object') {
                html += `<div class="data-item">
                    <span class="data-label">${this.formatLabel(key)}:</span>
                    <span class="data-value">${JSON.stringify(value)}</span>
                </div>`;
            } else {
                html += `<div class="data-item">
                    <span class="data-label">${this.formatLabel(key)}:</span>
                    <span class="data-value">${value}</span>
                </div>`;
            }
        }
        
        html += '</div></div>';
        return html;
    }

    createOperatorsList(operators) {
        let html = '<div class="operators-list"><h5>运营商状态:</h5>';
        
        operators.forEach(operator => {
            const statusClass = operator.status === 'active' ? 'status-active' : 'status-inactive';
            html += `<div class="operator-status">
                <span class="status-indicator ${statusClass}"></span>
                <span>${operator.name}</span>
                <span class="brightness-info">(亮度: ${operator.brightness_level})</span>
            </div>`;
        });
        
        html += '</div>';
        return html;
    }

    createSignalStrengthDisplay(signalData) {
        let html = '<div class="signal-strength"><h5>信号强度:</h5>';
        
        for (const [key, value] of Object.entries(signalData)) {
            html += `<div class="data-item">
                <span class="data-label">${key.toUpperCase()}:</span>
                <span class="data-value">${value}</span>
            </div>`;
        }
        
        html += '</div>';
        return html;
    }

    displayVisualAnalysis(visualData) {
        if (!visualData) {
            this.visualAnalysis.innerHTML = '<p>未进行视觉分析</p>';
            return;
        }

        let html = '<div class="visual-analysis-content">';
        
        // 活跃运营商
        if (visualData.active_operator) {
            html += `<div class="analysis-item">
                <h4>当前激活运营商</h4>
                <p class="active-operator">${visualData.active_operator}</p>
            </div>`;
        }
        
        // 运营商亮度分析
        if (visualData.operator_analysis) {
            html += '<div class="analysis-item"><h4>运营商亮度分析</h4>';
            
            for (const [operator, data] of Object.entries(visualData.operator_analysis)) {
                const brightness = data.brightness_stats.mean;
                const percentage = Math.min(100, (brightness / 255) * 100);
                
                html += `<div class="brightness-chart">
                    <div class="operator-name">${operator}</div>
                    <div class="brightness-bar">
                        <div class="brightness-fill" style="width: ${percentage}%"></div>
                    </div>
                    <div class="brightness-value">亮度值: ${brightness.toFixed(1)}</div>
                </div>`;
            }
            
            html += '</div>';
        }
        
        // 整体亮度统计
        if (visualData.brightness_summary) {
            html += `<div class="analysis-item">
                <h4>整体亮度统计</h4>
                <div class="data-grid">
                    <div class="data-item">
                        <span class="data-label">平均亮度:</span>
                        <span class="data-value">${visualData.brightness_summary.overall_mean.toFixed(1)}</span>
                    </div>
                    <div class="data-item">
                        <span class="data-label">标准差:</span>
                        <span class="data-value">${visualData.brightness_summary.overall_std.toFixed(1)}</span>
                    </div>
                </div>
            </div>`;
        }
        
        html += '</div>';
        this.visualAnalysis.innerHTML = html;
    }

    formatLabel(key) {
        const labelMap = {
            'operator': '运营商',
            'location': '位置',
            'network_type': '网络类型',
            'ping': 'Ping',
            'download': '下载速度',
            'upload': '上传速度',
            'active_operator': '当前运营商',
            'rsrp': 'RSRP',
            'rsrq': 'RSRQ',
            'sinr': 'SINR',
            'mcc': 'MCC',
            'mnc': 'MNC'
        };
        
        return labelMap[key] || key;
    }

    switchTab(tabName) {
        // 移除所有活跃状态
        this.tabBtns.forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        // 激活选中的标签页
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        document.getElementById(`${tabName}Tab`).classList.add('active');
    }

    async copyJSON() {
        if (!this.currentResult) return;
        
        try {
            await navigator.clipboard.writeText(JSON.stringify(this.currentResult, null, 2));
            
            // 显示复制成功提示
            const originalText = this.copyBtn.textContent;
            this.copyBtn.textContent = '已复制!';
            this.copyBtn.style.backgroundColor = '#27ae60';
            
            setTimeout(() => {
                this.copyBtn.textContent = originalText;
                this.copyBtn.style.backgroundColor = '';
            }, 2000);
        } catch (err) {
            console.error('复制失败:', err);
            alert('复制失败，请手动复制');
        }
    }

    showError(message) {
        this.hideAllSections();
        this.errorText.textContent = message;
        this.errorSection.style.display = 'block';
    }

    hideAllSections() {
        this.loadingSection.style.display = 'none';
        this.resultSection.style.display = 'none';
        this.errorSection.style.display = 'none';
    }

    resetApp() {
        this.hideAllSections();
        this.previewSection.style.display = 'none';
        this.uploadBtn.disabled = true;
        this.selectedFile = null;
        this.currentResult = null;
        this.fileInput.value = '';
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new OCRApp();
});
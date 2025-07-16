/**
 * OCR Web 应用前端JavaScript
 * 处理文件上传、图像分析和结果展示
 */

class OCRWebApp {
    constructor() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.uploadBtn = document.getElementById('uploadBtn');
        this.previewArea = document.getElementById('previewArea');
        this.previewImage = document.getElementById('previewImage');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.statusSection = document.getElementById('statusSection');
        this.resultsSection = document.getElementById('resultsSection');
        this.errorSection = document.getElementById('errorSection');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        
        this.currentFile = null;
        this.currentResults = null;
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        // 文件选择
        this.uploadBtn.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // 拖拽上传
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        
        // 分析和清除
        this.analyzeBtn.addEventListener('click', () => this.analyzeImage());
        this.clearBtn.addEventListener('click', () => this.clearAll());
        
        // 标签页切换
        const tabBtns = document.querySelectorAll('.tab-btn');
        tabBtns.forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });
        
        // 结果操作
        document.getElementById('copyJsonBtn').addEventListener('click', () => this.copyJson());
        document.getElementById('downloadJsonBtn').addEventListener('click', () => this.downloadJson());
        document.getElementById('retryBtn').addEventListener('click', () => this.analyzeImage());
        
        // 帮助模态框
        document.getElementById('helpBtn').addEventListener('click', () => this.showHelp());
        document.getElementById('modalClose').addEventListener('click', () => this.hideHelp());
        
        // 模态框背景点击关闭
        document.getElementById('helpModal').addEventListener('click', (e) => {
            if (e.target.id === 'helpModal') {
                this.hideHelp();
            }
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
            this.showError('不支持的文件类型，请选择图像文件');
            return;
        }
        
        // 验证文件大小 (16MB)
        if (file.size > 16 * 1024 * 1024) {
            this.showError('文件过大，请选择小于16MB的文件');
            return;
        }
        
        this.currentFile = file;
        this.showPreview(file);
    }
    
    showPreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            this.previewImage.src = e.target.result;
            this.previewArea.style.display = 'block';
            this.previewArea.classList.add('fade-in');
        };
        reader.readAsDataURL(file);
    }
    
    async analyzeImage() {
        if (!this.currentFile) {
            this.showError('请先选择一个图像文件');
            return;
        }
        
        // 显示处理状态
        this.showProcessingStatus();
        
        // 创建FormData
        const formData = new FormData();
        formData.append('file', this.currentFile);
        
        try {
            // 开始处理步骤
            this.updateProcessingStep(1, 'active');
            
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.updateProcessingStep(1, 'completed');
                this.updateProcessingStep(2, 'active');
                
                // 模拟处理步骤
                setTimeout(() => {
                    this.updateProcessingStep(2, 'completed');
                    this.updateProcessingStep(3, 'active');
                    
                    setTimeout(() => {
                        this.updateProcessingStep(3, 'completed');
                        this.updateProcessingStep(4, 'active');
                        
                        setTimeout(() => {
                            this.updateProcessingStep(4, 'completed');
                            this.showResults(result);
                        }, 500);
                    }, 500);
                }, 500);
            } else {
                this.showError(result.error || '处理失败');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showError('网络错误或服务器异常');
        }
    }
    
    showProcessingStatus() {
        // 隐藏其他区域
        this.previewArea.style.display = 'none';
        this.resultsSection.style.display = 'none';
        this.errorSection.style.display = 'none';
        
        // 显示处理状态
        this.statusSection.style.display = 'block';
        this.statusSection.classList.add('fade-in');
        
        // 重置步骤状态
        const steps = document.querySelectorAll('.step');
        steps.forEach(step => {
            step.classList.remove('active', 'completed');
        });
    }
    
    updateProcessingStep(stepNumber, status) {
        const step = document.getElementById(`step${stepNumber}`);
        if (step) {
            step.classList.remove('active', 'completed');
            step.classList.add(status);
        }
    }
    
    showResults(result) {
        // 隐藏处理状态
        this.statusSection.style.display = 'none';
        
        // 显示结果
        this.resultsSection.style.display = 'block';
        this.resultsSection.classList.add('fade-in');
        
        // 保存结果
        this.currentResults = result;
        
        // 填充结果数据
        this.populateResults(result);
    }
    
    populateResults(result) {
        const data = result.data || {};
        const structuredData = data.structured_data || {};
        const networkInfo = structuredData.network_info || {};
        const speedTest = structuredData.speed_test || {};
        
        // 概览标签页
        document.getElementById('extractedText').textContent = 
            data.extracted_text || '未识别到文字';
        document.getElementById('activeOperator').textContent = 
            speedTest.active_operator || networkInfo.operator || '未检测到';
        document.getElementById('networkType').textContent = 
            networkInfo.network_type || '未检测到';
        
        // 信号强度
        const signalStrength = networkInfo.signal_strength || {};
        const signalText = Object.entries(signalStrength)
            .map(([key, value]) => `${key.toUpperCase()}: ${value}`)
            .join(', ') || '未检测到';
        document.getElementById('signalStrength').textContent = signalText;
        
        // 网络信息标签页
        document.getElementById('rsrpValue').textContent = 
            signalStrength.rsrp || '-';
        document.getElementById('rsrqValue').textContent = 
            signalStrength.rsrq || '-';
        document.getElementById('sinrValue').textContent = 
            signalStrength.sinr || '-';
        
        // 测速结果
        document.getElementById('pingValue').textContent = 
            speedTest.ping || '-';
        document.getElementById('downloadValue').textContent = 
            speedTest.download || '-';
        document.getElementById('uploadValue').textContent = 
            speedTest.upload || '-';
        
        // 运营商状态
        this.populateOperatorStatus(speedTest.available_operators || []);
        
        // JSON数据
        document.getElementById('jsonOutput').textContent = 
            JSON.stringify(result, null, 2);
    }
    
    populateOperatorStatus(operators) {
        const operatorsGrid = document.getElementById('operatorsGrid');
        operatorsGrid.innerHTML = '';
        
        if (operators.length === 0) {
            operatorsGrid.innerHTML = '<p>未检测到运营商信息</p>';
            return;
        }
        
        operators.forEach(operator => {
            const card = document.createElement('div');
            card.className = `operator-card ${operator.status}`;
            
            card.innerHTML = `
                <div class="operator-name">${operator.name}</div>
                <div class="operator-status">
                    <span class="status-indicator ${operator.status}"></span>
                    <span>${operator.status === 'active' ? '激活' : '未激活'}</span>
                </div>
                <div class="brightness-info">
                    亮度级别: ${this.getBrightnessLabel(operator.brightness_level)}
                </div>
            `;
            
            operatorsGrid.appendChild(card);
        });
    }
    
    getBrightnessLabel(level) {
        const labels = {
            'very_high': '很高',
            'high': '高',
            'medium': '中等',
            'low': '低',
            'very_low': '很低'
        };
        return labels[level] || level;
    }
    
    switchTab(tabName) {
        // 更新标签按钮状态
        const tabBtns = document.querySelectorAll('.tab-btn');
        tabBtns.forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // 更新内容显示
        const tabContents = document.querySelectorAll('.tab-content');
        tabContents.forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}Tab`).classList.add('active');
    }
    
    copyJson() {
        if (!this.currentResults) {
            this.showError('没有可复制的数据');
            return;
        }
        
        const jsonText = JSON.stringify(this.currentResults, null, 2);
        
        if (navigator.clipboard) {
            navigator.clipboard.writeText(jsonText).then(() => {
                this.showToast('JSON数据已复制到剪贴板');
            }).catch(() => {
                this.fallbackCopyJson(jsonText);
            });
        } else {
            this.fallbackCopyJson(jsonText);
        }
    }
    
    fallbackCopyJson(text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        
        try {
            document.execCommand('copy');
            this.showToast('JSON数据已复制到剪贴板');
        } catch (err) {
            this.showError('复制失败，请手动复制');
        }
        
        document.body.removeChild(textarea);
    }
    
    downloadJson() {
        if (!this.currentResults) {
            this.showError('没有可下载的数据');
            return;
        }
        
        const jsonText = JSON.stringify(this.currentResults, null, 2);
        const blob = new Blob([jsonText], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `ocr_result_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        URL.revokeObjectURL(url);
        this.showToast('JSON文件已下载');
    }
    
    showError(message) {
        // 隐藏其他区域
        this.statusSection.style.display = 'none';
        this.resultsSection.style.display = 'none';
        
        // 显示错误
        this.errorSection.style.display = 'block';
        this.errorSection.classList.add('fade-in');
        document.getElementById('errorMessage').textContent = message;
    }
    
    showToast(message) {
        // 简单的toast通知
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            z-index: 1001;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }
    
    clearAll() {
        // 重置状态
        this.currentFile = null;
        this.currentResults = null;
        
        // 隐藏所有区域
        this.previewArea.style.display = 'none';
        this.statusSection.style.display = 'none';
        this.resultsSection.style.display = 'none';
        this.errorSection.style.display = 'none';
        
        // 重置文件输入
        this.fileInput.value = '';
        
        // 重置预览图像
        this.previewImage.src = '';
        
        // 移除样式类
        document.querySelectorAll('.fade-in').forEach(el => {
            el.classList.remove('fade-in');
        });
    }
    
    showHelp() {
        document.getElementById('helpModal').classList.add('show');
    }
    
    hideHelp() {
        document.getElementById('helpModal').classList.remove('show');
    }
}

// 添加动画样式
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .toast {
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
`;
document.head.appendChild(style);

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new OCRWebApp();
});

// 全局错误处理
window.addEventListener('error', (event) => {
    console.error('全局错误:', event.error);
});

// 阻止默认的拖拽行为
document.addEventListener('dragover', (e) => e.preventDefault());
document.addEventListener('drop', (e) => e.preventDefault());
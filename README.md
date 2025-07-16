# 图片文字识别Web应用

一个基于Python Flask的本地部署图片文字识别系统，支持中文识别和视觉状态分析。

## 功能特点

- **文字识别**: 支持中文和英文文字识别
- **视觉状态分析**: 通过亮度分析识别激活状态的文字
- **结构化输出**: 提取网络信息、速度测试等结构化数据
- **多格式支持**: 支持PNG、JPG、JPEG、GIF、BMP、TIFF格式
- **本地部署**: 无需云服务，完全本地运行
- **友好界面**: 现代化的Web界面，支持拖拽上传

## 系统要求

- Python 3.7+
- Tesseract OCR引擎
- OpenCV
- Flask

## 安装步骤

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 安装Tesseract OCR

#### Windows:
1. 下载Tesseract安装包: https://github.com/UB-Mannheim/tesseract/wiki
2. 安装后将安装路径添加到环境变量
3. 下载中文语言包并放置到tessdata目录

#### macOS:
```bash
brew install tesseract
brew install tesseract-lang
```

#### Ubuntu/Debian:
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-chi-sim
```

### 3. 运行应用

```bash
python app.py
```

访问 http://localhost:5000 开始使用。

## 使用说明

1. **上传图片**: 点击上传区域或拖拽图片文件
2. **开始识别**: 点击"开始识别"按钮
3. **查看结果**: 在不同标签页查看识别结果
   - **结构化数据**: 提取的网络信息、速度测试等
   - **原始文本**: 完整的OCR识别文本
   - **视觉分析**: 亮度分析和状态识别结果
   - **JSON输出**: 完整的JSON格式结果

## 输出格式

```json
{
  "success": true,
  "data": {
    "extracted_text": "识别到的完整文本",
    "structured_data": {
      "network_info": {
        "operator": "中国广电",
        "signal_strength": {
          "rsrp": "-89",
          "rsrq": "-11",
          "sinr": "23"
        },
        "network_type": "5G",
        "location": "116.67193/39.86616"
      },
      "speed_test": {
        "ping": "148ms",
        "download": "25.5Mbps",
        "upload": "1.7Mbps",
        "active_operator": "中国广电",
        "available_operators": [
          {
            "name": "中国广电",
            "status": "active",
            "brightness_level": "high"
          }
        ]
      }
    }
  },
  "timestamp": "2025-07-16T09:02:54Z"
}
```

## 核心技术

### 视觉状态识别算法

1. **文字定位**: 使用Tesseract OCR识别文字区域
2. **亮度分析**: 计算每个文字区域的平均亮度
3. **状态判断**: 比较亮度差异确定激活状态

### 数据提取

- 使用正则表达式提取网络参数
- 智能识别运营商名称
- 提取信号强度和速度测试数据

## API接口

### POST /api/upload
上传图片进行识别

**请求**: multipart/form-data
- file: 图片文件

**响应**: JSON格式的识别结果

### GET /api/health
健康检查接口

## 故障排除

### 常见问题

1. **Tesseract找不到**
   - 确保Tesseract已正确安装
   - 检查环境变量设置

2. **中文识别不准确**
   - 确保安装了中文语言包
   - 检查图片质量和清晰度

3. **识别速度慢**
   - 优化图片大小
   - 调整图片预处理参数

## 开发扩展

### 添加新的数据提取模式

在 `modules/data_extractor.py` 中添加新的正则表达式模式:

```python
self.patterns['new_category'] = {
    'pattern_name': r'regex_pattern'
}
```

### 优化视觉分析算法

在 `modules/visual_analyzer.py` 中调整亮度分析参数:

```python
self.brightness_threshold = 15  # 调整亮度阈值
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 联系方式

如有问题，请创建GitHub Issue或联系开发者。
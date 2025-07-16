# OCR Web应用 - 图像文字识别与视觉状态分析

一个本地部署的Web应用，专门用于识别图片中的文字内容并分析文字的视觉状态（亮度、激活状态等）。特别优化移动网络监控界面的识别和分析。

## 主要功能

- 📸 **图像文字识别**: 支持中文和英文文字的OCR识别
- 🎨 **视觉状态分析**: 通过亮度、对比度分析判断文字的激活状态
- 📊 **数据结构化**: 将识别结果转换为结构化JSON数据
- 🏢 **运营商检测**: 专门识别移动网络运营商选择状态
- 🌐 **本地部署**: 无需云服务依赖，完全本地运行
- 📱 **移动友好**: 响应式设计，支持移动设备访问

## 技术栈

- **前端**: HTML5, CSS3, JavaScript (原生)
- **后端**: Python Flask
- **OCR引擎**: Tesseract OCR
- **图像处理**: OpenCV, PIL (Pillow)
- **视觉分析**: 自定义亮度检测算法
- **数据处理**: 正则表达式, JSON

## 项目结构

```
ocr-webapp/
├── app.py                 # Flask主应用
├── requirements.txt       # Python依赖
├── static/
│   ├── css/
│   │   └── style.css     # 样式文件
│   └── js/
│       └── main.js       # 前端JavaScript
├── templates/
│   └── index.html        # 主页面
├── uploads/              # 上传文件夹
├── modules/
│   ├── __init__.py
│   ├── ocr_processor.py  # OCR处理模块
│   ├── visual_analyzer.py # 视觉状态分析模块
│   └── data_extractor.py # 数据提取模块
└── README.md            # 项目说明
```

## 安装和部署

### 系统要求

- Python 3.7+
- Tesseract OCR 4.0+
- OpenCV 4.0+

### 1. 安装Tesseract OCR

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-chi-sim  # 中文语言包
```

#### CentOS/RHEL
```bash
sudo yum install epel-release
sudo yum install tesseract
sudo yum install tesseract-langpack-chi_sim
```

#### macOS
```bash
brew install tesseract
brew install tesseract-lang
```

#### Windows
1. 从 [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki) 下载安装程序
2. 安装时选择中文语言包
3. 将Tesseract添加到系统PATH

### 2. 克隆项目

```bash
git clone https://github.com/SuAlex1996/ocr-webapp.git
cd ocr-webapp
```

### 3. 安装Python依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 运行应用

```bash
python app.py
```

应用将在 `http://localhost:5000` 启动。

## 使用说明

### 1. 上传图像

- 点击"选择文件"按钮或直接拖拽图像到上传区域
- 支持格式：PNG, JPG, JPEG, GIF, BMP, TIFF
- 文件大小限制：16MB

### 2. 分析图像

- 上传图像后，点击"开始分析"按钮
- 系统将按以下步骤处理：
  1. OCR文字识别
  2. 视觉状态分析
  3. 数据结构化
  4. 结果输出

### 3. 查看结果

结果以四个标签页形式展示：

- **概览**: 显示基本信息和识别摘要
- **网络信息**: 显示信号强度和测速结果
- **运营商状态**: 显示各运营商的激活状态
- **JSON数据**: 显示完整的结构化数据

### 4. 导出结果

- 点击"复制JSON"复制结果到剪贴板
- 点击"下载JSON"下载结果文件

## API接口

### 上传和分析图像
```
POST /upload
Content-Type: multipart/form-data

参数:
- file: 图像文件

响应: JSON格式的分析结果
```

### 健康检查
```
GET /health

响应: 应用状态信息
```

### 获取支持的运营商
```
GET /api/operators

响应: 支持的运营商列表
```

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
          },
          {
            "name": "中国移动",
            "status": "inactive",
            "brightness_level": "low"
          }
        ]
      }
    }
  },
  "timestamp": "2024-07-16T09:18:40Z"
}
```

## 核心算法

### 视觉状态识别算法

1. **文字定位**: 使用Tesseract OCR识别文字位置
2. **区域提取**: 提取每个目标文字的像素区域
3. **亮度计算**: 计算区域的平均亮度、标准差等统计值
4. **对比分析**: 比较不同区域的亮度和对比度
5. **状态判断**: 根据多因素评分判断激活状态

### 亮度分析原理

- **亮度统计**: 计算像素平均值、标准差、中位数
- **对比度分析**: 使用标准差衡量区域对比度
- **清晰度评估**: 使用拉普拉斯算子和边缘检测
- **综合评分**: 多因素权重计算最终激活状态

## 配置选项

### 修改上传限制

在 `app.py` 中修改：
```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 文件大小限制
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
```

### 调整亮度分析参数

在 `modules/visual_analyzer.py` 中修改：
```python
self.brightness_threshold = 50  # 亮度差异阈值
self.contrast_threshold = 30    # 对比度差异阈值
```

### 添加新的运营商

在 `modules/data_extractor.py` 中修改：
```python
self.operators = ['中国移动', '中国联通', '中国电信', '中国广电', '新运营商']
```

## 故障排除

### 常见问题

1. **Tesseract找不到**
   - 确保Tesseract已安装并在PATH中
   - 检查语言包是否正确安装

2. **识别效果不佳**
   - 确保图像清晰，分辨率适中
   - 避免过度倾斜或模糊的图像

3. **内存使用过高**
   - 调整图像大小限制
   - 优化图像预处理参数

### 调试模式

启动应用时添加调试参数：
```bash
python app.py
# 或在URL中添加 ?debug=true
```

### 日志查看

应用日志会显示在控制台中，包含：
- 文件上传信息
- OCR处理状态
- 视觉分析结果
- 错误信息

## 开发指南

### 添加新的图像处理功能

1. 在 `modules/` 目录创建新模块
2. 实现处理逻辑
3. 在 `app.py` 中集成
4. 更新前端展示

### 自定义视觉分析算法

1. 修改 `modules/visual_analyzer.py`
2. 实现新的分析方法
3. 调整判断逻辑
4. 测试和优化

### 扩展数据提取规则

1. 修改 `modules/data_extractor.py`
2. 添加新的正则表达式模式
3. 实现结构化提取逻辑
4. 更新输出格式

## 性能优化

- 使用图像预处理提高OCR准确率
- 实现异步处理减少响应时间
- 添加缓存机制避免重复计算
- 优化前端资源加载

## 安全考虑

- 文件类型验证
- 文件大小限制
- 上传路径安全
- 输入数据验证

## 版本历史

- **v1.0.0**: 初始版本，支持基本OCR和视觉状态分析
- 计划功能：批量处理、模板匹配、API认证

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献

欢迎提交问题和改进建议！

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 支持

如有问题或建议，请提交Issue或联系开发者。
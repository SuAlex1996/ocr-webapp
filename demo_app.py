"""
简化的测试版本 - 用于演示UI功能
不需要OCR依赖项即可运行
"""

import os
import json
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 应用配置
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB最大文件大小
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    处理文件上传和模拟OCR识别
    """
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有选择文件'
            }), 400
        
        file = request.files['file']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '没有选择文件'
            }), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': '不支持的文件类型'
            }), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f"文件上传成功: {filepath}")
        
        # 返回模拟的OCR结果
        result = generate_mock_result(filepath)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"文件上传处理失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'处理失败: {str(e)}'
        }), 500

def generate_mock_result(image_path):
    """
    生成模拟的OCR分析结果
    """
    return {
        "success": True,
        "data": {
            "extracted_text": "RSRP: -89 dBm\nRSRQ: -11 dB\nSINR: 23 dB\n5G网络\n中国广电\n中国移动\n延迟: 148ms\n下载: 25.5Mbps\n上传: 1.7Mbps\n位置: 116.67193/39.86616",
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
        "processing_info": {
            "image_path": image_path,
            "ocr_confidence": 85.6,
            "visual_analysis_performed": True,
            "operators_detected": 2,
            "processing_time": datetime.utcnow().isoformat() + 'Z'
        },
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """访问上传的文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'version': '1.0.0-demo'
    })

@app.route('/api/operators', methods=['GET'])
def get_supported_operators():
    """获取支持的运营商列表"""
    operators = ['中国移动', '中国联通', '中国电信', '中国广电']
    return jsonify({
        'success': True,
        'operators': operators
    })

@app.route('/api/test-ocr', methods=['POST'])
def test_ocr():
    """测试OCR功能 - 模拟版本"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有选择文件'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '没有选择文件'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': '不支持的文件类型'
            }), 400
        
        # 返回模拟的OCR结果
        return jsonify({
            'success': True,
            'ocr_result': {
                'text': '中国广电 中国移动 5G RSRP:-89 RSRQ:-11 SINR:23',
                'word_data': [
                    {'text': '中国广电', 'left': 100, 'top': 50, 'width': 80, 'height': 30, 'conf': 95},
                    {'text': '中国移动', 'left': 200, 'top': 50, 'width': 80, 'height': 30, 'conf': 92},
                    {'text': '5G', 'left': 150, 'top': 100, 'width': 30, 'height': 25, 'conf': 98},
                    {'text': 'RSRP:-89', 'left': 50, 'top': 150, 'width': 80, 'height': 20, 'conf': 88}
                ],
                'image_shape': [400, 600]
            },
            'average_confidence': 93.25
        })
        
    except Exception as e:
        logger.error(f"OCR测试失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'OCR测试失败: {str(e)}'
        }), 500

@app.errorhandler(413)
def too_large(e):
    """文件过大错误处理"""
    return jsonify({
        'success': False,
        'error': '文件过大，请选择小于16MB的文件'
    }), 413

@app.errorhandler(500)
def internal_error(e):
    """内部错误处理"""
    logger.error(f"内部错误: {str(e)}")
    return jsonify({
        'success': False,
        'error': '服务器内部错误'
    }), 500

if __name__ == '__main__':
    # 启动应用
    logger.info("启动OCR Web应用 (演示版本)...")
    logger.info("注意：这是演示版本，使用模拟数据。要使用真实OCR功能，请安装完整依赖项。")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
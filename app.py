"""
Flask主应用程序
处理图像上传和OCR识别
"""

import os
import json
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

# 导入自定义模块
from modules.ocr_processor import OCRProcessor
from modules.visual_analyzer import VisualAnalyzer
from modules.data_extractor import DataExtractor

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

# 初始化处理器
ocr_processor = OCRProcessor()
visual_analyzer = VisualAnalyzer()
data_extractor = DataExtractor()

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
    处理文件上传和OCR识别
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
        
        # 处理图像
        result = process_image(filepath)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"文件上传处理失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'处理失败: {str(e)}'
        }), 500

@app.route('/process', methods=['POST'])
def process_image_api():
    """
    处理图像的API接口
    """
    try:
        data = request.get_json()
        
        if not data or 'image_path' not in data:
            return jsonify({
                'success': False,
                'error': '缺少图像路径'
            }), 400
        
        image_path = data['image_path']
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            return jsonify({
                'success': False,
                'error': '图像文件不存在'
            }), 404
        
        # 处理图像
        result = process_image(image_path)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"图像处理API失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'处理失败: {str(e)}'
        }), 500

def process_image(image_path):
    """
    处理图像的核心函数
    
    Args:
        image_path (str): 图像路径
        
    Returns:
        dict: 处理结果
    """
    try:
        logger.info(f"开始处理图像: {image_path}")
        
        # 步骤1: OCR文字识别
        logger.info("步骤1: 执行OCR文字识别")
        ocr_result = ocr_processor.extract_text(image_path)
        
        # 步骤2: 视觉状态分析
        logger.info("步骤2: 执行视觉状态分析")
        
        # 定义要分析的运营商
        operators = ['中国移动', '中国联通', '中国电信', '中国广电']
        
        # 获取运营商文字区域
        operator_regions = ocr_processor.get_text_regions(image_path, operators)
        
        # 分析视觉状态
        visual_analysis = None
        if operator_regions['target_regions']:
            visual_analysis = visual_analyzer.analyze_text_brightness(
                image_path, operator_regions['target_regions']
            )
            
            # 专门的运营商比较
            comparison_result = visual_analyzer.compare_text_regions(
                image_path, operators
            )
            
            if comparison_result and 'comparison_result' in comparison_result:
                visual_analysis['comparison_result'] = comparison_result['comparison_result']
        
        # 步骤3: 数据提取和结构化
        logger.info("步骤3: 执行数据提取和结构化")
        
        # 使用移动网络专用的数据提取方法
        structured_result = data_extractor.extract_mobile_network_data(
            ocr_result, visual_analysis
        )
        
        # 步骤4: 验证结果
        logger.info("步骤4: 验证提取结果")
        is_valid, errors = data_extractor.validate_extracted_data(structured_result)
        
        if not is_valid:
            logger.warning(f"数据验证失败: {errors}")
            structured_result['validation_errors'] = errors
        
        # 添加处理过程信息
        structured_result['processing_info'] = {
            'image_path': image_path,
            'ocr_confidence': calculate_average_confidence(ocr_result),
            'visual_analysis_performed': visual_analysis is not None,
            'operators_detected': len(operator_regions['target_regions']) if operator_regions['target_regions'] else 0,
            'processing_time': datetime.utcnow().isoformat() + 'Z'
        }
        
        # 如果需要调试信息
        if request.args.get('debug') == 'true':
            structured_result['debug_info'] = {
                'ocr_result': ocr_result,
                'visual_analysis': visual_analysis,
                'operator_regions': operator_regions
            }
        
        logger.info("图像处理完成")
        return structured_result
        
    except Exception as e:
        logger.error(f"图像处理失败: {str(e)}")
        return {
            'success': False,
            'error': f'图像处理失败: {str(e)}',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

def calculate_average_confidence(ocr_result):
    """
    计算OCR识别的平均置信度
    
    Args:
        ocr_result (dict): OCR识别结果
        
    Returns:
        float: 平均置信度
    """
    try:
        word_data = ocr_result.get('word_data', [])
        if not word_data:
            return 0.0
        
        confidences = [word['conf'] for word in word_data if word['conf'] > 0]
        if not confidences:
            return 0.0
        
        return sum(confidences) / len(confidences)
        
    except Exception as e:
        logger.error(f"计算置信度失败: {str(e)}")
        return 0.0

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
        'version': '1.0.0'
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
    """测试OCR功能"""
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
        
        # 保存临时文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 只进行OCR识别
        ocr_result = ocr_processor.extract_text(filepath)
        
        # 清理临时文件
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify({
            'success': True,
            'ocr_result': ocr_result,
            'average_confidence': calculate_average_confidence(ocr_result)
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
    # 检查Tesseract是否可用
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        logger.info("Tesseract OCR可用")
    except Exception as e:
        logger.error(f"Tesseract OCR不可用: {str(e)}")
        logger.error("请确保已安装Tesseract OCR")
    
    # 启动应用
    logger.info("启动OCR Web应用...")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
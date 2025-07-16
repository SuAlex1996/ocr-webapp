from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from modules.ocr_processor import OCRProcessor
from modules.visual_analyzer import VisualAnalyzer
from modules.data_extractor import DataExtractor

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有文件被上传'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # 处理图片
            result = process_image(filepath)
            
            # 删除上传的文件（可选）
            # os.remove(filepath)
            
            return jsonify(result)
        else:
            return jsonify({'success': False, 'error': '不支持的文件格式'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def process_image(filepath):
    """处理上传的图片"""
    try:
        # 初始化处理器
        ocr_processor = OCRProcessor()
        visual_analyzer = VisualAnalyzer()
        data_extractor = DataExtractor()
        
        # OCR文字识别
        ocr_result = ocr_processor.process_image(filepath)
        
        # 视觉状态分析
        visual_result = visual_analyzer.analyze_brightness(filepath, ocr_result)
        
        # 数据提取和结构化
        structured_data = data_extractor.extract_structured_data(
            ocr_result['text'], 
            visual_result
        )
        
        # 构建最终结果
        result = {
            'success': True,
            'data': {
                'extracted_text': ocr_result['text'],
                'structured_data': structured_data,
                'visual_analysis': visual_result,
                'processing_info': {
                    'confidence': ocr_result.get('confidence', 0),
                    'detected_regions': len(ocr_result.get('regions', [])),
                    'brightness_analysis': visual_result.get('brightness_summary', {})
                }
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        return result
    
    except Exception as e:
        return {
            'success': False,
            'error': f'处理图片时发生错误: {str(e)}',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
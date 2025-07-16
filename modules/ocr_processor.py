"""
OCR处理模块
使用Tesseract OCR引擎进行文字识别
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRProcessor:
    def __init__(self):
        """初始化OCR处理器"""
        # 配置Tesseract OCR参数
        # 支持中文和英文
        self.config = '--oem 3 --psm 6 -l chi_sim+eng'
        
    def preprocess_image(self, image_path):
        """
        图像预处理
        
        Args:
            image_path (str): 图像路径
            
        Returns:
            tuple: (原始图像, 处理后图像)
        """
        try:
            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"无法读取图像: {image_path}")
            
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 应用高斯滤波去噪
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # 自适应阈值处理
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # 形态学操作，去除噪声
            kernel = np.ones((1, 1), np.uint8)
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            logger.info(f"图像预处理完成: {image_path}")
            return image, processed
            
        except Exception as e:
            logger.error(f"图像预处理失败: {str(e)}")
            raise
    
    def extract_text(self, image_path):
        """
        从图像中提取文字
        
        Args:
            image_path (str): 图像路径
            
        Returns:
            dict: 包含文字内容和位置信息的字典
        """
        try:
            # 预处理图像
            original, processed = self.preprocess_image(image_path)
            
            # 使用Tesseract进行OCR识别
            text = pytesseract.image_to_string(processed, config=self.config)
            
            # 获取文字位置信息
            boxes = pytesseract.image_to_boxes(processed, config=self.config)
            
            # 获取详细的文字信息
            data = pytesseract.image_to_data(processed, config=self.config, output_type=pytesseract.Output.DICT)
            
            # 处理结果
            result = {
                'text': text.strip(),
                'boxes': self._parse_boxes(boxes),
                'word_data': self._parse_word_data(data),
                'image_shape': original.shape[:2]  # (height, width)
            }
            
            logger.info(f"文字提取完成，识别到 {len(result['word_data'])} 个词")
            return result
            
        except Exception as e:
            logger.error(f"文字提取失败: {str(e)}")
            raise
    
    def _parse_boxes(self, boxes):
        """
        解析字符框位置信息
        
        Args:
            boxes (str): Tesseract输出的字符框信息
            
        Returns:
            list: 字符框信息列表
        """
        box_list = []
        for line in boxes.splitlines():
            if line.strip():
                parts = line.split()
                if len(parts) >= 6:
                    box_list.append({
                        'char': parts[0],
                        'left': int(parts[1]),
                        'bottom': int(parts[2]),
                        'right': int(parts[3]),
                        'top': int(parts[4]),
                        'page': int(parts[5])
                    })
        return box_list
    
    def _parse_word_data(self, data):
        """
        解析词语数据
        
        Args:
            data (dict): Tesseract输出的数据字典
            
        Returns:
            list: 词语信息列表
        """
        word_data = []
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            if int(data['conf'][i]) > 0:  # 只保留置信度大于0的结果
                word_info = {
                    'text': data['text'][i],
                    'left': data['left'][i],
                    'top': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i],
                    'conf': data['conf'][i]
                }
                word_data.append(word_info)
        
        return word_data
    
    def get_text_regions(self, image_path, target_texts=None):
        """
        获取特定文字的区域信息
        
        Args:
            image_path (str): 图像路径
            target_texts (list): 目标文字列表
            
        Returns:
            dict: 文字区域信息
        """
        try:
            ocr_result = self.extract_text(image_path)
            
            if target_texts is None:
                return ocr_result
            
            # 过滤目标文字
            filtered_regions = []
            for word in ocr_result['word_data']:
                if any(target in word['text'] for target in target_texts):
                    filtered_regions.append(word)
            
            result = {
                'text': ocr_result['text'],
                'target_regions': filtered_regions,
                'image_shape': ocr_result['image_shape']
            }
            
            logger.info(f"找到 {len(filtered_regions)} 个目标文字区域")
            return result
            
        except Exception as e:
            logger.error(f"获取文字区域失败: {str(e)}")
            raise
import cv2
import pytesseract
import numpy as np
from PIL import Image
import re

class OCRProcessor:
    def __init__(self):
        # 配置tesseract支持中文
        self.config = '--oem 3 --psm 6 -l chi_sim+eng'
        
    def process_image(self, image_path):
        """处理图片并进行OCR识别"""
        try:
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("无法读取图片文件")
            
            # 预处理图片
            processed_image = self._preprocess_image(image)
            
            # 进行OCR识别
            text = pytesseract.image_to_string(processed_image, config=self.config)
            
            # 获取文字区域信息
            regions = self._get_text_regions(processed_image)
            
            # 计算置信度
            confidence = self._calculate_confidence(processed_image)
            
            return {
                'text': text.strip(),
                'regions': regions,
                'confidence': confidence,
                'image_shape': image.shape
            }
            
        except Exception as e:
            raise Exception(f"OCR处理失败: {str(e)}")
    
    def _preprocess_image(self, image):
        """图片预处理"""
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 增强对比度
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # 去噪
        denoised = cv2.medianBlur(enhanced, 3)
        
        # 二值化
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def _get_text_regions(self, image):
        """获取文字区域信息"""
        try:
            # 使用tesseract获取文字区域
            data = pytesseract.image_to_data(image, config=self.config, output_type=pytesseract.Output.DICT)
            
            regions = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 30:  # 置信度阈值
                    region = {
                        'text': data['text'][i].strip(),
                        'bbox': {
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i]
                        },
                        'confidence': data['conf'][i]
                    }
                    if region['text']:  # 只保留有文字的区域
                        regions.append(region)
            
            return regions
            
        except Exception as e:
            print(f"获取文字区域失败: {str(e)}")
            return []
    
    def _calculate_confidence(self, image):
        """计算OCR置信度"""
        try:
            data = pytesseract.image_to_data(image, config=self.config, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            return np.mean(confidences) if confidences else 0
        except:
            return 0
import cv2
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR
from paddleocr import TextRecognition
import re

class OCRProcessor:
    def __init__(self):
        # 初始化PaddleOCR，支持中英文
        
        self.ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            # text_recognition_model_name="PP-OCRv5_mobile_rec"
            )
        # self.ocr = TextRecognition(
        #     model_name="PP-OCRv5_mobile_rec",
        #     model_dir="./PP-OCRv5_mobile_rec_infer/",
        #     device='cpu',
        #     enable_hpi=True,
        # )
    def process_image(self, image_path):
        """处理图片并进行OCR识别"""
        try:
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("无法读取图片文件")
            
            # # 去除干扰色
            # remove_image = self.remove_interference_color(image)
            
            # # 预处理图片
            # processed_image = self._preprocess_image(remove_image)

            # 进行OCR识别
            print('?????')
            result = self.ocr.predict(image)
            print('!!!!')
            # 处理OCR结果
            text_lines = []
            regions = []
            confidences = []
            print(result)
            if result and result[0]:
                for line in result[0]:
                    if line:
                        # PaddleOCR返回格式：[[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], (text, confidence)]
                        bbox = line[0]
                        text_info = line[1]
                        text = text_info[0]
                        confidence = text_info[1]
                        
                        text_lines.append(text)
                        confidences.append(confidence)
                        
                        # 计算边界框
                        x_coords = [point[0] for point in bbox]
                        y_coords = [point[1] for point in bbox]
                        
                        region = {
                            'text': text,
                            'bbox': {
                                'x': int(min(x_coords)),
                                'y': int(min(y_coords)),
                                'width': int(max(x_coords) - min(x_coords)),
                                'height': int(max(y_coords) - min(y_coords))
                            },
                            'confidence': confidence,
                            'polygon': bbox  # 四边形坐标
                        }
                        regions.append(region)
            
            # 合并所有文本
            full_text = '\n'.join(text_lines)
            
            # 计算平均置信度
            avg_confidence = np.mean(confidences) if confidences else 0
            
            return {
                'text': full_text.strip(),
                'regions': regions,
                'confidence': avg_confidence,
                'image_shape': image.shape
            }
            
        except Exception as e:
            raise Exception(f"OCR处理失败process_image: {str(e)}")
        
    def remove_interference_color(self, image):
        """去除干扰色"""
        # 转为HSV空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # 设定#877755的HSV范围（可微调）
        lower = np.array([20, 40, 80])
        upper = np.array([34, 100, 147])
        mask = cv2.inRange(hsv, lower, upper)
        # 反向：只保留非干扰色区域
        anti_mask = cv2.bitwise_not(mask)
        result = cv2.bitwise_and(image, image, mask=anti_mask)
        return result
    
    def _preprocess_image(self, image):
        """图片预处理"""
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 增强对比度
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # 去噪
        denoised = cv2.medianBlur(enhanced, 3)
        cv2.imwrite("denoised_image.png", denoised)
        
        # 二值化
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        denoised = cv2.medianBlur(binary, 3)
        
        # 保存处理后的图片（可选）
        cv2.imwrite("processed_image.png", denoised)
        return denoised
    
    def get_text_only(self, image_path):
        """仅获取文本内容的简化方法"""
        try:
            result = self.ocr.predict(image_path, cls=True)
            text_lines = []
            
            if result and result[0]:
                for line in result[0]:
                    if line:
                        text = line[1][0]
                        text_lines.append(text)
            
            return '\n'.join(text_lines)
            
        except Exception as e:
            raise Exception(f"OCR处理失败get_text_only: {str(e)}")
    
    def get_text_with_positions(self, image_path):
        """获取文本及其位置信息"""
        try:
            result = self.ocr.predict(image_path, cls=True)
            text_data = []
            
            if result and result[0]:
                for line in result[0]:
                    if line:
                        bbox = line[0]
                        text = line[1][0]
                        confidence = line[1][1]
                        
                        # 计算中心点
                        center_x = sum([point[0] for point in bbox]) / 4
                        center_y = sum([point[1] for point in bbox]) / 4
                        
                        text_data.append({
                            'text': text,
                            'confidence': confidence,
                            'bbox': bbox,
                            'center': [center_x, center_y]
                        })
            
            return text_data
            
        except Exception as e:
            raise Exception(f"OCR处理失败get_text_with_positions: {str(e)}")

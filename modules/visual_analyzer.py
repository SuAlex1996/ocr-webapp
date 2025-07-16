import cv2
import numpy as np
from PIL import Image
import re

class VisualAnalyzer:
    def __init__(self):
        self.brightness_threshold = 10  # 亮度差异阈值
        
    def analyze_brightness(self, image_path, ocr_result):
        """分析图片中文字区域的亮度"""
        try:
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("无法读取图片文件")
            
            # 转换为灰度图用于亮度分析
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 分析运营商文字的亮度
            operator_analysis = self._analyze_operator_brightness(gray, ocr_result['regions'])
            
            # 分析整体亮度分布
            brightness_summary = self._analyze_overall_brightness(gray)
            
            return {
                'operator_analysis': operator_analysis,
                'brightness_summary': brightness_summary,
                'active_operator': self._determine_active_operator(operator_analysis)
            }
            
        except Exception as e:
            raise Exception(f"视觉分析失败: {str(e)}")
    
    def _analyze_operator_brightness(self, gray_image, regions):
        """分析运营商文字的亮度"""
        operator_keywords = ['中国广电', '中国移动', '中国联通', '中国电信']
        operator_brightness = {}
        
        for region in regions:
            text = region['text']
            
            # 检查是否包含运营商关键词
            for keyword in operator_keywords:
                if keyword in text or self._fuzzy_match(text, keyword):
                    bbox = region['bbox']
                    
                    # 提取文字区域
                    x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']
                    
                    # 确保坐标在图像范围内
                    h_img, w_img = gray_image.shape
                    x = max(0, min(x, w_img - 1))
                    y = max(0, min(y, h_img - 1))
                    w = max(1, min(w, w_img - x))
                    h = max(1, min(h, h_img - y))
                    
                    text_region = gray_image[y:y+h, x:x+w]
                    
                    if text_region.size > 0:
                        # 计算亮度统计
                        brightness_stats = self._calculate_brightness_stats(text_region)
                        
                        operator_brightness[keyword] = {
                            'text': text,
                            'bbox': bbox,
                            'brightness_stats': brightness_stats,
                            'region_size': text_region.size,
                            'confidence': region.get('confidence', 0)
                        }
        
        return operator_brightness
    
    def _fuzzy_match(self, text, keyword):
        """模糊匹配运营商名称"""
        # 移除空格和特殊字符
        text_clean = re.sub(r'[^\w\u4e00-\u9fff]', '', text)
        keyword_clean = re.sub(r'[^\w\u4e00-\u9fff]', '', keyword)
        
        # 检查是否包含关键字的主要部分
        if len(keyword_clean) > 2:
            return keyword_clean[2:] in text_clean  # 例如：'广电' in text
        return False
    
    def _calculate_brightness_stats(self, region):
        """计算区域亮度统计"""
        if region.size == 0:
            return {
                'mean': 0,
                'std': 0,
                'min': 0,
                'max': 0,
                'median': 0
            }
        
        return {
            'mean': float(np.mean(region)),
            'std': float(np.std(region)),
            'min': float(np.min(region)),
            'max': float(np.max(region)),
            'median': float(np.median(region))
        }
    
    def _analyze_overall_brightness(self, gray_image):
        """分析整体亮度分布"""
        return {
            'overall_mean': float(np.mean(gray_image)),
            'overall_std': float(np.std(gray_image)),
            'histogram': np.histogram(gray_image, bins=10)[0].tolist()
        }
    
    def _determine_active_operator(self, operator_analysis):
        """根据亮度分析确定活跃的运营商"""
        if not operator_analysis:
            return None
        
        # 按亮度排序
        sorted_operators = sorted(
            operator_analysis.items(),
            key=lambda x: x[1]['brightness_stats']['mean'],
            reverse=True
        )
        
        if len(sorted_operators) < 2:
            return sorted_operators[0][0] if sorted_operators else None
        
        # 检查最亮的和第二亮的之间的差异
        brightest = sorted_operators[0]
        second_brightest = sorted_operators[1]
        
        brightness_diff = (brightest[1]['brightness_stats']['mean'] - 
                         second_brightest[1]['brightness_stats']['mean'])
        
        # 如果亮度差异超过阈值，返回最亮的
        if brightness_diff > self.brightness_threshold:
            return brightest[0]
        
        # 如果差异不大，可能都是激活状态或者都不是
        return brightest[0]  # 默认返回最亮的
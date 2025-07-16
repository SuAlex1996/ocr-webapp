"""
视觉状态分析模块
分析图像中文字的视觉状态（亮度、对比度等）
用于判断文字的激活状态
"""

import cv2
import numpy as np
import logging
from typing import List, Dict, Tuple, Optional

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisualAnalyzer:
    def __init__(self):
        """初始化视觉分析器"""
        # 亮度分析的阈值设置
        self.brightness_threshold = 50  # 亮度差异阈值
        self.contrast_threshold = 30    # 对比度差异阈值
        
    def analyze_text_brightness(self, image_path: str, text_regions: List[Dict]) -> Dict:
        """
        分析文字区域的亮度
        
        Args:
            image_path (str): 图像路径
            text_regions (list): 文字区域列表
            
        Returns:
            dict: 亮度分析结果
        """
        try:
            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"无法读取图像: {image_path}")
            
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            brightness_results = []
            
            for region in text_regions:
                # 提取文字区域
                x, y, w, h = region['left'], region['top'], region['width'], region['height']
                
                # 确保区域在图像范围内
                x = max(0, x)
                y = max(0, y)
                w = min(w, gray.shape[1] - x)
                h = min(h, gray.shape[0] - y)
                
                if w > 0 and h > 0:
                    # 提取区域
                    region_roi = gray[y:y+h, x:x+w]
                    
                    # 计算亮度统计
                    brightness_stats = self._calculate_brightness_stats(region_roi)
                    
                    # 计算对比度
                    contrast = self._calculate_contrast(region_roi)
                    
                    # 分析文字清晰度
                    clarity = self._analyze_text_clarity(region_roi)
                    
                    result = {
                        'text': region['text'],
                        'region': {'x': x, 'y': y, 'width': w, 'height': h},
                        'brightness': brightness_stats,
                        'contrast': contrast,
                        'clarity': clarity,
                        'confidence': region.get('conf', 0)
                    }
                    
                    brightness_results.append(result)
            
            # 分析激活状态
            activation_analysis = self._analyze_activation_states(brightness_results)
            
            logger.info(f"完成 {len(brightness_results)} 个文字区域的亮度分析")
            
            return {
                'region_analysis': brightness_results,
                'activation_analysis': activation_analysis,
                'summary': self._generate_summary(brightness_results, activation_analysis)
            }
            
        except Exception as e:
            logger.error(f"亮度分析失败: {str(e)}")
            raise
    
    def _calculate_brightness_stats(self, roi: np.ndarray) -> Dict:
        """
        计算区域亮度统计
        
        Args:
            roi (np.ndarray): 区域图像
            
        Returns:
            dict: 亮度统计信息
        """
        if roi.size == 0:
            return {'mean': 0, 'std': 0, 'min': 0, 'max': 0}
        
        return {
            'mean': float(np.mean(roi)),
            'std': float(np.std(roi)),
            'min': float(np.min(roi)),
            'max': float(np.max(roi)),
            'median': float(np.median(roi))
        }
    
    def _calculate_contrast(self, roi: np.ndarray) -> float:
        """
        计算区域对比度
        
        Args:
            roi (np.ndarray): 区域图像
            
        Returns:
            float: 对比度值
        """
        if roi.size == 0:
            return 0.0
        
        # 使用标准差作为对比度的衡量
        return float(np.std(roi))
    
    def _analyze_text_clarity(self, roi: np.ndarray) -> Dict:
        """
        分析文字清晰度
        
        Args:
            roi (np.ndarray): 区域图像
            
        Returns:
            dict: 清晰度分析结果
        """
        if roi.size == 0:
            return {'sharpness': 0.0, 'edge_density': 0.0}
        
        # 计算锐度（使用拉普拉斯算子）
        laplacian = cv2.Laplacian(roi, cv2.CV_64F)
        sharpness = np.var(laplacian)
        
        # 计算边缘密度
        edges = cv2.Canny(roi, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        return {
            'sharpness': float(sharpness),
            'edge_density': float(edge_density)
        }
    
    def _analyze_activation_states(self, brightness_results: List[Dict]) -> Dict:
        """
        分析激活状态
        
        Args:
            brightness_results (list): 亮度分析结果列表
            
        Returns:
            dict: 激活状态分析结果
        """
        if not brightness_results:
            return {'active_texts': [], 'inactive_texts': []}
        
        # 计算平均亮度
        avg_brightness = np.mean([r['brightness']['mean'] for r in brightness_results])
        
        active_texts = []
        inactive_texts = []
        
        for result in brightness_results:
            brightness = result['brightness']['mean']
            contrast = result['contrast']
            
            # 判断激活状态的逻辑
            # 1. 亮度高于平均值
            # 2. 对比度较高
            # 3. 清晰度较高
            is_active = self._determine_activation_status(
                brightness, avg_brightness, contrast, result['clarity']
            )
            
            text_info = {
                'text': result['text'],
                'brightness_level': self._categorize_brightness(brightness),
                'brightness_value': brightness,
                'contrast_value': contrast,
                'status': 'active' if is_active else 'inactive',
                'confidence': result['confidence']
            }
            
            if is_active:
                active_texts.append(text_info)
            else:
                inactive_texts.append(text_info)
        
        return {
            'active_texts': active_texts,
            'inactive_texts': inactive_texts,
            'average_brightness': avg_brightness
        }
    
    def _determine_activation_status(self, brightness: float, avg_brightness: float, 
                                   contrast: float, clarity: Dict) -> bool:
        """
        判断文字是否为激活状态
        
        Args:
            brightness (float): 文字亮度
            avg_brightness (float): 平均亮度
            contrast (float): 对比度
            clarity (dict): 清晰度信息
            
        Returns:
            bool: 是否为激活状态
        """
        # 多因素判断激活状态
        brightness_score = brightness - avg_brightness
        contrast_score = contrast
        clarity_score = clarity['sharpness']
        
        # 综合评分
        activation_score = (
            (brightness_score > self.brightness_threshold) * 0.4 +
            (contrast_score > self.contrast_threshold) * 0.3 +
            (clarity_score > 100) * 0.3  # 锐度阈值
        )
        
        return activation_score > 0.5
    
    def _categorize_brightness(self, brightness: float) -> str:
        """
        分类亮度级别
        
        Args:
            brightness (float): 亮度值
            
        Returns:
            str: 亮度级别
        """
        if brightness > 180:
            return 'very_high'
        elif brightness > 140:
            return 'high'
        elif brightness > 100:
            return 'medium'
        elif brightness > 60:
            return 'low'
        else:
            return 'very_low'
    
    def _generate_summary(self, brightness_results: List[Dict], 
                         activation_analysis: Dict) -> Dict:
        """
        生成分析摘要
        
        Args:
            brightness_results (list): 亮度分析结果
            activation_analysis (dict): 激活状态分析
            
        Returns:
            dict: 分析摘要
        """
        total_texts = len(brightness_results)
        active_count = len(activation_analysis['active_texts'])
        inactive_count = len(activation_analysis['inactive_texts'])
        
        return {
            'total_text_regions': total_texts,
            'active_regions': active_count,
            'inactive_regions': inactive_count,
            'average_brightness': activation_analysis['average_brightness'],
            'activation_ratio': active_count / total_texts if total_texts > 0 else 0
        }
    
    def compare_text_regions(self, image_path: str, text_list: List[str]) -> Dict:
        """
        比较特定文字列表的视觉状态
        
        Args:
            image_path (str): 图像路径
            text_list (list): 要比较的文字列表
            
        Returns:
            dict: 比较结果
        """
        try:
            # 这里需要先获取OCR结果
            from .ocr_processor import OCRProcessor
            
            ocr = OCRProcessor()
            ocr_result = ocr.get_text_regions(image_path, text_list)
            
            # 分析亮度
            brightness_analysis = self.analyze_text_brightness(
                image_path, ocr_result['target_regions']
            )
            
            # 专门针对运营商选择的比较
            comparison_result = self._compare_operator_selection(
                brightness_analysis, text_list
            )
            
            return {
                'ocr_result': ocr_result,
                'brightness_analysis': brightness_analysis,
                'comparison_result': comparison_result
            }
            
        except Exception as e:
            logger.error(f"文字区域比较失败: {str(e)}")
            raise
    
    def _compare_operator_selection(self, brightness_analysis: Dict, 
                                  text_list: List[str]) -> Dict:
        """
        专门用于运营商选择比较的方法
        
        Args:
            brightness_analysis (dict): 亮度分析结果
            text_list (list): 运营商文字列表
            
        Returns:
            dict: 运营商选择比较结果
        """
        active_texts = brightness_analysis['activation_analysis']['active_texts']
        inactive_texts = brightness_analysis['activation_analysis']['inactive_texts']
        
        # 构建运营商状态字典
        operator_states = {}
        
        # 处理激活的文字
        for text_info in active_texts:
            for operator in text_list:
                if operator in text_info['text']:
                    operator_states[operator] = {
                        'status': 'active',
                        'brightness_level': text_info['brightness_level'],
                        'brightness_value': text_info['brightness_value'],
                        'confidence': text_info['confidence']
                    }
        
        # 处理非激活的文字
        for text_info in inactive_texts:
            for operator in text_list:
                if operator in text_info['text'] and operator not in operator_states:
                    operator_states[operator] = {
                        'status': 'inactive',
                        'brightness_level': text_info['brightness_level'],
                        'brightness_value': text_info['brightness_value'],
                        'confidence': text_info['confidence']
                    }
        
        # 确定当前激活的运营商
        active_operator = None
        max_brightness = 0
        
        for operator, state in operator_states.items():
            if state['status'] == 'active' and state['brightness_value'] > max_brightness:
                active_operator = operator
                max_brightness = state['brightness_value']
        
        return {
            'operator_states': operator_states,
            'active_operator': active_operator,
            'available_operators': list(operator_states.keys())
        }
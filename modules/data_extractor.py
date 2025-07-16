"""
数据提取和结构化模块
从OCR结果中提取结构化数据
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataExtractor:
    def __init__(self):
        """初始化数据提取器"""
        # 定义正则表达式模式
        self.patterns = {
            'rsrp': r'RSRP[:\s]*(-?\d+)',
            'rsrq': r'RSRQ[:\s]*(-?\d+)',
            'sinr': r'SINR[:\s]*(-?\d+)',
            'ping': r'(\d+)\s*ms',
            'download_speed': r'(\d+\.?\d*)\s*Mbps.*下载',
            'upload_speed': r'(\d+\.?\d*)\s*Mbps.*上传',
            'coordinates': r'(\d+\.\d+)/(\d+\.\d+)',
            'network_type': r'(2G|3G|4G|5G)',
            'operators': r'(中国移动|中国联通|中国电信|中国广电)'
        }
        
        # 运营商列表
        self.operators = ['中国移动', '中国联通', '中国电信', '中国广电']
        
    def extract_structured_data(self, ocr_text: str, visual_analysis: Dict) -> Dict:
        """
        从OCR文本和视觉分析结果中提取结构化数据
        
        Args:
            ocr_text (str): OCR识别的文本
            visual_analysis (dict): 视觉分析结果
            
        Returns:
            dict: 结构化数据
        """
        try:
            # 提取网络信息
            network_info = self._extract_network_info(ocr_text)
            
            # 提取测速信息
            speed_test_info = self._extract_speed_test_info(ocr_text, visual_analysis)
            
            # 生成最终结果
            result = {
                'success': True,
                'data': {
                    'extracted_text': ocr_text,
                    'structured_data': {
                        'network_info': network_info,
                        'speed_test': speed_test_info
                    }
                },
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            
            logger.info("结构化数据提取完成")
            return result
            
        except Exception as e:
            logger.error(f"数据提取失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
    
    def _extract_network_info(self, text: str) -> Dict:
        """
        提取网络信息
        
        Args:
            text (str): OCR文本
            
        Returns:
            dict: 网络信息
        """
        network_info = {}
        
        # 提取信号强度信息
        signal_strength = {}
        
        # RSRP
        rsrp_match = re.search(self.patterns['rsrp'], text, re.IGNORECASE)
        if rsrp_match:
            signal_strength['rsrp'] = rsrp_match.group(1)
        
        # RSRQ
        rsrq_match = re.search(self.patterns['rsrq'], text, re.IGNORECASE)
        if rsrq_match:
            signal_strength['rsrq'] = rsrq_match.group(1)
        
        # SINR
        sinr_match = re.search(self.patterns['sinr'], text, re.IGNORECASE)
        if sinr_match:
            signal_strength['sinr'] = sinr_match.group(1)
        
        if signal_strength:
            network_info['signal_strength'] = signal_strength
        
        # 提取网络类型
        network_type_match = re.search(self.patterns['network_type'], text)
        if network_type_match:
            network_info['network_type'] = network_type_match.group(1)
        
        # 提取位置信息
        coordinates_match = re.search(self.patterns['coordinates'], text)
        if coordinates_match:
            network_info['location'] = f"{coordinates_match.group(1)}/{coordinates_match.group(2)}"
        
        # 提取运营商信息
        operator_match = re.search(self.patterns['operators'], text)
        if operator_match:
            network_info['operator'] = operator_match.group(1)
        
        return network_info
    
    def _extract_speed_test_info(self, text: str, visual_analysis: Dict) -> Dict:
        """
        提取测速信息
        
        Args:
            text (str): OCR文本
            visual_analysis (dict): 视觉分析结果
            
        Returns:
            dict: 测速信息
        """
        speed_test_info = {}
        
        # 提取ping值
        ping_match = re.search(self.patterns['ping'], text)
        if ping_match:
            speed_test_info['ping'] = f"{ping_match.group(1)}ms"
        
        # 提取下载速度
        download_matches = re.findall(r'(\d+\.?\d*)\s*Mbps', text)
        if download_matches:
            # 通常第一个是下载速度，第二个是上传速度
            if len(download_matches) >= 1:
                speed_test_info['download'] = f"{download_matches[0]}Mbps"
            if len(download_matches) >= 2:
                speed_test_info['upload'] = f"{download_matches[1]}Mbps"
        
        # 从视觉分析中提取运营商状态信息
        if visual_analysis and 'comparison_result' in visual_analysis:
            comparison_result = visual_analysis['comparison_result']
            
            # 当前激活的运营商
            if comparison_result['active_operator']:
                speed_test_info['active_operator'] = comparison_result['active_operator']
            
            # 所有可用运营商的状态
            available_operators = []
            for operator, state in comparison_result['operator_states'].items():
                operator_info = {
                    'name': operator,
                    'status': state['status'],
                    'brightness_level': state['brightness_level']
                }
                available_operators.append(operator_info)
            
            if available_operators:
                speed_test_info['available_operators'] = available_operators
        
        return speed_test_info
    
    def extract_mobile_network_data(self, ocr_result: Dict, visual_analysis: Dict) -> Dict:
        """
        专门用于移动网络监控数据提取
        
        Args:
            ocr_result (dict): OCR识别结果
            visual_analysis (dict): 视觉分析结果
            
        Returns:
            dict: 移动网络监控数据
        """
        try:
            text = ocr_result.get('text', '')
            
            # 使用更精确的提取方法
            structured_data = self.extract_structured_data(text, visual_analysis)
            
            # 针对移动网络监控界面的特殊处理
            if structured_data['success']:
                # 增强网络信息提取
                network_info = self._enhance_network_info_extraction(text, ocr_result)
                if network_info:
                    structured_data['data']['structured_data']['network_info'].update(network_info)
                
                # 增强测速信息提取
                speed_info = self._enhance_speed_test_extraction(text, visual_analysis)
                if speed_info:
                    structured_data['data']['structured_data']['speed_test'].update(speed_info)
            
            return structured_data
            
        except Exception as e:
            logger.error(f"移动网络数据提取失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
    
    def _enhance_network_info_extraction(self, text: str, ocr_result: Dict) -> Dict:
        """
        增强网络信息提取
        
        Args:
            text (str): OCR文本
            ocr_result (dict): OCR结果
            
        Returns:
            dict: 增强的网络信息
        """
        enhanced_info = {}
        
        # 使用词语级别的数据进行更精确的提取
        word_data = ocr_result.get('word_data', [])
        
        # 寻找信号强度相关的词语
        for i, word in enumerate(word_data):
            word_text = word['text'].strip()
            
            # 查找RSRP、RSRQ、SINR等关键词附近的数值
            if 'RSRP' in word_text.upper():
                # 查找附近的数值
                nearby_number = self._find_nearby_number(word_data, i)
                if nearby_number:
                    enhanced_info['rsrp_detailed'] = {
                        'value': nearby_number,
                        'position': word
                    }
            
            elif 'RSRQ' in word_text.upper():
                nearby_number = self._find_nearby_number(word_data, i)
                if nearby_number:
                    enhanced_info['rsrq_detailed'] = {
                        'value': nearby_number,
                        'position': word
                    }
            
            elif 'SINR' in word_text.upper():
                nearby_number = self._find_nearby_number(word_data, i)
                if nearby_number:
                    enhanced_info['sinr_detailed'] = {
                        'value': nearby_number,
                        'position': word
                    }
        
        return enhanced_info
    
    def _enhance_speed_test_extraction(self, text: str, visual_analysis: Dict) -> Dict:
        """
        增强测速信息提取
        
        Args:
            text (str): OCR文本
            visual_analysis (dict): 视觉分析结果
            
        Returns:
            dict: 增强的测速信息
        """
        enhanced_info = {}
        
        # 更精确的速度提取
        speed_patterns = {
            'download': r'下载.*?(\d+\.?\d*)\s*Mbps',
            'upload': r'上传.*?(\d+\.?\d*)\s*Mbps',
            'ping': r'延迟.*?(\d+)\s*ms'
        }
        
        for key, pattern in speed_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                enhanced_info[f'{key}_detailed'] = {
                    'value': match.group(1),
                    'unit': 'Mbps' if key != 'ping' else 'ms'
                }
        
        # 从视觉分析中提取详细的运营商信息
        if visual_analysis and 'comparison_result' in visual_analysis:
            comparison_result = visual_analysis['comparison_result']
            
            # 详细的运营商状态分析
            operator_analysis = {
                'selection_confidence': 0.0,
                'brightness_comparison': {},
                'visual_indicators': {}
            }
            
            operator_states = comparison_result.get('operator_states', {})
            
            # 计算选择置信度
            active_operators = [op for op, state in operator_states.items() 
                             if state['status'] == 'active']
            
            if len(active_operators) == 1:
                operator_analysis['selection_confidence'] = 0.9
            elif len(active_operators) > 1:
                operator_analysis['selection_confidence'] = 0.5
            
            # 亮度比较
            for operator, state in operator_states.items():
                operator_analysis['brightness_comparison'][operator] = {
                    'brightness_value': state['brightness_value'],
                    'brightness_level': state['brightness_level'],
                    'relative_brightness': state['brightness_value'] / max(
                        [s['brightness_value'] for s in operator_states.values()]
                    )
                }
            
            enhanced_info['operator_analysis'] = operator_analysis
        
        return enhanced_info
    
    def _find_nearby_number(self, word_data: List[Dict], index: int, 
                          search_range: int = 3) -> Optional[str]:
        """
        在指定词语附近查找数字
        
        Args:
            word_data (list): 词语数据列表
            index (int): 当前词语索引
            search_range (int): 搜索范围
            
        Returns:
            str: 找到的数字，如果没有找到则返回None
        """
        start_index = max(0, index - search_range)
        end_index = min(len(word_data), index + search_range + 1)
        
        for i in range(start_index, end_index):
            if i != index:
                word_text = word_data[i]['text'].strip()
                # 查找数字（包括负数）
                number_match = re.search(r'-?\d+', word_text)
                if number_match:
                    return number_match.group(0)
        
        return None
    
    def format_json_output(self, data: Dict, pretty: bool = True) -> str:
        """
        格式化JSON输出
        
        Args:
            data (dict): 要格式化的数据
            pretty (bool): 是否美化输出
            
        Returns:
            str: JSON字符串
        """
        try:
            if pretty:
                return json.dumps(data, ensure_ascii=False, indent=2)
            else:
                return json.dumps(data, ensure_ascii=False)
        except Exception as e:
            logger.error(f"JSON格式化失败: {str(e)}")
            return json.dumps({
                'success': False,
                'error': f'JSON格式化失败: {str(e)}'
            }, ensure_ascii=False)
    
    def validate_extracted_data(self, data: Dict) -> Tuple[bool, List[str]]:
        """
        验证提取的数据
        
        Args:
            data (dict): 提取的数据
            
        Returns:
            tuple: (是否有效, 错误信息列表)
        """
        errors = []
        
        # 检查基本结构
        if not data.get('success', False):
            errors.append("数据提取失败")
            return False, errors
        
        # 检查数据字段
        if 'data' not in data:
            errors.append("缺少data字段")
        else:
            data_section = data['data']
            
            # 检查extracted_text
            if 'extracted_text' not in data_section:
                errors.append("缺少extracted_text字段")
            elif not data_section['extracted_text'].strip():
                errors.append("提取的文本为空")
            
            # 检查structured_data
            if 'structured_data' not in data_section:
                errors.append("缺少structured_data字段")
            else:
                structured_data = data_section['structured_data']
                
                # 检查网络信息
                if 'network_info' not in structured_data:
                    errors.append("缺少network_info字段")
                
                # 检查测速信息
                if 'speed_test' not in structured_data:
                    errors.append("缺少speed_test字段")
        
        # 检查时间戳
        if 'timestamp' not in data:
            errors.append("缺少timestamp字段")
        
        return len(errors) == 0, errors
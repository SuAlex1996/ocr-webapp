import re
from datetime import datetime

class DataExtractor:
    def __init__(self):
        # 正则表达式模式
        self.patterns = {
            'signal_strength': {
                'rsrp': r'RSRP[:\s]*(-?\d+)',
                'rsrq': r'RSRQ[:\s]*(-?\d+)',
                'sinr': r'SINR[:\s]*(-?\d+)'
            },
            'network_info': {
                'location': r'(\d+\.\d+/\d+\.\d+)',
                'mcc': r'MCC[:\s]*(\d+)',
                'mnc': r'MNC[:\s]*(\d+)'
            },
            'speed_test': {
                'ping': r'(\d+)\s*ms',
                'download': r'(\d+\.?\d*)\s*Mbps.*下载',
                'upload': r'(\d+\.?\d*)\s*Mbps.*上传'
            }
        }
    
    def extract_structured_data(self, text, visual_result):
        """提取结构化数据"""
        try:
            # 提取网络信息
            network_info = self._extract_network_info(text)
            
            # 提取速度测试信息
            speed_test = self._extract_speed_test(text, visual_result)
            
            # 提取信号强度
            signal_strength = self._extract_signal_strength(text)
            
            # 组合结果
            structured_data = {
                'network_info': {
                    **network_info,
                    'signal_strength': signal_strength
                },
                'speed_test': speed_test
            }
            
            return structured_data
            
        except Exception as e:
            print(f"数据提取失败: {str(e)}")
            return {}
    
    def _extract_network_info(self, text):
        """提取网络信息"""
        network_info = {}
        
        # 提取运营商信息
        operators = ['中国广电', '中国移动', '中国联通', '中国电信']
        for operator in operators:
            if operator in text:
                network_info['operator'] = operator
                break
        
        # 提取位置信息
        location_match = re.search(self.patterns['network_info']['location'], text)
        if location_match:
            network_info['location'] = location_match.group(1)
        
        # 提取MCC/MNC
        mcc_match = re.search(self.patterns['network_info']['mcc'], text)
        if mcc_match:
            network_info['mcc'] = mcc_match.group(1)
        
        mnc_match = re.search(self.patterns['network_info']['mnc'], text)
        if mnc_match:
            network_info['mnc'] = mnc_match.group(1)
        
        # 判断网络类型
        if '5G' in text:
            network_info['network_type'] = '5G'
        elif 'LTE' in text or '4G' in text:
            network_info['network_type'] = '4G'
        elif '3G' in text:
            network_info['network_type'] = '3G'
        
        return network_info
    
    def _extract_signal_strength(self, text):
        """提取信号强度信息"""
        signal_strength = {}
        
        # 提取RSRP
        rsrp_match = re.search(self.patterns['signal_strength']['rsrp'], text)
        if rsrp_match:
            signal_strength['rsrp'] = rsrp_match.group(1)
        
        # 提取RSRQ
        rsrq_match = re.search(self.patterns['signal_strength']['rsrq'], text)
        if rsrq_match:
            signal_strength['rsrq'] = rsrq_match.group(1)
        
        # 提取SINR
        sinr_match = re.search(self.patterns['signal_strength']['sinr'], text)
        if sinr_match:
            signal_strength['sinr'] = sinr_match.group(1)
        
        return signal_strength
    
    def _extract_speed_test(self, text, visual_result):
        """提取速度测试信息"""
        speed_test = {}
        
        # 提取ping值
        ping_matches = re.findall(r'(\d+)\s*ms', text)
        if ping_matches:
            # 通常第一个较大的数值是ping值
            ping_values = [int(p) for p in ping_matches if int(p) > 10]
            if ping_values:
                speed_test['ping'] = f"{ping_values[0]}ms"
        
        # 提取下载速度
        download_matches = re.findall(r'(\d+\.?\d*)\s*Mbps', text)
        if download_matches:
            # 通常较大的数值是下载速度
            download_values = [float(d) for d in download_matches if float(d) > 1]
            if download_values:
                speed_test['download'] = f"{max(download_values)}Mbps"
        
        # 提取上传速度
        upload_matches = re.findall(r'(\d+\.?\d*)\s*Mbps', text)
        if upload_matches:
            # 通常较小的数值是上传速度
            upload_values = [float(u) for u in upload_matches if float(u) < 10]
            if upload_values:
                speed_test['upload'] = f"{min(upload_values)}Mbps"
        
        # 添加视觉分析结果
        if visual_result and 'active_operator' in visual_result:
            speed_test['active_operator'] = visual_result['active_operator']
        
        # 添加运营商状态信息
        if visual_result and 'operator_analysis' in visual_result:
            available_operators = []
            for operator, data in visual_result['operator_analysis'].items():
                status = 'active' if operator == visual_result.get('active_operator') else 'inactive'
                brightness_level = 'high' if data['brightness_stats']['mean'] > 150 else 'low'
                
                available_operators.append({
                    'name': operator,
                    'status': status,
                    'brightness_level': brightness_level,
                    'brightness_value': data['brightness_stats']['mean']
                })
            
            speed_test['available_operators'] = available_operators
        
        return speed_test
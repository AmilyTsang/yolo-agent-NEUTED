import json
import re

class OutputParser:
    def parse_json(self, output_text):
        try:
            start_idx = output_text.find("{")
            end_idx = output_text.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = output_text[start_idx:end_idx]
                result = json.loads(json_str)
                return self._normalize_keys(result)
        except:
            pass
        
        return self._get_default_result()
    
    def _normalize_keys(self, result):
        mapping = {
            '类别': 'defect_type',
            '类型': 'defect_type',
            '缺陷类型': 'defect_type',
            '依据': 'evidence',
            '证据': 'evidence',
            '风险': 'severity',
            '风险等级': 'severity',
            '严重程度': 'severity',
            '成因': 'causes',
            '原因': 'causes',
            '措施': 'measures',
            '解决措施': 'measures',
            '建议': 'suggestions',
            '预防建议': 'suggestions'
        }
        
        normalized = {}
        for key, value in result.items():
            normalized_key = mapping.get(key, key)
            normalized[normalized_key] = value
        
        return normalized
    
    def _get_default_result(self):
        return {
            'defect_type': 'unknown',
            'evidence': ['模型分析'],
            'severity': 'medium',
            'causes': '文档未详述',
            'measures': '文档未详述',
            'suggestions': '文档未详述'
        }
    
    def parse_severity(self, severity_str):
        severity_map = {
            '高': 'high',
            '中': 'medium',
            '低': 'low',
            'high': 'high',
            'medium': 'medium',
            'low': 'low'
        }
        return severity_map.get(severity_str.lower(), 'medium')
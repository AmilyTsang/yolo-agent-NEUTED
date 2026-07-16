import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.core.constants import DEFECT_TYPE_MAP, SEVERITY_MAP

class ReportSerializer:
    @staticmethod
    def serialize_defect_summary(fused_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        defect_counts = {}
        for defect in fused_results:
            defect_type = defect.get('defect_type', 'unknown')
            defect_counts[defect_type] = defect_counts.get(defect_type, 0) + 1
        
        high_severity = sum(1 for d in fused_results if d.get('severity') == 'high')
        medium_severity = sum(1 for d in fused_results if d.get('severity') == 'medium')
        low_severity = len(fused_results) - high_severity - medium_severity
        
        return {
            'total': len(fused_results),
            'types': defect_counts,
            'high_severity': high_severity,
            'medium_severity': medium_severity,
            'low_severity': low_severity
        }
    
    @staticmethod
    def serialize_defect_detail(defect: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'defect_type': defect.get('defect_type', 'unknown'),
            'defect_name': DEFECT_TYPE_MAP.get(defect.get('defect_type', ''), defect.get('defect_type', 'unknown')),
            'confidence_level': defect.get('confidence_level', 0),
            'bbox': defect.get('bbox', []),
            'severity': defect.get('severity', 'medium'),
            'severity_text': SEVERITY_MAP.get(defect.get('severity', ''), defect.get('severity', '')),
            'evidence': defect.get('evidence', []),
            'causes': defect.get('causes', ''),
            'measures': defect.get('measures', ''),
            'suggestions': defect.get('suggestions', ''),
            'recommendation': defect.get('recommendation', '')
        }
    
    @staticmethod
    def serialize_report(file_id: str, fused_results: List[Dict[str, Any]], 
                        decision: str, decision_reason: str,
                        confirmed_by: Optional[str] = None, 
                        confirmed_at: Optional[str] = None) -> Dict[str, Any]:
        decision_text_map = {
            'auto_pass': '自动通过',
            'auto_reject': '自动判NG',
            'manual_review': '人工审核',
            'pending': '待确认'
        }
        
        return {
            'report_id': file_id,
            'generated_at': datetime.now().isoformat(),
            'decision': decision,
            'decision_text': decision_text_map.get(decision, '待确认'),
            'decision_reason': decision_reason,
            'defect_summary': ReportSerializer.serialize_defect_summary(fused_results),
            'defects': [ReportSerializer.serialize_defect_detail(d) for d in fused_results],
            'confirmed_by': confirmed_by,
            'confirmed_at': confirmed_at,
            'workflow': [
                '图像预处理',
                'YOLO缺陷检测',
                '置信度判断',
                'ROI裁剪(扩边20%)',
                'RAG知识检索',
                'Prompt Builder',
                'Qwen2.5-VL验证',
                'Detection Fusion',
                'Decision Engine',
                'Report Generator'
            ]
        }
    
    @staticmethod
    def to_json(report_data: Dict[str, Any], filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
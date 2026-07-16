from typing import List, Dict, Any, Optional

from app.fusion.score_calibrator import ScoreCalibrator
from app.core.constants import SEVERITY_BY_TYPE
from app.core.logging import logger

class FusionEngine:
    def __init__(self, rag_config=None):
        self.retriever = None
        if rag_config:
            from app.rag.retriever import RAGRetriever
            self.retriever = RAGRetriever(rag_config)
        
        self.score_calibrator = ScoreCalibrator()
        self.severity_map = {'高': 'high', '中': 'medium', '低': 'low'}
    
    def fuse(self, detections: List[Dict[str, Any]], 
             qwen_results: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        logger.info("开始Detection Fusion")
        
        fused_results = []
        
        for i, detection in enumerate(detections):
            defect_type = detection['defect_type']
            confidence = detection['confidence']
            bbox = detection['bbox']
            
            fused = {
                'defect_type': defect_type,
                'confidence_level': confidence,
                'bbox': bbox,
                'evidence': [f"YOLO检测: {defect_type}, 置信度: {confidence:.4f}"],
                'severity': SEVERITY_BY_TYPE.get(defect_type, 'medium'),
                'recommendation': '',
                'causes': '',
                'measures': '',
                'suggestions': '',
                'confidence_judgment': 'high' if confidence >= 0.6 else 'low'
            }
            
            qwen_result = qwen_results[i] if qwen_results and i < len(qwen_results) else None
            
            if qwen_result:
                fused = self._integrate_qwen_result(fused, qwen_result)
            else:
                if self.retriever:
                    fused = self._enrich_with_knowledge(fused)
            
            fused['confidence_level'] = self.score_calibrator.calibrate(
                fused['confidence_level'], fused['severity'], qwen_result is not None
            )
            
            fused['recommendation'] = self._generate_recommendation(fused)
            
            fused_results.append(fused)
        
        logger.info(f"Detection Fusion完成，共{len(fused_results)}个融合结果")
        
        return fused_results
    
    def _integrate_qwen_result(self, fused: Dict[str, Any], qwen_result: Dict[str, Any]) -> Dict[str, Any]:
        evidence = qwen_result.get('evidence', qwen_result.get('依据', []))
        if isinstance(evidence, list):
            fused['evidence'].extend(evidence)
        else:
            fused['evidence'].append(str(evidence))
        
        severity = qwen_result.get('severity', qwen_result.get('风险', 'medium'))
        fused['severity'] = self.severity_map.get(severity, severity)
        
        fused['causes'] = qwen_result.get('causes', qwen_result.get('成因', ''))
        fused['measures'] = qwen_result.get('measures', qwen_result.get('措施', ''))
        fused['suggestions'] = qwen_result.get('suggestions', qwen_result.get('建议', ''))
        
        return fused
    
    def _enrich_with_knowledge(self, fused: Dict[str, Any]) -> Dict[str, Any]:
        standard = self.retriever.search_standard(fused['defect_type'])
        if standard:
            severity = standard.get('severity', 'medium')
            fused['severity'] = self.severity_map.get(severity, severity)
            fused['evidence'].append(f"企业标准: {standard.get('standard', '')}")
        
        return fused
    
    def _generate_recommendation(self, fused: Dict[str, Any]) -> str:
        recommendations = {
            'high': f"检测到高风险缺陷({fused['defect_type']})，建议立即停机检查相关设备",
            'medium': f"检测到中等风险缺陷({fused['defect_type']})，建议优化相关工艺参数",
            'low': f"检测到低风险缺陷({fused['defect_type']})，建议加强监控，定期维护"
        }
        return recommendations.get(fused['severity'], "建议结合实际情况进行判断")
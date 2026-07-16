from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

@dataclass
class PipelineContext:
    file_id: Optional[str] = None
    image_path: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    
    preprocessed: Dict[str, Any] = field(default_factory=dict)
    detections: List[Dict[str, Any]] = field(default_factory=list)
    qwen_results: List[Dict[str, Any]] = field(default_factory=list)
    fused_results: List[Dict[str, Any]] = field(default_factory=list)
    decision: str = 'pending'
    decision_reason: str = ''
    needs_review: bool = False
    reports: Dict[str, str] = field(default_factory=dict)
    
    error: Optional[str] = None
    success: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'defects': self.detections,
            'fused_results': self.fused_results,
            'decision': self.decision,
            'decision_reason': self.decision_reason,
            'needs_review': self.needs_review,
            'reports': self.reports if self.reports else None,
            'error': self.error if self.error else None
        }
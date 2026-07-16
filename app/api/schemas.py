from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Defect:
    defect_type: str
    confidence: float
    bbox: List[int]
    area: Optional[int] = None

@dataclass
class FusedResult:
    defect_type: str
    confidence_level: float
    bbox: List[int]
    evidence: List[str]
    severity: str
    recommendation: str
    causes: str = ""
    measures: str = ""
    suggestions: str = ""
    confidence_judgment: str = ""

@dataclass
class DetectionRequest:
    file_id: Optional[str] = None
    image_path: Optional[str] = None

@dataclass
class DetectionResponse:
    success: bool
    defects: List[Defect] = field(default_factory=list)
    fused_results: List[FusedResult] = field(default_factory=list)
    decision: str = "pending"
    decision_reason: str = ""
    needs_review: bool = False
    reports: Optional[dict] = None
    error: Optional[str] = None

@dataclass
class ConfirmRequest:
    file_id: str
    user_id: str
    confirm_decision: str

@dataclass
class ConfirmResponse:
    success: bool
    message: str
    decision: Optional[str] = None

@dataclass
class AutoDecisionRequest:
    file_id: str

@dataclass
class AutoDecisionResponse:
    success: bool
    decision: str
    reason: str

@dataclass
class ReportRequest:
    file_id: str

@dataclass
class ReportResponse:
    success: bool
    json_report: Optional[str] = None
    pdf_report: Optional[str] = None
    message: str = ""
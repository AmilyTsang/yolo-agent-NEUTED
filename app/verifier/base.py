from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseVerifier(ABC):
    @abstractmethod
    def __init__(self, config: Dict[str, Any]):
        pass
    
    @abstractmethod
    def load_model(self):
        pass
    
    @abstractmethod
    def verify(self, roi_image, full_image, defect_type, confidence, 
              enterprise_standard, historical_cases, threshold=0.6) -> Dict[str, Any]:
        pass
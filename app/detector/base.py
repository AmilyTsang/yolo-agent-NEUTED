from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseDetector(ABC):
    @abstractmethod
    def __init__(self, config: Dict[str, Any]):
        pass
    
    @abstractmethod
    def load_model(self):
        pass
    
    @abstractmethod
    def detect(self, image_path: str) -> Any:
        pass
    
    @abstractmethod
    def parse_results(self, results: Any) -> List[Dict[str, Any]]:
        pass
class ScoreCalibrator:
    def __init__(self, high_weight=0.7, medium_weight=0.85, low_weight=0.95):
        self.high_weight = high_weight
        self.medium_weight = medium_weight
        self.low_weight = low_weight
        self.verification_boost = 0.05
    
    def calibrate(self, confidence: float, severity: str, verified: bool = False) -> float:
        weight = self._get_severity_weight(severity)
        calibrated = confidence * weight
        
        if verified:
            calibrated = min(1.0, calibrated + self.verification_boost)
        
        return round(calibrated, 4)
    
    def _get_severity_weight(self, severity: str) -> float:
        weights = {
            'high': self.high_weight,
            'medium': self.medium_weight,
            'low': self.low_weight
        }
        return weights.get(severity, self.medium_weight)
    
    def combine_scores(self, yolo_score: float, qwen_score: float = None, 
                      weights: tuple = (0.6, 0.4)) -> float:
        if qwen_score is None:
            return yolo_score
        
        combined = weights[0] * yolo_score + weights[1] * qwen_score
        return round(min(1.0, combined), 4)
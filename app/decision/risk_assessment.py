class RiskAssessor:
    def __init__(self):
        self.severity_map = {
            'crazing': 'medium',
            'inclusion': 'high',
            'patches': 'medium',
            'pitted_surface': 'low',
            'rolled-in_scale': 'medium',
            'scratches': 'low'
        }
    
    def assess_risk(self, defect_type, confidence, qwen_result=None):
        if qwen_result and 'severity' in qwen_result:
            return qwen_result['severity']
        
        if defect_type in self.severity_map:
            return self.severity_map[defect_type]
        
        if confidence >= 0.9:
            return 'high'
        elif confidence >= 0.6:
            return 'medium'
        else:
            return 'low'
    
    def calculate_risk_score(self, defects):
        score_map = {'high': 3, 'medium': 2, 'low': 1}
        total_score = 0
        
        for defect in defects:
            severity = defect.get('severity', 'medium')
            total_score += score_map.get(severity, 2)
        
        return total_score
from typing import Dict, Any, Tuple

from app.decision.rules import load_rules, DEFAULT_RULES

class RuleEngine:
    def __init__(self, config=None):
        self.rules = load_rules(config)
    
    def evaluate(self, defects) -> Tuple[str, str]:
        high_severity = sum(1 for d in defects if d.get('severity') == 'high')
        medium_severity = sum(1 for d in defects if d.get('severity') == 'medium')
        low_severity = sum(1 for d in defects if d.get('severity') == 'low')
        total_defects = len(defects)
        
        if high_severity >= self.rules['high_severity']['threshold']:
            action = self.rules['high_severity']['action']
            reason = self.rules['high_severity']['reason'].format(high_severity)
            return action, reason
        
        if medium_severity >= self.rules['medium_severity']['manual_review_threshold']:
            action = 'manual_review'
            reason = self.rules['medium_severity']['manual_review_reason'].format(medium_severity)
            return action, reason
        
        if medium_severity >= self.rules['medium_severity']['auto_reject_threshold']:
            action = 'auto_reject'
            reason = self.rules['medium_severity']['auto_reject_reason'].format(medium_severity)
            return action, reason
        
        if total_defects == 0:
            action = self.rules['no_defects']['action']
            reason = self.rules['no_defects']['reason']
            return action, reason
        
        action = self.rules['low_severity']['action']
        reason = self.rules['low_severity']['reason']
        return action, reason
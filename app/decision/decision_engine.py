from typing import Dict, Any

from app.decision.risk_assessment import RiskAssessor
from app.decision.rule_engine import RuleEngine
from app.core.logging import logger

class DecisionEngine:
    def __init__(self, config=None):
        self.risk_assessor = RiskAssessor()
        self.rule_engine = RuleEngine(config)
    
    def assess(self, defects):
        logger.info(f"开始风险评估，缺陷数量: {len(defects)}")
        
        for defect in defects:
            qwen_result = defect.get('qwen_result', {})
            defect['severity'] = self.risk_assessor.assess_risk(
                defect.get('defect_type', ''),
                defect.get('confidence', 0),
                qwen_result
            )
        
        logger.info(f"风险评估完成")
        return defects
    
    def decide(self, defects):
        logger.info("开始决策引擎")
        
        assessed_defects = self.assess(defects)
        decision, reason = self.rule_engine.evaluate(assessed_defects)
        
        logger.info(f"决策引擎完成，判定结果: {decision}")
        
        return {
            'decision': decision,
            'decision_reason': reason,
            'defects': assessed_defects,
            'needs_review': decision == 'manual_review'
        }
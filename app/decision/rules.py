from typing import Dict, Any

DEFAULT_RULES = {
    'high_severity': {
        'action': 'manual_review',
        'threshold': 1,
        'reason': '检测到{}个高风险缺陷，需要人工审核'
    },
    'medium_severity': {
        'manual_review_threshold': 3,
        'auto_reject_threshold': 1,
        'manual_review_reason': '检测到{}个中等风险缺陷，需要人工审核',
        'auto_reject_reason': '检测到{}个中等风险缺陷，自动判NG'
    },
    'low_severity': {
        'action': 'auto_pass',
        'reason': '仅检测到低风险缺陷，自动通过'
    },
    'no_defects': {
        'action': 'auto_pass',
        'reason': '未检测到缺陷，自动通过'
    }
}

def load_rules(config: Dict[str, Any] = None) -> Dict[str, Any]:
    if not config:
        return DEFAULT_RULES
    
    rules = DEFAULT_RULES.copy()
    
    if 'high_severity' in config:
        rules['high_severity'].update(config['high_severity'])
    
    if 'medium_severity' in config:
        rules['medium_severity'].update(config['medium_severity'])
    
    if 'low_severity' in config:
        rules['low_severity'].update(config['low_severity'])
    
    if 'no_defects' in config:
        rules['no_defects'].update(config['no_defects'])
    
    return rules
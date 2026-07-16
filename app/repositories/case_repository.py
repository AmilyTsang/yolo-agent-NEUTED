import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.core.constants import CACHE_DIR
from app.core.logging import logger

class CaseRepository:
    def __init__(self):
        self.storage_dir = os.path.join(CACHE_DIR, 'cases')
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def save_case(self, case_data: Dict[str, Any]) -> str:
        try:
            case_id = case_data.get('case_id', str(hash(json.dumps(case_data, sort_keys=True))))
            filepath = os.path.join(self.storage_dir, f"{case_id}.json")
            case_data['created_at'] = datetime.now().isoformat()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(case_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"案例保存成功: {case_id}")
            return case_id
        except Exception as e:
            logger.error(f"保存案例失败: {str(e)}")
            return ''
    
    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        try:
            filepath = os.path.join(self.storage_dir, f"{case_id}.json")
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取案例失败: {str(e)}")
            return None
    
    def search_cases(self, defect_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            files = os.listdir(self.storage_dir)
            cases = []
            
            for filename in files:
                if filename.endswith('.json'):
                    filepath = os.path.join(self.storage_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        case = json.load(f)
                        if case.get('defect_type') == defect_type:
                            cases.append(case)
            
            cases.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return cases[:limit]
        except Exception as e:
            logger.error(f"搜索案例失败: {str(e)}")
            return []
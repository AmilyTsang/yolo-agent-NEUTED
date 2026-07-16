import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.core.constants import CACHE_DIR
from app.core.logging import logger

class ReviewRepository:
    def __init__(self):
        self.storage_dir = os.path.join(CACHE_DIR, 'reviews')
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def save_review(self, file_id: str, review_data: Dict[str, Any]) -> bool:
        try:
            filepath = os.path.join(self.storage_dir, f"{file_id}.json")
            review_data['reviewed_at'] = datetime.now().isoformat()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(review_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"审核记录保存成功: {file_id}")
            return True
        except Exception as e:
            logger.error(f"保存审核记录失败: {str(e)}")
            return False
    
    def get_review(self, file_id: str) -> Optional[Dict[str, Any]]:
        try:
            filepath = os.path.join(self.storage_dir, f"{file_id}.json")
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取审核记录失败: {str(e)}")
            return None
    
    def list_reviews(self, status: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            files = sorted(os.listdir(self.storage_dir), reverse=True)[:limit]
            reviews = []
            
            for filename in files:
                if filename.endswith('.json'):
                    file_id = filename[:-5]
                    review = self.get_review(file_id)
                    if review:
                        if status is None or review.get('status') == status:
                            reviews.append(review)
            
            return reviews
        except Exception as e:
            logger.error(f"列出审核记录失败: {str(e)}")
            return []
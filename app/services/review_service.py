from typing import Dict, Any, Optional

from app.repositories.review_repository import ReviewRepository
from app.repositories.detection_repository import DetectionRepository
from app.core.logging import logger

class ReviewService:
    def __init__(self):
        self.review_repo = ReviewRepository()
        self.detection_repo = DetectionRepository()
    
    def create_review(self, file_id: str, user_id: str, 
                     decision: str, comment: str = '') -> Dict[str, Any]:
        logger.info(f"创建审核记录: file_id={file_id}, user_id={user_id}, decision={decision}")
        
        detection_data = self.detection_repo.get_detection(file_id)
        
        review_data = {
            'file_id': file_id,
            'user_id': user_id,
            'decision': decision,
            'comment': comment,
            'detection_summary': {
                'total_defects': len(detection_data.get('fused_results', [])) if detection_data else 0
            }
        }
        
        success = self.review_repo.save_review(file_id, review_data)
        
        return {
            'success': success,
            'file_id': file_id,
            'decision': decision
        }
    
    def get_review_status(self, file_id: str) -> Optional[Dict[str, Any]]:
        return self.review_repo.get_review(file_id)
    
    def list_pending_reviews(self, limit: int = 20) -> list:
        return self.review_repo.list_reviews(status='pending', limit=limit)
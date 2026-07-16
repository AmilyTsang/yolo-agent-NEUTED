import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.core.constants import CACHE_DIR
from app.core.logging import logger

class DetectionRepository:
    def __init__(self):
        self.storage_dir = os.path.join(CACHE_DIR, 'detections')
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def save_detection(self, file_id: str, detection_data: Dict[str, Any]) -> bool:
        try:
            filepath = os.path.join(self.storage_dir, f"{file_id}.json")
            detection_data['saved_at'] = datetime.now().isoformat()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(detection_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"检测结果保存成功: {file_id}")
            return True
        except Exception as e:
            logger.error(f"保存检测结果失败: {str(e)}")
            return False
    
    def get_detection(self, file_id: str) -> Optional[Dict[str, Any]]:
        try:
            filepath = os.path.join(self.storage_dir, f"{file_id}.json")
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取检测结果失败: {str(e)}")
            return None
    
    def delete_detection(self, file_id: str) -> bool:
        try:
            filepath = os.path.join(self.storage_dir, f"{file_id}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"检测结果删除成功: {file_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"删除检测结果失败: {str(e)}")
            return False
    
    def list_detections(self, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            files = sorted(os.listdir(self.storage_dir), reverse=True)[:limit]
            detections = []
            
            for filename in files:
                if filename.endswith('.json'):
                    file_id = filename[:-5]
                    detection = self.get_detection(file_id)
                    if detection:
                        detections.append(detection)
            
            return detections
        except Exception as e:
            logger.error(f"列出检测结果失败: {str(e)}")
            return []
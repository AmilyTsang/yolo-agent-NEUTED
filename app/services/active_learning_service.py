import os
import json
from datetime import datetime
from typing import List, Dict, Any

from app.core.constants import DATASETS_DIR, UPLOADS_DIR
from app.core.logging import logger

class ActiveLearningService:
    def __init__(self):
        self.pending_dir = os.path.join(DATASETS_DIR, 'active_learning', 'pending')
        self.reviewed_dir = os.path.join(DATASETS_DIR, 'active_learning', 'reviewed')
        self.rejected_dir = os.path.join(DATASETS_DIR, 'active_learning', 'rejected')
        
        os.makedirs(self.pending_dir, exist_ok=True)
        os.makedirs(self.reviewed_dir, exist_ok=True)
        os.makedirs(self.rejected_dir, exist_ok=True)
    
    def add_to_pending(self, file_id: str, image_path: str, 
                      detection_result: Dict[str, Any]) -> bool:
        try:
            filename = os.path.basename(image_path)
            pending_path = os.path.join(self.pending_dir, filename)
            
            if not os.path.exists(image_path):
                logger.warning(f"源文件不存在: {image_path}")
                return False
            
            import shutil
            shutil.copy2(image_path, pending_path)
            
            metadata = {
                'file_id': file_id,
                'image_path': pending_path,
                'detection_result': detection_result,
                'added_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            metadata_path = os.path.join(self.pending_dir, f"{file_id}_metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"添加到主动学习队列: {file_id}")
            return True
        except Exception as e:
            logger.error(f"添加到主动学习队列失败: {str(e)}")
            return False
    
    def accept_case(self, file_id: str, user_label: str = '') -> bool:
        try:
            metadata_path = os.path.join(self.pending_dir, f"{file_id}_metadata.json")
            if not os.path.exists(metadata_path):
                logger.warning(f"元数据文件不存在: {file_id}")
                return False
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            image_path = metadata['image_path']
            filename = os.path.basename(image_path)
            
            import shutil
            shutil.move(image_path, os.path.join(self.reviewed_dir, filename))
            shutil.move(metadata_path, os.path.join(self.reviewed_dir, f"{file_id}_metadata.json"))
            
            metadata['status'] = 'reviewed'
            metadata['user_label'] = user_label
            metadata['reviewed_at'] = datetime.now().isoformat()
            
            reviewed_metadata_path = os.path.join(self.reviewed_dir, f"{file_id}_metadata.json")
            with open(reviewed_metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"接受案例: {file_id}, 标签: {user_label}")
            return True
        except Exception as e:
            logger.error(f"接受案例失败: {str(e)}")
            return False
    
    def reject_case(self, file_id: str, reason: str = '') -> bool:
        try:
            metadata_path = os.path.join(self.pending_dir, f"{file_id}_metadata.json")
            if not os.path.exists(metadata_path):
                logger.warning(f"元数据文件不存在: {file_id}")
                return False
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            image_path = metadata['image_path']
            filename = os.path.basename(image_path)
            
            import shutil
            shutil.move(image_path, os.path.join(self.rejected_dir, filename))
            shutil.move(metadata_path, os.path.join(self.rejected_dir, f"{file_id}_metadata.json"))
            
            metadata['status'] = 'rejected'
            metadata['reject_reason'] = reason
            metadata['rejected_at'] = datetime.now().isoformat()
            
            rejected_metadata_path = os.path.join(self.rejected_dir, f"{file_id}_metadata.json")
            with open(rejected_metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"拒绝案例: {file_id}, 原因: {reason}")
            return True
        except Exception as e:
            logger.error(f"拒绝案例失败: {str(e)}")
            return False
    
    def get_pending_count(self) -> int:
        try:
            files = [f for f in os.listdir(self.pending_dir) if f.endswith('_metadata.json')]
            return len(files)
        except Exception as e:
            logger.error(f"获取待处理数量失败: {str(e)}")
            return 0
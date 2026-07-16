import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.constants import (
    MODELS_DIR, KNOWLEDGE_DIR, DATASETS_DIR, RUNTIME_DIR,
    UPLOADS_DIR, REPORTS_DIR, CACHE_DIR, LOGS_DIR
)
from app.core.logging import setup_logging

logger = setup_logging('init_project')

def main():
    logger.info("初始化项目目录结构...")
    
    directories = [
        MODELS_DIR,
        os.path.join(MODELS_DIR, 'yolo'),
        os.path.join(MODELS_DIR, 'qwen', 'base'),
        os.path.join(MODELS_DIR, 'qwen', 'adapters'),
        KNOWLEDGE_DIR,
        os.path.join(KNOWLEDGE_DIR, 'raw', 'enterprise_standard'),
        os.path.join(KNOWLEDGE_DIR, 'raw', 'historical_cases'),
        os.path.join(KNOWLEDGE_DIR, 'raw', 'repair_guidelines'),
        os.path.join(KNOWLEDGE_DIR, 'raw', 'defect_manual'),
        os.path.join(KNOWLEDGE_DIR, 'processed'),
        os.path.join(KNOWLEDGE_DIR, 'indexes'),
        DATASETS_DIR,
        os.path.join(DATASETS_DIR, 'raw', 'neu_det'),
        os.path.join(DATASETS_DIR, 'interim'),
        os.path.join(DATASETS_DIR, 'processed', 'yolo'),
        os.path.join(DATASETS_DIR, 'processed', 'qwen'),
        os.path.join(DATASETS_DIR, 'active_learning', 'pending'),
        os.path.join(DATASETS_DIR, 'active_learning', 'reviewed'),
        os.path.join(DATASETS_DIR, 'active_learning', 'rejected'),
        RUNTIME_DIR,
        UPLOADS_DIR,
        REPORTS_DIR,
        CACHE_DIR,
        LOGS_DIR
    ]
    
    for dir_path in directories:
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"创建目录: {dir_path}")
    
    logger.info("项目初始化完成！")

if __name__ == '__main__':
    main()
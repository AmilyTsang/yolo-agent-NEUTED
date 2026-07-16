import logging
import os
import sys
from datetime import datetime
from typing import Optional

from app.core.constants import LOGS_DIR

def setup_logging(
    name: str = 'defect_agent',
    log_level: str = 'INFO',
    log_file: Optional[str] = None
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    if log_file:
        file_path = os.path.join(LOGS_DIR, log_file)
    else:
        timestamp = datetime.now().strftime('%Y%m%d')
        file_path = os.path.join(LOGS_DIR, f'{name}_{timestamp}.log')
    
    file_handler = logging.FileHandler(file_path, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()
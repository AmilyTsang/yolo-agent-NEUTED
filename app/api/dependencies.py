import os
import uuid
from typing import Optional

from flask import request

from app.core.config import get_all_configs
from app.core.constants import ALLOWED_EXTENSIONS, UPLOADS_DIR, REPORTS_DIR
from app.core.logging import logger

analysis_cache = {}

def validate_file_extension(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(image_file) -> Optional[str]:
    if not image_file or image_file.filename == '':
        return None
    
    if not validate_file_extension(image_file.filename):
        return None
    
    file_id = str(uuid.uuid4())
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    
    image_path = os.path.join(UPLOADS_DIR, f"{file_id}_{image_file.filename}")
    image_file.save(image_path)
    
    logger.info(f"文件上传成功: {image_path}")
    return file_id, image_path

def get_uploaded_file_path(file_id: str) -> Optional[str]:
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    image_files = [f for f in os.listdir(UPLOADS_DIR) if f.startswith(file_id)]
    
    if not image_files:
        return None
    
    return os.path.join(UPLOADS_DIR, image_files[0])

def get_config():
    return get_all_configs()

def get_cache_entry(file_id: str):
    return analysis_cache.get(file_id)

def set_cache_entry(file_id: str, data: dict):
    analysis_cache[file_id] = data

def remove_cache_entry(file_id: str):
    if file_id in analysis_cache:
        del analysis_cache[file_id]
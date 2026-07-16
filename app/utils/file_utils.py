import os
import shutil
from typing import Optional

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def get_file_extension(filename: str) -> str:
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def get_filename_without_extension(filename: str) -> str:
    return filename.rsplit('.', 1)[0] if '.' in filename else filename

def file_exists(path: str) -> bool:
    return os.path.exists(path) and os.path.isfile(path)

def directory_exists(path: str) -> bool:
    return os.path.exists(path) and os.path.isdir(path)

def get_file_size(path: str) -> Optional[int]:
    if file_exists(path):
        return os.path.getsize(path)
    return None

def copy_file(src: str, dst: str) -> bool:
    try:
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False

def move_file(src: str, dst: str) -> bool:
    try:
        shutil.move(src, dst)
        return True
    except Exception:
        return False

def delete_file(path: str) -> bool:
    try:
        if file_exists(path):
            os.remove(path)
            return True
        return False
    except Exception:
        return False

def list_files(directory: str, extension: str = None) -> list:
    try:
        files = []
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                if extension is None or get_file_extension(filename) == extension:
                    files.append(filename)
        return files
    except Exception:
        return []
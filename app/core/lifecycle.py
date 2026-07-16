import os
from typing import Callable, List

from app.core.constants import UPLOADS_DIR, REPORTS_DIR, CACHE_DIR, LOGS_DIR
from app.core.logging import logger

_lifecycle_hooks = {
    'startup': [],
    'shutdown': []
}

def register_startup_hook(hook: Callable):
    _lifecycle_hooks['startup'].append(hook)

def register_shutdown_hook(hook: Callable):
    _lifecycle_hooks['shutdown'].append(hook)

def initialize_runtime_dirs():
    dirs = [UPLOADS_DIR, REPORTS_DIR, CACHE_DIR, LOGS_DIR]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"确保目录存在: {dir_path}")

def run_startup_hooks():
    logger.info("运行启动钩子...")
    initialize_runtime_dirs()
    
    for hook in _lifecycle_hooks['startup']:
        try:
            hook()
            logger.info(f"启动钩子执行成功: {hook.__name__}")
        except Exception as e:
            logger.error(f"启动钩子执行失败: {hook.__name__}, 错误: {str(e)}")

def run_shutdown_hooks():
    logger.info("运行关闭钩子...")
    for hook in _lifecycle_hooks['shutdown']:
        try:
            hook()
            logger.info(f"关闭钩子执行成功: {hook.__name__}")
        except Exception as e:
            logger.error(f"关闭钩子执行失败: {hook.__name__}, 错误: {str(e)}")
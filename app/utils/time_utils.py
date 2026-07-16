from datetime import datetime, timedelta
from typing import Optional

def get_current_timestamp() -> str:
    return datetime.now().isoformat()

def get_current_time_str(format_str: str = '%Y%m%d_%H%M%S') -> str:
    return datetime.now().strftime(format_str)

def get_current_date_str(format_str: str = '%Y-%m-%d') -> str:
    return datetime.now().strftime(format_str)

def format_timestamp(timestamp: str, format_str: str = '%Y年%m月%d日 %H:%M:%S') -> str:
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime(format_str)
    except Exception:
        return timestamp

def parse_timestamp(timestamp: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(timestamp)
    except Exception:
        return None

def get_time_delta(start_time: str, end_time: str) -> Optional[timedelta]:
    try:
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        return end - start
    except Exception:
        return None

def format_duration(duration: timedelta) -> str:
    hours = duration.seconds // 3600
    minutes = (duration.seconds % 3600) // 60
    seconds = duration.seconds % 60
    
    if hours > 0:
        return f"{hours}小时{minutes}分钟{seconds}秒"
    elif minutes > 0:
        return f"{minutes}分钟{seconds}秒"
    else:
        return f"{seconds}秒"
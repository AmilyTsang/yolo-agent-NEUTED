import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CONFIG_DIR = os.path.join(BASE_DIR, 'configs')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
KNOWLEDGE_DIR = os.path.join(BASE_DIR, 'knowledge')
DATASETS_DIR = os.path.join(BASE_DIR, 'datasets')
RUNTIME_DIR = os.path.join(BASE_DIR, 'runtime')
UPLOADS_DIR = os.path.join(RUNTIME_DIR, 'uploads')
REPORTS_DIR = os.path.join(RUNTIME_DIR, 'reports')
CACHE_DIR = os.path.join(RUNTIME_DIR, 'cache')
LOGS_DIR = os.path.join(RUNTIME_DIR, 'logs')

YOLO_MODEL_PATH = os.path.join(MODELS_DIR, 'yolo', 'best.pt')
QWEN_MODEL_DIR = os.path.join(MODELS_DIR, 'qwen', 'base')
QWEN_ADAPTERS_DIR = os.path.join(MODELS_DIR, 'qwen', 'adapters')

CONFIDENCE_THRESHOLD = 0.6
ROI_EXPANSION_RATIO = 0.2

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}
MAX_FILE_SIZE_MB = 16

DECISION_RESULTS = {
    'AUTO_PASS': 'auto_pass',
    'AUTO_REJECT': 'auto_reject',
    'MANUAL_REVIEW': 'manual_review',
    'PENDING': 'pending'
}

SEVERITY_LEVELS = {
    'HIGH': 'high',
    'MEDIUM': 'medium',
    'LOW': 'low'
}

DEFECT_TYPES = [
    'crazing',
    'inclusion',
    'patches',
    'pitted_surface',
    'rolled-in_scale',
    'scratches'
]

DEFECT_TYPE_MAP = {
    'crazing': '发丝纹',
    'inclusion': '夹杂',
    'patches': '斑块',
    'pitted_surface': '麻点',
    'rolled-in_scale': '氧化铁皮压入',
    'scratches': '划痕'
}

SEVERITY_MAP = {
    'high': '高',
    'medium': '中',
    'low': '低'
}

SEVERITY_BY_TYPE = {
    'crazing': 'medium',
    'inclusion': 'high',
    'patches': 'medium',
    'pitted_surface': 'low',
    'rolled-in_scale': 'medium',
    'scratches': 'low'
}
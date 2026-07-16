import os
import yaml
from typing import Dict, Any

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'configs')

class ConfigLoader:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._configs = {}
        return cls._instance
    
    def load_config(self, config_name: str) -> Dict[str, Any]:
        if config_name in self._configs:
            return self._configs[config_name]
        
        config_path = os.path.join(CONFIG_DIR, f'{config_name}.yaml')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        self._configs[config_name] = config
        return config
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        return {
            'yolo': self.load_config('yolo'),
            'qwen': self.load_config('qwen'),
            'rag': self.load_config('rag'),
            'decision_rules': self.load_config('decision_rules'),
            'system': self.load_config('system')
        }
    
    def reload(self):
        self._configs.clear()

config_loader = ConfigLoader()

def get_config(config_name: str) -> Dict[str, Any]:
    return config_loader.load_config(config_name)

def get_all_configs() -> Dict[str, Dict[str, Any]]:
    return config_loader.get_all_configs()
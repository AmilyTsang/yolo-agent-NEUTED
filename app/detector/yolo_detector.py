import os
import torch
from ultralytics import YOLO
from app.detector.base import BaseDetector
from app.detector.postprocess import parse_detections
from app.core.logging import logger

class YOLODetector(BaseDetector):
    def __init__(self, config):
        self.model_path = config['model']['path']
        self.conf_threshold = config['confidence']['threshold']
        self.iou_threshold = config['confidence']['iou_threshold']
        self.classes = config['classes']
        self.device = config['inference']['device']
        self.imgsz = config['inference']['imgsz']
        self.model = None
    
    def load_model(self):
        if self.model is None:
            try:
                self.model = YOLO(self.model_path)
                logger.info(f"YOLO模型加载成功: {self.model_path}")
            except Exception as e:
                logger.error(f"YOLO模型加载失败: {str(e)}")
                raise
    
    def detect(self, image_path):
        self.load_model()
        
        results = self.model(
            image_path,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            imgsz=self.imgsz,
            device=self.device
        )
        
        return results[0]
    
    def parse_results(self, results):
        return parse_detections(results, self.classes)
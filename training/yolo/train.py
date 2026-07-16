import os
import yaml
from ultralytics import YOLO

def train_yolo(config_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    model = YOLO('yolov8n.pt')
    
    model.train(
        data=config['data'],
        epochs=config['epochs'],
        imgsz=config['imgsz'],
        batch=config['batch'],
        device=config['device']
    )
    
    model.val()
    model.export(format='onnx')

if __name__ == '__main__':
    train_yolo('configs/yolo.yaml')
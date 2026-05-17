import os
import cv2
import numpy as np

class YOLODetector:
    def __init__(self):
        self.model = None
        self.classes = [
            '划痕', '裂纹', '凹陷', '凸起', '腐蚀', 
            '磨损', '变形', '污渍', '气泡', '断裂'
        ]
        self.colors = [
            (0, 0, 255),    # 红色 - 划痕
            (0, 255, 255),  # 黄色 - 裂纹
            (255, 0, 0),    # 蓝色 - 凹陷
            (0, 255, 0),    # 绿色 - 凸起
            (255, 255, 0),  # 青色 - 腐蚀
            (255, 0, 255),  # 品红 - 磨损
            (128, 0, 255),  # 紫色 - 变形
            (255, 128, 0),  # 橙色 - 污渍
            (0, 128, 255),  # 粉红 - 气泡
            (128, 128, 0)   # 橄榄 - 断裂
        ]
        
        # 尝试加载YOLO模型
        self._load_model()
    
    def _load_model(self):
        model_path = '../models/yolov8n.pt'
        try:
            from ultralytics import YOLO
            if os.path.exists(model_path):
                self.model = YOLO(model_path)
                print("YOLO模型加载成功")
            else:
                print("未找到YOLO模型文件，将使用模拟检测")
        except ImportError:
            print("未安装ultralytics，将使用模拟检测")
    
    def detect(self, image_path):
        """
        检测图像中的缺陷
        返回格式: [{
            'type': '划痕',
            'confidence': 0.85,
            'bbox': [x1, y1, x2, y2],
            'area': 1200
        }]
        """
        if self.model is not None:
            return self._detect_real(image_path)
        else:
            return self._detect_simulated(image_path)
    
    def _detect_real(self, image_path):
        """使用真实YOLO模型检测"""
        results = self.model(image_path)
        detections = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                if conf > 0.5:  # 置信度阈值
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    detections.append({
                        'type': self.classes[cls] if cls < len(self.classes) else '未知',
                        'confidence': conf,
                        'bbox': [x1, y1, x2, y2],
                        'area': (x2 - x1) * (y2 - y1)
                    })
        
        return detections
    
    def _detect_simulated(self, image_path):
        """模拟检测结果"""
        # 读取图像获取尺寸
        img = cv2.imread(image_path)
        if img is None:
            return []
        
        height, width = img.shape[:2]
        
        # 生成随机模拟缺陷
        import random
        np.random.seed(42)  # 固定种子以获得可预测的结果
        
        num_defects = random.randint(1, 3)
        detections = []
        
        defect_types = ['划痕', '裂纹', '凹陷', '腐蚀', '磨损']
        
        for _ in range(num_defects):
            defect_type = random.choice(defect_types)
            x1 = random.randint(50, width - 150)
            y1 = random.randint(50, height - 150)
            x2 = x1 + random.randint(50, 150)
            y2 = y1 + random.randint(30, 80)
            
            detections.append({
                'type': defect_type,
                'confidence': round(random.uniform(0.6, 0.95), 2),
                'bbox': [x1, y1, x2, y2],
                'area': (x2 - x1) * (y2 - y1)
            })
        
        return detections
    
    def draw_boxes(self, image_path, detections, output_path):
        """在图像上绘制检测框"""
        img = cv2.imread(image_path)
        if img is None:
            return
        
        for defect in detections:
            x1, y1, x2, y2 = defect['bbox']
            defect_type = defect['type']
            confidence = defect['confidence']
            
            # 获取颜色
            idx = self.classes.index(defect_type) if defect_type in self.classes else 9
            color = self.colors[idx]
            
            # 绘制矩形框
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            
            # 添加标签
            label = f"{defect_type} {confidence:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            label_y = max(y1, label_size[1] + 10)
            cv2.rectangle(img, (x1, label_y - label_size[1] - 10), 
                         (x1 + label_size[0], label_y), color, -1)
            cv2.putText(img, label, (x1, label_y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        cv2.imwrite(output_path, img)
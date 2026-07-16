import numpy as np

def parse_detections(results, class_names):
    detections = []
    
    if results.boxes is None:
        return detections
    
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        conf = float(box.conf[0])
        cls_id = int(box.cls[0])
        label = class_names[cls_id] if cls_id < len(class_names) else "unknown"
        
        detections.append({
            'defect_type': label,
            'confidence': conf,
            'bbox': [x1, y1, x2, y2],
            'area': (x2 - x1) * (y2 - y1)
        })
    
    return detections

def filter_detections(detections, min_confidence=0.0):
    return [d for d in detections if d['confidence'] >= min_confidence]

def group_by_type(detections):
    grouped = {}
    for det in detections:
        defect_type = det['defect_type']
        if defect_type not in grouped:
            grouped[defect_type] = []
        grouped[defect_type].append(det)
    return grouped

def calculate_statistics(detections):
    if not detections:
        return {'total': 0, 'types': {}, 'avg_confidence': 0}
    
    defect_counts = {}
    total_confidence = 0
    
    for det in detections:
        defect_type = det['defect_type']
        defect_counts[defect_type] = defect_counts.get(defect_type, 0) + 1
        total_confidence += det['confidence']
    
    return {
        'total': len(detections),
        'types': defect_counts,
        'avg_confidence': total_confidence / len(detections)
    }
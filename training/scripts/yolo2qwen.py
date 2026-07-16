import os
import json

def convert_yolo_to_qwen(yolo_labels_dir, images_dir, output_file):
    samples = []
    class_names = ['crazing', 'inclusion', 'patches', 'pitted_surface', 'rolled-in_scale', 'scratches']
    
    for label_file in os.listdir(yolo_labels_dir):
        if not label_file.endswith('.txt'):
            continue
        
        image_name = label_file.replace('.txt', '.jpg')
        image_path = os.path.join(images_dir, image_name)
        
        if not os.path.exists(image_path):
            continue
        
        with open(os.path.join(yolo_labels_dir, label_file), 'r') as f:
            lines = f.readlines()
        
        defects = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 5:
                class_id = int(parts[0])
                confidence = float(parts[5]) if len(parts) > 5 else 0.9
                defect_type = class_names[class_id] if class_id < len(class_names) else 'unknown'
                defects.append({'type': defect_type, 'confidence': confidence})
        
        if defects:
            sample = {
                'image_path': image_path,
                'defects': defects,
                'analysis': ''
            }
            samples.append(sample)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    convert_yolo_to_qwen('datasets/yolo/labels/train', 'datasets/yolo/images/train', 'datasets/qwen/train_raw.json')
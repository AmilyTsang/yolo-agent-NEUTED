import cv2
import numpy as np
from PIL import Image

def read_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return None
    return img

def convert_to_rgb(image):
    if len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def normalize_image(image):
    return image / 255.0

def image_to_pil(image):
    if isinstance(image, np.ndarray):
        if image.dtype == np.float32 or image.dtype == np.float64:
            image = (image * 255).astype(np.uint8)
        return Image.fromarray(image)
    return image

def crop_roi(image, bbox, expansion_ratio=0.2):
    width, height = image.size
    x1, y1, x2, y2 = bbox
    
    bbox_width = x2 - x1
    bbox_height = y2 - y1
    
    expand_x = int(bbox_width * expansion_ratio)
    expand_y = int(bbox_height * expansion_ratio)
    
    new_x1 = max(0, x1 - expand_x)
    new_y1 = max(0, y1 - expand_y)
    new_x2 = min(width, x2 + expand_x)
    new_y2 = min(height, y2 + expand_y)
    
    return image.crop((new_x1, new_y1, new_x2, new_y2))

def draw_bboxes(image, boxes, labels, colors=None):
    img = image.copy()
    if colors is None:
        colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 0, 255), (255, 255, 0)]
    
    for i, (box, label) in enumerate(zip(boxes, labels)):
        x1, y1, x2, y2 = box
        color = colors[i % len(colors)]
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        
        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
        label_y = max(y1, label_size[1] + 10)
        cv2.rectangle(img, (x1, label_y - label_size[1] - 10),
                     (x1 + label_size[0], label_y), color, -1)
        cv2.putText(img, label, (x1, label_y - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    
    return img
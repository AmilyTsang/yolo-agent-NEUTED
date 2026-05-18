#!/usr/bin/env python3
"""
YOLOv8 检测 + Qwen2-VL 分析流水线
功能：作为后端工具函数，接收图片路径，返回结构化 JSON 数据。
"""

import os
import json
import torch
import cv2
import warnings
from PIL import Image
from ultralytics import YOLO
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration
from peft import PeftModel

# ==================== 配置区域 ====================
YOLO_MODEL_PATH = "/root/autodl-tmp/yolo-agent-NEUTED/runs/detect/train5/weights/best.pt"
QWEN_BASE_MODEL = "/root/autodl-tmp/models/Qwen2-VL-2B-Instruct"
QWEN_LORA_PATH = ""  # 如有微调权重请填写
CLASS_NAMES = ['crazing', 'inclusion', 'patches', 'pitted_surface', 'rolled-in_scale', 'scratches']
# ===============================================

warnings.filterwarnings("ignore")

def load_models():
    """加载模型（按需加载，避免重复占用显存）"""
    yolo_model = YOLO(YOLO_MODEL_PATH)
    
    processor = AutoProcessor.from_pretrained(QWEN_BASE_MODEL, trust_remote_code=True)
    qwen_model = Qwen2VLForConditionalGeneration.from_pretrained(
        QWEN_BASE_MODEL,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True
    )
    
    if QWEN_LORA_PATH and os.path.exists(QWEN_LORA_PATH):
        qwen_model = PeftModel.from_pretrained(qwen_model, QWEN_LORA_PATH)
    
    qwen_model.eval()
    return yolo_model, qwen_model, processor

def analyze_defect_region(model, processor, crop_image, defect_label):
    """调用 Qwen 分析缺陷，返回结构化文本"""
    messages = [
        {"role": "system", "content": "你是宝钢热轧产线资深工程师。回答要极度精简，直击要害，不要教科书式废话，必须给出可执行的工艺建议。"},
        {"role": "user", "content": [
            {"type": "image", "image": crop_image},
            {"type": "text", "text": f"缺陷类型: {defect_label}。\n请按以下格式输出：\n1. 产线成因：(不超过20字)\n2. 解决措施：(不超过20字)\n3. 预防建议：(不超过20字)"}
        ]}
    ]
    
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=text, images=crop_image, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=200, do_sample=False)
    
    response = processor.decode(outputs[0], skip_special_tokens=True)
    if "assistant" in response:
        response = response.split("assistant")[-1].strip()
    
    # 解析结构化数据
    lines = response.split('\n')
    result = {"成因": "文档未详述", "措施": "文档未详述", "建议": "文档未详述"}
    for line in lines:
        if "成因" in line: result["成因"] = line.split("：")[-1].strip()
        if "措施" in line: result["措施"] = line.split("：")[-1].strip()
        if "建议" in line: result["建议"] = line.split("：")[-1].strip()
    
    return result

def run_pipeline(image_path: str) -> dict:
    """
    主入口函数，供 backend/app.py 调用。
    返回标准 JSON 字典，无多余打印。
    """
    try:
        yolo_model, qwen_model, processor = load_models()
        
        # 1. YOLO 检测
        results = yolo_model(image_path)[0]
        orig_img = cv2.imread(image_path)
        if orig_img is None:
            return {"success": False, "error": "无法读取图片文件"}
            
        h, w = orig_img.shape[:2]
        detections = results.boxes
        
        if detections is None or len(detections) == 0:
            return {"success": True, "defects": [], "analysis": []}
        
        defects_list = []
        analysis_list = []
        
        # 2. 遍历分析
        for i, box in enumerate(detections):
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            
            # 裁剪
            y1c, y2c = max(0, y1), min(h, y2)
            x1c, x2c = max(0, x1), min(w, x2)
            crop_img = orig_img[y1c:y2c, x1c:x2c]
            pil_crop = Image.fromarray(cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB))
            
            label = CLASS_NAMES[cls_id] if cls_id < len(CLASS_NAMES) else "unknown"
            
            # 3. Qwen 分析
            analysis_result = analyze_defect_region(qwen_model, processor, pil_crop, label)
            
            # 4. 组装数据
            defect_info = {
                "类别": label,
                "坐标": [x1, y1, x2, y2],
                "置信度": round(conf, 3),
                "详细分析": analysis_result
            }
            defects_list.append(defect_info)
            
            analysis_item = {
                "缺陷编号": f"缺陷{i+1}",
                "类型": label,
                "分析": analysis_result
            }
            analysis_list.append(analysis_item)
            
        return {
            "success": True,
            "defects": defects_list,
            "analysis": analysis_list
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
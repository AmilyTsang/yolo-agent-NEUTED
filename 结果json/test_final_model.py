#!/usr/bin/env python3
"""
最终模型验证脚本
功能：1. 单张图片推理演示  2. 批量测试计算指标 (TP, FP, FN, F1)
格式：严格遵循 Qwen2-VL 官方 messages 格式
"""

import os
import json
import re
import torch
from PIL import Image
from transformers import Qwen2VLForConditionalGeneration, Qwen2VLProcessor, AutoProcessor
from peft import PeftModel

# ==================== 配置区域 ====================
BASE_MODEL_PATH = "/root/autodl-tmp/models/Qwen2-VL-2B-Instruct"
LORA_PATH      = "./qwen_detection_lora_final/final"  # 你训练好的 LoRA 权重目录
TEST_IMG_DIR   = "/root/autodl-tmp/yolo-agent-NEUTED/NEU-DET/test/images"
TEST_LABEL_DIR = "/root/autodl-tmp/yolo-agent-NEUTED/NEU-DET/test/labels"
OUTPUT_JSON    = "final_evaluation_results.json"

# 类别列表（用于匹配）
CATEGORIES = ['crazing', 'inclusion', 'patches', 'pitted_surface', 'rolled-in_scale', 'scratches']
IOU_THRESHOLD = 0.5
# =================================================

def parse_predicted_boxes(text):
    """
    从模型输出文本中提取预测框。
    匹配格式：缺陷1: crazing | (91,21)-(134,106) | 原因: ... | 建议: ...
    """
    boxes = []
    # 正则：捕获 "缺陷X: 类别 | (x1,y1)-(x2,y2)"
    pattern = r'缺陷\d+:\s*(\w+)\s*\|\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)-\(\s*(\d+)\s*,\s*(\d+)\s*\)'
    matches = re.findall(pattern, text)
    
    for match in matches:
        cat_str = match[0].lower()
        # 映射到标准类别名
        cat = None
        for c in CATEGORIES:
            if c in cat_str:  # 简单的包含匹配
                cat = c
                break
        if cat is None:
            continue
            
        x1, y1, x2, y2 = int(match[1]), int(match[2]), int(match[3]), int(match[4])
        boxes.append((cat, x1, y1, x2, y2))
    return boxes

def read_yolo_labels(label_path, img_w, img_h):
    """读取 YOLO 格式的 Ground Truth"""
    boxes = []
    if not os.path.exists(label_path):
        return boxes
    with open(label_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 5: continue
            cls_id = int(parts[0])
            # NEU-DET 标签通常从 1 开始，或者 0 开始，这里假设 0 开始
            # 如果你的标签是 1-6，需要 cls_id - 1
            cat = CATEGORIES[int(cls_id)]
            x_center = float(parts[1]) * img_w
            y_center = float(parts[2]) * img_h
            width = float(parts[3]) * img_w
            height = float(parts[4]) * img_h
            
            x1 = int(x_center - width / 2)
            y1 = int(y_center - height / 2)
            x2 = int(x_center + width / 2)
            y2 = int(y_center + height / 2)
            boxes.append((cat, x1, y1, x2, y2))
    return boxes

def calculate_iou(box1, box2):
    """计算 IoU"""
    x1, y1, x2, y2 = box1
    x1g, y1g, x2g, y2g = box2
    
    xi1 = max(x1, x1g)
    yi1 = max(y1, y1g)
    xi2 = min(x2, x2g)
    yi2 = min(y2, y2g)
    
    inter = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    area1 = (x2 - x1) * (y2 - y1)
    area2 = (x2g - x1g) * (y2g - y1g)
    union = area1 + area2 - inter
    return inter / union if union > 0 else 0.0

def load_model_and_processor():
    """加载微调后的模型"""
    print("🚀 加载模型中...")
    processor = AutoProcessor.from_pretrained(BASE_MODEL_PATH, trust_remote_code=True)
    
    # 1. 加载基础模型
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        BASE_MODEL_PATH,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True
    )
    
    # 2. 加载 LoRA 权重
    print(f"📦 加载 LoRA 权重: {LORA_PATH}")
    model = PeftModel.from_pretrained(model, LORA_PATH)
    model.eval()
    print("✅ 模型加载完成！")
    return model, processor

def predict_single_image(model, processor, image_path):
    """对单张图片进行推理"""
    image = Image.open(image_path).convert("RGB")
    
    # 构造官方格式的 messages
    messages = [
        {"role": "system", "content": "你是一名专业的钢铁表面缺陷检测专家。请根据图片识别缺陷，并按‘缺陷编号: 类别 | 坐标 | 原因 | 建议’的格式输出。"},
        {"role": "user", "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": "请检测这张图片中的所有钢材表面缺陷，给出类别、位置、原因分析及预防建议。"}
        ]}
    ]
    
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=text, images=image, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=False,  # 推理时不采样，保证输出稳定
        )
    
    response = processor.decode(outputs[0], skip_special_tokens=True)
    
    # 提取 Assistant 的回复部分
    if "assistant" in response:
        response = response.split("assistant")[-1].strip()
    
    return response

def batch_evaluate(model, processor):
    """批量评估"""
    print(f"\n📊 开始批量评估...")
    img_files = [f for f in os.listdir(TEST_IMG_DIR) if f.lower().endswith(('.jpg', '.png'))]
    
    total_tp, total_fp, total_fn = 0, 0, 0
    details = []
    
    for idx, img_file in enumerate(img_files):
        img_path = os.path.join(TEST_IMG_DIR, img_file)
        label_path = os.path.join(TEST_LABEL_DIR, img_file.replace('.jpg', '.txt').replace('.png', '.txt'))
        
        # 1. 预测
        response = predict_single_image(model, processor, img_path)
        pred_boxes = parse_predicted_boxes(response)
        
        # 2. 读取 GT
        img = Image.open(img_path)
        img_w, img_h = img.size
        gt_boxes = read_yolo_labels(label_path, img_w, img_h)
        
        # 3. 计算指标 (一对一匹配，简化版)
        matched_gt = set()
        tp, fp, fn = 0, 0, 0
        
        for pb in pred_boxes:
            cat_p, *box_p = pb
            best_iou = 0
            best_idx = -1
            for i, gb in enumerate(gt_boxes):
                cat_g, *box_g = gb
                if cat_p != cat_g: continue
                cur_iou = calculate_iou(box_p, box_g)
                if cur_iou > best_iou:
                    best_iou = cur_iou
                    best_idx = i
            
            if best_iou >= IOU_THRESHOLD and best_idx != -1:
                tp += 1
                matched_gt.add(best_idx)
            else:
                fp += 1
                
        fn = len(gt_boxes) - len(matched_gt)
        total_tp += tp
        total_fp += fp
        total_fn += fn
        
        details.append({
            "image": img_file,
            "prediction": response,
            "pred_boxes": [p[0] for p in pred_boxes],
            "gt_boxes": [g[0] for g in gt_boxes],
            "tp": tp, "fp": fp, "fn": fn
        })
        
        if (idx + 1) % 10 == 0:
            print(f"  处理进度: {idx+1}/{len(img_files)}")
            
    # 4. 汇总结果
    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "metrics": {"TP": total_tp, "FP": total_fp, "FN": total_fn, "Precision": precision, "Recall": recall, "F1": f1},
        "details": details
    }

def main():
    # 1. 加载模型
    model, processor = load_model_and_processor()
    
    # 2. 单张图片演示 (可选)
    print("\n" + "="*60)
    print("🖼️  单张图片推理演示:")
    demo_img = os.path.join(TEST_IMG_DIR, "crazing_13.jpg") # 随便挑一张
    if os.path.exists(demo_img):
        res = predict_single_image(model, processor, demo_img)
        print(res)
    else:
        print("未找到演示图片，跳过。")
    print("="*60)
    
    # 3. 批量评估
    results = batch_evaluate(model, processor)
    
    # 4. 打印结果
    print("\n" + "="*60)
    print("📈 最终评估结果:")
    m = results["metrics"]
    print(f"TP: {m['TP']}, FP: {m['FP']}, FN: {m['FN']}")
    print(f"Precision: {m['Precision']:.4f}")
    print(f"Recall: {m['Recall']:.4f}")
    print(f"F1 Score: {m['F1']:.4f}")
    print("="*60)
    
    # 5. 保存结果
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"💾 详细结果已保存至: {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
    
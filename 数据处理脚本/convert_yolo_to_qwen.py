#!/usr/bin/env python3
"""
NEU-DET YOLO 格式转 Qwen2-VL 微调数据格式 (最终版)
特点：紧凑的单行输出，包含编号、坐标、原因及建议。
"""

import os
import json
import cv2
import argparse
from pathlib import Path

# NEU-DET 数据集的6个缺陷类别
NEU_DET_CLASSES = [
    'crazing',          # 裂纹
    'inclusion',        # 夹杂
    'patches',          # 斑块
    'pitted_surface',   # 点蚀表面
    'rolled-in_scale',  # 轧制氧化皮
    'scratches'         # 划痕
]

def generate_defect_analysis(boxes_info):
    """
    生成结构化的缺陷分析文本。
    格式：缺陷1: [类别 | 坐标 | 原因 | 建议]; 缺陷2: [...]
    """
    if not boxes_info:
        return "检测结果: 未发现明显缺陷。"

    results = []
    for i, box in enumerate(boxes_info, 1):
        bbox = box["bbox"]
        label = box["label"]
        x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]
        
        # 1. 原因分析库
        reasons = {
            "crazing": "表面出现网状裂纹，通常由冷却不当或材料内部应力集中引起",
            "inclusion": "表面含有非金属夹杂物，源于冶炼或连铸工艺控制不当",
            "patches": "表面出现不规则斑块，多由氧化皮脱落不均或局部腐蚀造成",
            "pitted_surface": "表面存在点状凹坑，通常是酸洗或轧制过程中的局部腐蚀所致",
            "rolled-in_scale": "氧化皮在轧制过程中被压入钢体表面，因除鳞不彻底导致",
            "scratches": "表面存在线性划痕，多为运输或加工过程中机械接触损伤"
        }
        
        # 2. 预防建议库
        suggestions = {
            "crazing": "优化冷却工艺，控制冷却速率均匀性，进行应力消除退火",
            "inclusion": "加强炼钢过程渣系控制，提高纯净度，优化连铸保护浇注",
            "patches": "定期清理轧辊和导卫，优化乳化液浓度与喷射压力",
            "pitted_surface": "严格控制酸洗工艺参数，确保轧辊表面光洁度",
            "rolled-in_scale": "强化高压水除鳞效果，优化加热炉气氛控制",
            "scratches": "检查生产线导槽与辊道，消除尖锐棱角，规范吊装操作"
        }
        
        reason = reasons.get(label, "未知原因")
        suggestion = suggestions.get(label, "建议检查生产工艺")
        
        # 3. 组合成紧凑字符串 (使用 | 分隔不同字段，不使用换行符)
        # 格式：缺陷1: crazing | (1,9)-(108,121) | 原因: ... | 建议: ...
        result_str = f"缺陷{i}: {label} | ({x1},{y1})-({x2},{y2}) | 原因: {reason} | 建议: {suggestion}"
        results.append(result_str)
    
    # 多个缺陷用分号分隔
    return "; ".join(results)

def convert_single_split(yolo_images_dir, yolo_labels_dir, output_jsonl, split_name):
    """
    转换单个数据集划分（train/valid/test）
    """
    data_list = []
    
    if not os.path.exists(yolo_images_dir):
        print(f"❌ 错误: 图片目录不存在: {yolo_images_dir}")
        return 0
        
    if not os.path.exists(yolo_labels_dir):
        print(f"❌ 错误: 标签目录不存在: {yolo_labels_dir}")
        return 0
    
    # 获取所有图片文件
    image_files = []
    for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        image_files.extend(list(Path(yolo_images_dir).glob(f'*{ext}')))
    
    print(f"🔍 在 {split_name} 中发现 {len(image_files)} 张图片")
    
    for img_path in image_files:
        # 获取对应的标签文件路径
        label_path = Path(yolo_labels_dir) / f"{img_path.stem}.txt"
        
        if not label_path.exists():
            continue
        
        # 读取图片尺寸
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"⚠️ 警告: 无法读取图片 {img_path}")
            continue
            
        h, w, _ = img.shape
        
        # 读取YOLO标注
        boxes_info = []
        with open(label_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split()
                if len(parts) != 5:
                    continue
                    
                cls_id = int(parts[0])
                x_center, y_center, width, height = map(float, parts[1:])
                
                # 转换为像素坐标 [x1, y1, x2, y2]
                x1 = int((x_center - width / 2) * w)
                y1 = int((y_center - height / 2) * h)
                x2 = int((x_center + width / 2) * w)
                y2 = int((y_center + height / 2) * h)
                
                # 防止越界
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                
                if cls_id < len(NEU_DET_CLASSES):
                    class_name = NEU_DET_CLASSES[cls_id]
                else:
                    class_name = f"unknown_{cls_id}"
                
                boxes_info.append({
                    "bbox": [x1, y1, x2, y2],
                    "label": class_name
                })
        
        if not boxes_info:
            continue
        
        # === 构建 Qwen2-VL 训练对话格式 ===
        relative_img_path = str(img_path).replace('\\', '/')
        
        # 调用新的生成函数
        assistant_response = generate_defect_analysis(boxes_info)
        
        messages = [
            {
                "role": "system",
                "content": "你是一名专业的钢铁表面缺陷检测专家。请根据图片识别缺陷，并按‘缺陷编号: 类别 | 坐标 | 原因 | 建议’的格式输出。"
            },
            {
                "role": "user",
                "content": f"<|image|>{relative_img_path}\n请检测这张图片中的所有钢材表面缺陷，给出类别、位置、原因分析及预防建议。"
            },
            {
                "role": "assistant",
                "content": assistant_response
            }
        ]
        
        data_item = {
            "id": img_path.stem,
            "image": relative_img_path,
            "conversations": messages
        }
        
        data_list.append(data_item)
    
    # 写入JSONL文件
    with open(output_jsonl, 'w', encoding='utf-8') as f:
        for item in data_list:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"✅ {split_name} 转换完成! 共 {len(data_list)} 个样本")
    print(f"📄 输出文件: {output_jsonl}")
    
    return len(data_list)

def main():
    parser = argparse.ArgumentParser(description="NEU-DET YOLO格式转Qwen2-VL微调数据格式 (最终版)")
    parser.add_argument("--data_root", type=str, default="NEU-DET", 
                       help="NEU-DET数据集根目录")
    parser.add_argument("--output_dir", type=str, default=".", 
                       help="输出目录（默认为当前目录）")
    parser.add_argument("--splits", nargs="+", default=["train", "valid", "test"],
                       help="要转换的数据集划分")
    
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    total_samples = 0
    
    print("🚀 开始转换 NEU-DET 数据集到 Qwen2-VL 格式...")
    print(f"📁 数据集根目录: {args.data_root}")
    print(f"📁 输出目录: {args.output_dir}")
    print("-" * 50)
    
    for split in args.splits:
        yolo_images_dir = os.path.join(args.data_root, split, "images")
        yolo_labels_dir = os.path.join(args.data_root, split, "labels")
        output_jsonl = os.path.join(args.output_dir, f"qwen_finetune_{split}.jsonl")
        
        count = convert_single_split(yolo_images_dir, yolo_labels_dir, output_jsonl, split)
        total_samples += count
    
    print("-" * 50)
    print(f"🎉 转换完成! 总共生成 {total_samples} 个训练样本")
    print("\n📋 生成的文件:")
    for split in args.splits:
        output_file = os.path.join(args.output_dir, f"qwen_finetune_{split}.jsonl")
        if os.path.exists(output_file):
            print(f"   - {output_file}")

if __name__ == "__main__":
    main()
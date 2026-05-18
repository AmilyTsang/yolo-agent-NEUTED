#!/usr/bin/env python3
"""
NEU-DET YOLO 格式转 Qwen2-VL 微调数据格式
适用于 yolo-agent-NEUTED 项目结构
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

def convert_single_split(yolo_images_dir, yolo_labels_dir, output_jsonl, split_name):
    """
    转换单个数据集划分（train/valid/test）
    
    Args:
        yolo_images_dir: YOLO格式图片目录
        yolo_labels_dir: YOLO格式标签目录
        output_jsonl: 输出的JSONL文件路径
        split_name: 数据集划分名称（用于日志）
    """
    data_list = []
    
    # 确保目录存在
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
            # 如果没有标签文件，跳过（可能是负样本）
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
                
                # 获取类别名称
                if cls_id < len(NEU_DET_CLASSES):
                    class_name = NEU_DET_CLASSES[cls_id]
                else:
                    class_name = f"unknown_{cls_id}"
                
                boxes_info.append({
                    "bbox": [x1, y1, x2, y2],
                    "label": class_name
                })
        
        # 如果没有检测到框，跳过
        if not boxes_info:
            continue
        
        # === 构建 Qwen2-VL 训练对话格式 ===
        # 使用相对路径（相对于项目根目录）
        relative_img_path = str(img_path).replace('\\', '/')
        
        # 构建消息列表
        messages = [
            {
                "role": "system",
                "content": "你是一名专业的钢铁表面缺陷检测专家。请根据图片准确识别缺陷类型、位置和严重程度。"
            },
            {
                "role": "user",
                "content": f"<|image|>{relative_img_path}\n请分析这张钢铁表面图片，识别所有缺陷并给出详细分析。"
            },
            {
                "role": "assistant",
                "content": generate_defect_analysis(boxes_info, relative_img_path)
            }
        ]
        
        # 构建JSONL条目
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

def generate_defect_analysis(boxes_info, img_path):
    """生成缺陷分析的文本内容"""
    if not boxes_info:
        return "图片中未发现明显缺陷。"
    
    analysis = f"在这张钢铁表面图片中，检测到 {len(boxes_info)} 处缺陷：\n\n"
    
    for i, box in enumerate(boxes_info, 1):
        bbox = box["bbox"]
        label = box["label"]
        
        # 计算缺陷面积占比
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        
        analysis += f"{i}. **{label}**\n"
        analysis += f"   - 位置坐标: [{bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}]\n"
        analysis += f"   - 缺陷面积: {area} 像素\n"
        
        # 根据缺陷类型添加专业分析
        if label == "crazing":
            analysis += f"   - 分析: 表面出现网状裂纹，通常由冷却不当或材料应力引起。\n"
        elif label == "inclusion":
            analysis += f"   - 分析: 表面含有非金属夹杂物，可能影响材料强度和表面质量。\n"
        elif label == "patches":
            analysis += f"   - 分析: 表面出现不规则斑块，可能是氧化皮脱落或腐蚀造成。\n"
        elif label == "pitted_surface":
            analysis += f"   - 分析: 表面有点状凹坑，通常由腐蚀或制造过程中的缺陷导致。\n"
        elif label == "rolled-in_scale":
            analysis += f"   - 分析: 轧制过程中氧化皮压入表面，影响表面光洁度。\n"
        elif label == "scratches":
            analysis += f"   - 分析: 表面存在划痕，可能是运输或加工过程中造成的机械损伤。\n"
        
        analysis += "\n"
    
    analysis += "**处理建议**: 建议根据具体缺陷类型采取相应的修复措施，如打磨、涂层或更换材料。"
    
    return analysis

def main():
    parser = argparse.ArgumentParser(description="NEU-DET YOLO格式转Qwen2-VL微调数据格式")
    parser.add_argument("--data_root", type=str, default="NEU-DET", 
                       help="NEU-DET数据集根目录")
    parser.add_argument("--output_dir", type=str, default=".", 
                       help="输出目录（默认为当前目录）")
    parser.add_argument("--splits", nargs="+", default=["train", "valid", "test"],
                       help="要转换的数据集划分")
    
    args = parser.parse_args()
    
    # 创建输出目录
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
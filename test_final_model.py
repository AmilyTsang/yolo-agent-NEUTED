import torch
import os
import json
import re
from PIL import Image
from transformers import Qwen2VLForConditionalGeneration, Qwen2VLProcessor
from peft import PeftModel
import argparse

# ==================== 模型路径配置 ====================
BASE_MODEL_PATH = "/root/autodl-tmp/models/Qwen2-VL-2B-Instruct"
FINAL_MODEL_PATH = "./qlora_500steps_output_final"  # 最终合并模型
ADAPTER_PATH = "./qlora_500steps_output/checkpoint-500"
TEST_DATA_DIR = "/root/autodl-tmp/yolo-agent-NEUTED/NEU-DET/valid"
OUTPUT_FILE = "final_model_results.json"
# ======================================================

CATEGORIES = ['crazing', 'inclusion', 'patches', 'pitted_surface', 'rolled-in_scale', 'scratches']

def parse_boxes(output_text):
    boxes = []
    lines = re.split(r'[；;]', output_text)
    for line in lines:
        line = line.strip()
        if not line:
            continue
        pattern = r'([a-zA-Z_]+)\s*[:：]?\s*[\(\[]?(\d+)[,，](\d+)[\)\]]?\s*[-–]\s*[\(\[]?(\d+)[,，](\d+)[\)\]]?'
        matches = re.findall(pattern, line)
        for match in matches:
            cat, x1, y1, x2, y2 = match
            if cat in CATEGORIES:
                boxes.append((cat, int(x1), int(y1), int(x2), int(y2)))
            else:
                alias_map = {'crazing': 'crazing', 'inclusion': 'inclusion', 'patches': 'patches',
                             'pitted': 'pitted_surface', 'rolled': 'rolled-in_scale', 'scratch': 'scratches'}
                if cat in alias_map:
                    boxes.append((alias_map[cat], int(x1), int(y1), int(x2), int(y2)))
    return boxes

def read_yolo_labels(label_path, img_w, img_h):
    boxes = []
    if not os.path.exists(label_path):
        return boxes
    with open(label_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                cls_id = int(parts[0])
                x_center = float(parts[1])
                y_center = float(parts[2])
                width = float(parts[3])
                height = float(parts[4])
                x1 = int((x_center - width / 2) * img_w)
                y1 = int((y_center - height / 2) * img_h)
                x2 = int((x_center + width / 2) * img_w)
                y2 = int((y_center + height / 2) * img_h)
                category = CATEGORIES[cls_id]
                boxes.append((category, x1, y1, x2, y2))
    return boxes

def iou(box1, box2):
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

def evaluate_single_image(model, processor, image_path, label_path=None, verbose=True):
    try:
        image = Image.open(image_path).convert("RGB")
        img_w, img_h = image.size
    except Exception as e:
        print(f"❌ 无法读取图片 {image_path}: {e}")
        return None, None, None

    question = "请检测这张图片中的所有钢材表面缺陷，并给出类别和位置。"
    messages = [{"role": "user", "content": f"<|vision_start|><|image_pad|><|vision_end|>\n{question}"}]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=text, images=image, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=False,
        )
    response = processor.decode(outputs[0], skip_special_tokens=True)
    pred_boxes = parse_boxes(response)

    gt_boxes = []
    if label_path and os.path.exists(label_path):
        gt_boxes = read_yolo_labels(label_path, img_w, img_h)

    if verbose:
        print(f"\n📷 图片: {os.path.basename(image_path)}")
        print(f"🔍 模型原始输出:\n{response}")
        print(f"✅ 预测框: {pred_boxes}")
        print(f"📝 真实框: {gt_boxes}")

    return pred_boxes, gt_boxes, response

def compute_metrics(pred_boxes_list, gt_boxes_list, iou_threshold=0.5):
    total_tp = total_fp = total_fn = 0
    for pred_boxes, gt_boxes in zip(pred_boxes_list, gt_boxes_list):
        matched_gt = set()
        for pred in pred_boxes:
            cat_pred, *box_pred = pred
            best_iou = 0
            best_idx = -1
            for idx, gt in enumerate(gt_boxes):
                if idx in matched_gt:
                    continue
                cat_gt, *box_gt = gt
                if cat_pred == cat_gt:
                    cur_iou = iou(box_pred, box_gt)
                    if cur_iou > best_iou:
                        best_iou = cur_iou
                        best_idx = idx
            if best_iou >= iou_threshold and best_idx != -1:
                total_tp += 1
                matched_gt.add(best_idx)
            else:
                total_fp += 1
        total_fn += len(gt_boxes) - len(matched_gt)
    
    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {'TP': total_tp, 'FP': total_fp, 'FN': total_fn,
            'Precision': precision, 'Recall': recall, 'F1': f1}

def load_final_model(model_path):
    """加载最终合并后的完整模型"""
    print(f"📦 加载完整模型: {model_path}")
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        model_path,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    processor = Qwen2VLProcessor.from_pretrained(model_path, trust_remote_code=True)
    model.eval()
    print("✅ 完整模型加载完成！")
    return model, processor

def load_lora_model(base_model_path, adapter_path):
    """加载基础模型 + LoRA adapter"""
    print(f"📦 加载基础模型: {base_model_path}")
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        base_model_path,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    processor = Qwen2VLProcessor.from_pretrained(base_model_path, trust_remote_code=True)
    
    print(f"📦 加载 LoRA adapter: {adapter_path}")
    model = PeftModel.from_pretrained(model, adapter_path)
    model.eval()
    print("✅ LoRA 模型加载完成！")
    return model, processor

def main():
    parser = argparse.ArgumentParser(description="验证Qwen2-VL最终模型")
    parser.add_argument('--model_type', type=str, default='final', 
                        choices=['final', 'lora'],
                        help='模型类型: final(完整模型) 或 lora(基础模型+adapter)')
    parser.add_argument('--model_path', type=str, default=FINAL_MODEL_PATH,
                        help='模型路径')
    parser.add_argument('--base_model', type=str, default=BASE_MODEL_PATH,
                        help='基础模型路径（仅lora模式需要）')
    parser.add_argument('--adapter', type=str, default=ADAPTER_PATH,
                        help='LoRA adapter路径（仅lora模式需要）')
    parser.add_argument('--image', type=str, help='单张测试图片路径')
    parser.add_argument('--test_dir', type=str, default=TEST_DATA_DIR,
                        help='测试数据集目录')
    parser.add_argument('--output', type=str, default=OUTPUT_FILE,
                        help='输出结果文件')
    args = parser.parse_args()

    # 加载模型
    if args.model_type == 'final':
        model, processor = load_final_model(args.model_path)
    else:
        model, processor = load_lora_model(args.base_model, args.adapter)

    pred_list, gt_list, details = [], [], []

    if args.image:
        print(f"\n🔍 测试单张图片: {args.image}")
        label_path = None
        if args.test_dir:
            img_name = os.path.basename(args.image)
            label_name = os.path.splitext(img_name)[0] + '.txt'
            label_path = os.path.join(args.test_dir, 'labels', label_name)
        
        pred, gt, raw = evaluate_single_image(model, processor, args.image, label_path, verbose=True)
        if pred is not None:
            pred_list.append(pred)
            gt_list.append(gt)
            details.append({
                'image': os.path.basename(args.image), 
                'predictions': pred, 
                'ground_truth': gt, 
                'raw_output': raw
            })
            
    else:
        img_dir = os.path.join(args.test_dir, 'images')
        label_dir = os.path.join(args.test_dir, 'labels')
        
        if not os.path.isdir(img_dir):
            print(f"❌ 图片目录不存在: {img_dir}")
            return
        
        img_files = sorted([f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))])
        print(f"\n📊 批量测试模式，找到 {len(img_files)} 张图片")
        
        for idx, img_file in enumerate(img_files):
            img_path = os.path.join(img_dir, img_file)
            label_name = os.path.splitext(img_file)[0] + '.txt'
            label_path = os.path.join(label_dir, label_name)
            
            print(f"\n[{idx+1}/{len(img_files)}] 处理: {img_file}")
            pred, gt, raw = evaluate_single_image(model, processor, img_path, label_path, verbose=False)
            
            if pred is not None:
                pred_list.append(pred)
                gt_list.append(gt)
                details.append({
                    'image': img_file, 
                    'predictions': pred, 
                    'ground_truth': gt, 
                    'raw_output': raw
                })

    if pred_list:
        metrics = compute_metrics(pred_list, gt_list)
        print("\n" + "="*60)
        print("📈 测试结果汇总:")
        print(f"测试图片数: {len(pred_list)}")
        print(f"真阳性(TP): {metrics['TP']}")
        print(f"假阳性(FP): {metrics['FP']}")
        print(f"假阴性(FN): {metrics['FN']}")
        print(f"精确率(Precision): {metrics['Precision']:.4f}")
        print(f"召回率(Recall): {metrics['Recall']:.4f}")
        print(f"F1分数: {metrics['F1']:.4f}")
        print("="*60)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({'metrics': metrics, 'details': details}, f, indent=2, ensure_ascii=False)
        print(f"\n💾 详细结果已保存至: {args.output}")
    else:
        print("\n⚠️ 没有成功处理的图片，请检查输入路径。")

if __name__ == "__main__":
    main()

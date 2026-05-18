#!/usr/bin/env python3
import os
import torch
import json
from PIL import Image
from transformers import (
    Qwen2VLForConditionalGeneration,
    Qwen2VLProcessor,
    TrainingArguments,
    Trainer,
)
from peft import LoraConfig, get_peft_model
from datasets import Dataset

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# ========== 配置 ==========
MODEL_ID = "/root/autodl-tmp/models/Qwen2-VL-2B-Instruct"
TRAIN_JSONL = "/root/autodl-tmp/yolo-agent-NEUTED/qwen_finetune_train.jsonl"
VAL_JSONL   = "/root/autodl-tmp/yolo-agent-NEUTED/qwen_finetune_valid.jsonl"
OUTPUT_DIR = "./qlora_500steps_output"
BASE_DIR = "/root/autodl-tmp/yolo-agent-NEUTED"

# 增加训练步数和改进配置
TRAIN_STEPS = 2000          # 增加训练步数
BATCH_SIZE = 1
GRADIENT_ACCUMULATION = 4
LEARNING_RATE = 1e-4        # 降低学习率更稳定
SAVE_STEPS = 100            # 更频繁保存

print("加载模型...")
model = Qwen2VLForConditionalGeneration.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)
model.config.use_cache = False
processor = Qwen2VLProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)

# 改进 LoRA 配置 - 增加 target_modules 覆盖更多层
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],  # 增加更多模块
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, lora_config)
model.enable_input_require_grads()
model.print_trainable_parameters()
model.train()

def load_jsonl(path):
    data = []
    with open(path) as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

train_data = load_jsonl(TRAIN_JSONL)
val_data = load_jsonl(VAL_JSONL) if os.path.exists(VAL_JSONL) else []
print(f"训练集: {len(train_data)} 条, 验证集: {len(val_data)} 条")

train_dataset = Dataset.from_list(train_data)
val_dataset = Dataset.from_list(val_data) if val_data else None

def preprocess(example):
    """预处理函数，确保训练数据格式与测试时一致"""
    img_path = example["image"]
    if not img_path.startswith("/"):
        img_path = os.path.join(BASE_DIR, img_path)
    try:
        image = Image.open(img_path).convert("RGB")
    except Exception as e:
        print(f"图像加载失败: {img_path}, 跳过该样本")
        return None

    messages = []
    # 添加系统提示
    messages.append({
        "role": "system",
        "content": "你是钢铁表面缺陷检测专家。请用中文回答，格式为：缺陷类别: (x1,y1)-(x2,y2)，多个缺陷用分号分隔。"
    })
    
    for conv in example["conversations"]:
        role = conv["role"]
        content = conv["content"]
        
        if role == "user":
            # 统一用户提问格式，与测试时保持一致
            content = content.replace("<|image|>", "")
            content = "<|vision_start|><|image_pad|><|vision_end|>\n请检测这张图片中的所有钢材表面缺陷，并给出类别和位置。"
            messages.append({"role": "user", "content": content})
            
        elif role == "assistant":
            # 简化输出格式，只保留类别和坐标
            # 从原始回答中提取缺陷信息，转换为简洁格式
            simplified_content = simplify_output(content)
            if simplified_content:
                messages.append({"role": "assistant", "content": simplified_content})
            else:
                # 如果无法解析，使用原始内容但简化
                messages.append({"role": "assistant", "content": content})

    if not messages:
        print(f"跳过 {img_path}: 无有效对话")
        return None

    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(
        text=text,
        images=image,
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=512
    )
    inputs = {k: v.squeeze(0) for k, v in inputs.items()}
    inputs["labels"] = inputs["input_ids"].clone()
    return inputs

def simplify_output(content):
    """
    将训练数据中的复杂回答转换为简洁格式：
    原始: "crazing\n- 位置坐标: [1, 9, 108, 121]"
    简化: "crazing: (1,9)-(108,121)"
    """
    import re
    
    # 匹配格式：**crazing**\n   - 位置坐标: [1, 9, 108, 121]
    pattern = r'\*\*(\w+)\*\*.*?位置坐标:\s*\[(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\]'
    matches = re.findall(pattern, content, re.DOTALL)
    
    if matches:
        result = "; ".join([f"{cat}: ({x1},{y1})-({x2},{y2})" for cat, x1, y1, x2, y2 in matches])
        return result
    
    # 如果无法解析，返回None
    return None

print("预处理训练集...")
train_dataset = train_dataset.map(preprocess, remove_columns=train_dataset.column_names)
train_dataset = train_dataset.filter(lambda x: x is not None)
if val_dataset:
    print("预处理验证集...")
    val_dataset = val_dataset.map(preprocess, remove_columns=val_dataset.column_names)
    val_dataset = val_dataset.filter(lambda x: x is not None)

print(f"预处理后 - 训练集: {len(train_dataset)} 条, 验证集: {len(val_dataset) if val_dataset else 0} 条")

# 改进训练参数
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRADIENT_ACCUMULATION,
    gradient_checkpointing=True,
    learning_rate=LEARNING_RATE,
    max_steps=TRAIN_STEPS,
    save_steps=SAVE_STEPS,
    fp16=True,
    logging_steps=10,
    eval_steps=100,
    eval_strategy="steps" if val_dataset else "no",
    save_total_limit=5,
    remove_unused_columns=False,
    report_to="none",
    warmup_steps=50,           # 添加预热
    weight_decay=0.01,         # 添加权重衰减
    optim="adamw_torch",       # 使用 AdamW 优化器
)

class CustomTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        outputs = model(**inputs)
        loss = outputs.loss
        return (loss, outputs) if return_outputs else loss

trainer = CustomTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=processor.tokenizer,
)

print(f"开始训练（总步数 {TRAIN_STEPS}，每 {SAVE_STEPS} 步保存）...")
print(f"学习率: {LEARNING_RATE}, 批次: {BATCH_SIZE}x{GRADIENT_ACCUMULATION}")
trainer.train()

# 保存最终模型
final_dir = OUTPUT_DIR + "_final"
model.save_pretrained(final_dir)
processor.save_pretrained(final_dir)
print(f"最终模型已保存至 {final_dir}")

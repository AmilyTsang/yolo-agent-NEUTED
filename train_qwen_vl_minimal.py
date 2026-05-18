#!/usr/bin/env python3
"""
极简训练脚本：只检测缺陷类别和坐标，不输出原因和建议。
适用场景：模型之前出现严重幻觉（TP=0），需要先学会“看”和“定位”。
"""

import os
import json
import torch
import warnings
from PIL import Image
from torch.utils.data import Dataset
from transformers import (
    Qwen2VLForConditionalGeneration,
    Qwen2VLProcessor,
    TrainingArguments,
    Trainer,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

warnings.filterwarnings("ignore")

# ==================== 配置区域 ====================
BASE_MODEL_PATH = "/root/autodl-tmp/models/Qwen2-VL-2B-Instruct"
# 注意：这里指向清洗后的干净数据（只有类别和坐标）
TRAIN_JSONL    = "/root/autodl-tmp/yolo-agent-NEUTED/qwen_finetune_train_clean.jsonl"
VAL_JSONL      = "/root/autodl-tmp/yolo-agent-NEUTED/qwen_finetune_valid_clean.jsonl"
OUTPUT_DIR     = "./qwen_detection_minimal"

# 训练参数：因为任务变简单了，步数可以减少
BATCH_SIZE        = 1
GRADIENT_ACCUMULATION = 8   # 有效批次 8
LEARNING_RATE    = 1e-5      # 降低学习率，防止“背答案”
NUM_TRAIN_EPOCHS = 2         # 只跑2个Epoch，够用了
MAX_LENGTH       = 256        # 输出变短了，不需要1024那么长
SAVE_STEPS       = 200
# =================================================

def load_jsonl(path):
    data = []
    if not os.path.exists(path): return data
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip(): data.append(json.loads(line))
    return data

class MinimalDefectDataset(Dataset):
    def __init__(self, data_list, processor, base_dir=""):
        self.data = data_list
        self.processor = processor
        self.base_dir = base_dir

    def __len__(self): return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        img_path = item["image"]
        
        # 1. 加载图片
        if self.base_dir and not os.path.isabs(img_path):
            full_img_path = os.path.join(self.base_dir, img_path)
        else:
            full_img_path = img_path
            
        try:
            image = Image.open(full_img_path).convert("RGB")
        except Exception as e:
            print(f"❌ 图片加载失败: {full_img_path}, {e}")
            return None

        # 2. 构造极简 Messages
        # System: 只做检测
        # User: 只问位置和类别
        # Assistant: 只有 "crazing: (1,9)-(108,121)" 这种干净内容
        messages = [
            {"role": "system", "content": "你是一个工业缺陷检测器。请只输出缺陷类别和坐标，不要输出原因和建议。"},
            {"role": "user", "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": "请检测这张图片中的所有钢材表面缺陷，给出类别和位置。"}
            ]},
            {"role": "assistant", "content": item["conversations"][2]["content"]} # 直接取清洗后的内容
        ]

        # 3. 应用 Template
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)

        # 4. 处理输入
        inputs = self.processor(
            text=text,
            images=image,
            padding="max_length",
            truncation=True,
            max_length=MAX_LENGTH,
            return_tensors="pt"
        )

        inputs = {k: v.squeeze(0) for k, v in inputs.items()}

        # 5. Labels
        labels = inputs["input_ids"].clone()
        labels[labels == self.processor.tokenizer.pad_token_id] = -100
        inputs["labels"] = labels
        
        return inputs

def main():
    print("🚀 开始加载模型和数据（极简模式）...")
    
    processor = Qwen2VLProcessor.from_pretrained(BASE_MODEL_PATH, trust_remote_code=True)
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        BASE_MODEL_PATH,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True
    )
    
    model = prepare_model_for_kbit_training(model)
    
    # LoRA 配置
    lora_config = LoraConfig(
        r=8,               # 任务简单，Rank可以小一点
        lora_alpha=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    model.train()

    # 加载数据
    BASE_DIR = "/root/autodl-tmp/yolo-agent-NEUTED"
    print("📂 加载清洗后的数据...")
    train_raw = load_jsonl(TRAIN_JSONL)
    val_raw = load_jsonl(VAL_JSONL)
    
    train_dataset = MinimalDefectDataset(train_raw, processor, base_dir=BASE_DIR)
    val_dataset = MinimalDefectDataset(val_raw, processor, base_dir=BASE_DIR) if val_raw else None
    
    print(f"✅ 训练集: {len(train_dataset)}, 验证集: {len(val_dataset) if val_dataset else 0}")

    # 训练参数
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION,
        learning_rate=LEARNING_RATE,
        num_train_epochs=NUM_TRAIN_EPOCHS,
        logging_steps=10,
        save_steps=SAVE_STEPS,
        save_total_limit=2,
        eval_strategy="steps" if val_dataset else "no",
        eval_steps=SAVE_STEPS,
        bf16=True,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        report_to="none",
        remove_unused_columns=False,
        optim="adamw_torch",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=processor.tokenizer,
    )

    print("🏃‍♂️ 开始极简训练（只学定位和分类）...")
    trainer.train()

    print(f"💾 保存模型到 {OUTPUT_DIR}/final")
    model.save_pretrained(f"{OUTPUT_DIR}/final")
    processor.save_pretrained(f"{OUTPUT_DIR}/final")
    print("🎉 第一阶段训练完成！模型已学会看图和定位。")

if __name__ == "__main__":
    main()
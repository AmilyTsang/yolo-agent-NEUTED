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
MODEL_ID = "/root/autodl-tmp/qwen_model"
TRAIN_JSONL = "/root/autodl-tmp/yolo-agent-NEUTED/qwen_finetune_train.jsonl"
VAL_JSONL   = "/root/autodl-tmp/yolo-agent-NEUTED/qwen_finetune_valid.jsonl"
OUTPUT_DIR = "./qlora_stable_output"
BASE_DIR = "/root/autodl-tmp/yolo-agent-NEUTED"

print("加载模型 (FP16)...")
model = Qwen2VLForConditionalGeneration.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)
processor = Qwen2VLProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)

# LoRA 配置（与简化版一致）
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
model.train()  # 确保训练模式

def load_jsonl(file_path):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data

train_raw = load_jsonl(TRAIN_JSONL)
val_raw = load_jsonl(VAL_JSONL) if os.path.exists(VAL_JSONL) else []
print(f"训练集: {len(train_raw)} 条, 验证集: {len(val_raw)} 条")

train_dataset = Dataset.from_list(train_raw)
val_dataset = Dataset.from_list(val_raw) if val_raw else None

def preprocess(example):
    img_path = example["image"]
    if not img_path.startswith("/"):
        img_path = os.path.join(BASE_DIR, img_path)
    image = Image.open(img_path).convert("RGB")
    
    messages = []
    for conv in example["conversations"]:
        role = conv["role"]
        content = conv["content"]
        if role == "system":
            continue
        elif role == "user":
            if "<|vision_start|>" not in content:
                content = content.replace("<|image|>", "")
                content = "<|vision_start|><|image_pad|><|vision_end|>\n" + content
            messages.append({"role": "user", "content": content})
        elif role == "assistant":
            messages.append({"role": "assistant", "content": content})
    
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(
        text=text,
        images=image,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=2048
    )
    inputs = {k: v.squeeze(0) for k, v in inputs.items()}
    inputs["labels"] = inputs["input_ids"].clone()
    return inputs

print("预处理训练集...")
train_dataset = train_dataset.map(preprocess, remove_columns=train_dataset.column_names)
if val_dataset:
    print("预处理验证集...")
    val_dataset = val_dataset.map(preprocess, remove_columns=val_dataset.column_names)

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    num_train_epochs=10,
    fp16=True,
    logging_steps=10,
    save_steps=500,
    eval_steps=500,
    eval_strategy="steps" if val_dataset else "no",
    remove_unused_columns=False,
    report_to="none",
)

class QwenTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        outputs = model(**inputs)
        loss = outputs.loss
        return (loss, outputs) if return_outputs else loss

trainer = QwenTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=processor.tokenizer,
)

print("开始 FP16 LoRA 微调...")
trainer.train()

final_dir = OUTPUT_DIR + "_final"
model.save_pretrained(final_dir)
processor.save_pretrained(final_dir)
print(f"模型已保存至 {final_dir}")
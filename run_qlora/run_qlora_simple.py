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

# 配置
MODEL_ID = "/root/autodl-tmp/qwen_model"
TRAIN_JSONL = "/root/autodl-tmp/yolo-agent-NEUTED/qwen_finetune_train.jsonl"
VAL_JSONL   = "/root/autodl-tmp/yolo-agent-NEUTED/qwen_finetune_valid.jsonl"
OUTPUT_DIR = "./qlora_simple_output"
BASE_DIR = "/root/autodl-tmp/yolo-agent-NEUTED"

# 只取很少数据用于调试
def load_small(file_path, limit=2):
    data = []
    with open(file_path, 'r') as f:
        for i, line in enumerate(f):
            if i >= limit:
                break
            if line.strip():
                data.append(json.loads(line))
    return data

train_raw = load_small(TRAIN_JSONL, 2)
val_raw = load_small(VAL_JSONL, 1) if os.path.exists(VAL_JSONL) else []
print(f"调试数据: 训练集 {len(train_raw)} 条, 验证集 {len(val_raw)} 条")

# 加载模型（不用量化，fp16）
print("加载模型...")
model = Qwen2VLForConditionalGeneration.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float16,
    device_map="auto"
)
processor = Qwen2VLProcessor.from_pretrained(MODEL_ID)

# 添加 LoRA
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
model.train()  # 关键：确保训练模式

# 构建数据集
def preprocess(example):
    img_path = example["image"]
    if not img_path.startswith("/"):
        img_path = os.path.join(BASE_DIR, img_path)
    image = Image.open(img_path).convert("RGB")
    
    # 消息格式
    messages = []
    for conv in example["conversations"]:
        if conv["role"] == "system":
            continue
        elif conv["role"] == "user":
            content = conv["content"]
            # 添加图像占位符
            if "<|vision_start|>" not in content:
                content = content.replace("<|image|>", "")
                content = "<|vision_start|><|image_pad|><|vision_end|>\n" + content
            messages.append({"role": "user", "content": content})
        elif conv["role"] == "assistant":
            messages.append({"role": "assistant", "content": conv["content"]})
    
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=text, images=image, return_tensors="pt", padding=True, truncation=True, max_length=512)
    # 移除 batch 维度
    inputs = {k: v.squeeze(0) for k, v in inputs.items()}
    # 显式设置 labels（复制 input_ids）
    inputs["labels"] = inputs["input_ids"].clone()
    return inputs

train_dataset = Dataset.from_list(train_raw).map(preprocess, remove_columns=train_raw[0].keys())
if val_raw:
    val_dataset = Dataset.from_list(val_raw).map(preprocess, remove_columns=val_raw[0].keys())
else:
    val_dataset = None

# 训练参数
args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=1,
    learning_rate=1e-4,
    num_train_epochs=1,
    fp16=True,
    logging_steps=1,
    save_steps=10,
    remove_unused_columns=False,
    report_to="none",
)

class MyTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        outputs = model(**inputs)
        loss = outputs.loss
        print(f"Loss: {loss.item() if loss is not None else 'None'}, requires_grad: {loss.requires_grad if loss is not None else 'N/A'}")
        return (loss, outputs) if return_outputs else loss

trainer = MyTrainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=processor.tokenizer,
)

print("开始训练...")
trainer.train()

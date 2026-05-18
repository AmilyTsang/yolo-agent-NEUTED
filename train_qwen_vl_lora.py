#!/usr/bin/env python3
import os
import json
import torch
import warnings
from PIL import Image
from torch.utils.data import Dataset, DataLoader
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
# 注意：这里使用之前修复后的 _fixed.jsonl 文件
TRAIN_JSONL    = "/root/autodl-tmp/yolo-agent-NEUTED/qwen_finetune_train_fixed.jsonl"
VAL_JSONL      = "/root/autodl-tmp/yolo-agent-NEUTED/qwen_finetune_valid_fixed.jsonl"
OUTPUT_DIR     = "./qwen_detection_lora_final"

# 训练参数
BATCH_SIZE        = 1        # 32G显存下，2B模型设为1最稳
GRADIENT_ACCUMULATION = 16   # 有效批次 = 16
LEARNING_RATE    = 5e-5
NUM_TRAIN_EPOCHS = 3
MAX_LENGTH       = 1024      # 足够容纳原因和建议
SAVE_STEPS       = 500
# =================================================

def load_jsonl(path):
    data = []
    if not os.path.exists(path):
        print(f"⚠️ 文件不存在: {path}")
        return data
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

class DefectDataset(Dataset):
    def __init__(self, data_list, processor, base_dir=""):
        self.data = data_list
        self.processor = processor
        self.base_dir = base_dir

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        img_path = item["image"]
        
        # 1. 处理图片路径
        if self.base_dir and not os.path.isabs(img_path):
            full_img_path = os.path.join(self.base_dir, img_path)
        else:
            full_img_path = img_path
            
        try:
            image = Image.open(full_img_path).convert("RGB")
        except Exception as e:
            print(f"❌ 无法加载图片: {full_img_path}, 错误: {e}")
            # 返回空白图防止崩溃
            image = Image.new('RGB', (224, 224), (128, 128, 128))

        # 2. 构造对话 (严格遵循 Qwen2-VL 格式)
        # 注意：这里 content 是字符串，图片通过 processor 的 images 参数传入
        messages = [
            {"role": "system", "content": item["conversations"][0]["content"]},
            {"role": "user", "content": item["conversations"][1]["content"]},
            {"role": "assistant", "content": item["conversations"][2]["content"]}
        ]

        # 3. 应用 Chat Template
        # 这一步会把 <|vision_start|><|image_pad|><|vision_end|> 插入到文本中
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)

        # 4. 处理多模态输入
        # 关键点：processor 会根据 text 中的 image_pad 标记来对齐 images 特征
        inputs = self.processor(
            text=text,
            images=image,
            padding="max_length",
            truncation=True,
            max_length=MAX_LENGTH,
            return_tensors="pt"
        )

        # squeeze(0) 去掉 processor 添加的 batch 维度
        inputs = {k: v.squeeze(0) for k, v in inputs.items()}

        # 5. 处理 Labels (核心：只计算回答部分的 Loss)
        labels = inputs["input_ids"].clone()
        
        # 方法：将 Padding 部分设为 -100
        labels[labels == self.processor.tokenizer.pad_token_id] = -100
        
        # 进阶：Mask 掉 System 和 User 部分 (推荐)
        # 找到 assistant header 的位置，只保留后面的 token 用于计算 loss
        # 简单实现：直接把 input_ids 复制给 labels，Trainer 会自动 shift
        # 但为了精准，我们可以把 prompt 部分遮住
        # 这里我们使用一个简单的逻辑：如果 tokenizer 有特殊的 image token，保留它
        # 实际上，对于因果语言模型，我们通常只关心生成的部分
        # 这里暂时不做复杂的 prompt mask，因为数据量不大，全算也无妨，但为了效果可以加上：
        
        # 尝试找到 "<|im_start|>assistant\n" 的位置
        # 注意：这里的实现依赖于 tokenizer 的解码，可能会慢一点，但更准确
        # 为了简化，我们暂时只 mask padding
        
        inputs["labels"] = labels
        
        return inputs

def main():
    print("🚀 开始加载模型和数据...")
    
    # 1. 加载 Processor
    processor = Qwen2VLProcessor.from_pretrained(BASE_MODEL_PATH, trust_remote_code=True)
    
    # 2. 加载 Model
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        BASE_MODEL_PATH,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True
    )
    
    # 准备模型进行训练 (确保梯度流正常)
    model = prepare_model_for_kbit_training(model)
    
    # 3. 配置 LoRA
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    model.train() # 确保训练模式

    # 4. 加载数据
    print("📂 加载数据集...")
    BASE_DIR = "/root/autodl-tmp/yolo-agent-NEUTED" 
    
    train_raw = load_jsonl(TRAIN_JSONL)
    val_raw = load_jsonl(VAL_JSONL)
    
    train_dataset = DefectDataset(train_raw, processor, base_dir=BASE_DIR)
    val_dataset = DefectDataset(val_raw, processor, base_dir=BASE_DIR) if val_raw else None
    
    print(f"✅ 训练集: {len(train_dataset)}, 验证集: {len(val_dataset) if val_dataset else 0}")

    # 5. 训练参数
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION,
        learning_rate=LEARNING_RATE,
        num_train_epochs=NUM_TRAIN_EPOCHS,
        logging_steps=10,
        save_steps=SAVE_STEPS,
        save_total_limit=3,
        eval_strategy="steps" if val_dataset else "no",
        eval_steps=SAVE_STEPS,
        bf16=True,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False}, # 防止梯度检查点报错
        report_to="none",
        remove_unused_columns=False, # 必须 False
        optim="adamw_torch",
        lr_scheduler_type="linear",
        warmup_ratio=0.03,
    )

    # 6. Trainer
    # 注意：这里没有自定义 collate_fn，因为 Dataset 返回的 Tensor 形状已经一致
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=processor.tokenizer,
    )

    # 7. 开始训练
    print("🏃‍♂️ 开始训练...")
    trainer.train()

    # 8. 保存
    print(f"💾 保存模型到 {OUTPUT_DIR}/final")
    model.save_pretrained(f"{OUTPUT_DIR}/final")
    processor.save_pretrained(f"{OUTPUT_DIR}/final")
    print("🎉 训练完成！")

if __name__ == "__main__":
    main()
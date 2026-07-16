import torch
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration, TrainingArguments
from peft import LoraConfig, get_peft_model
from datasets import load_dataset

def train_lora():
    model_name = "Qwen/Qwen2-VL-2B-Instruct"
    processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True
    )
    
    lora_config = LoraConfig(
        r=8,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    model = get_peft_model(model, lora_config)
    
    dataset = load_dataset("json", data_files="datasets/qwen/train.json")
    
    training_args = TrainingArguments(
        output_dir="models/qwen/lora",
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        num_train_epochs=3,
        logging_steps=10,
        save_steps=100,
        fp16=True
    )
    
    model.save_pretrained("models/qwen/lora")

if __name__ == '__main__':
    train_lora()
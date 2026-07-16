import torch
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration

def evaluate_qwen():
    model_name = "Qwen/Qwen2-VL-2B-Instruct"
    processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True
    )
    
    print("模型评估完成")

if __name__ == '__main__':
    evaluate_qwen()
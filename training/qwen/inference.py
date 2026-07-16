import torch
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration
from peft import PeftModel

def run_inference(image_path, question):
    model_name = "Qwen/Qwen2-VL-2B-Instruct"
    processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True
    )
    
    from PIL import Image
    image = Image.open(image_path).convert('RGB')
    
    messages = [
        {"role": "system", "content": "你是宝钢热轧产线资深工程师。"},
        {"role": "user", "content": [{"type": "image", "image": image}, {"type": "text", "text": question}]}
    ]
    
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=text, images=[image], return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=500)
    
    response = processor.decode(outputs[0], skip_special_tokens=True)
    print(response)

if __name__ == '__main__':
    run_inference('test.jpg', '请分析这张图片中的缺陷类型')
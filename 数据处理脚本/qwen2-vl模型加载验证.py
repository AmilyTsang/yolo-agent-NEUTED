from transformers import Qwen2VLForConditionalGeneration, Qwen2VLProcessor

model_id = "Qwen/Qwen2-VL-7B-Instruct"
model = Qwen2VLForConditionalGeneration.from_pretrained(model_id, device_map="auto")
processor = Qwen2VLProcessor.from_pretrained(model_id)

print("✅ 模型加载成功！")
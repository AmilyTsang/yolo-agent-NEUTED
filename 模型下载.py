# 使用模型的Hugging Face仓库地址进行下载
from transformers import AutoModelForCausalLM, AutoProcessor

model_id = "Qwen/Qwen2-VL-2B-Instruct"

# 下载并加载模型
model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)
# 下载并加载处理器
processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
print("模型下载并加载成功！")
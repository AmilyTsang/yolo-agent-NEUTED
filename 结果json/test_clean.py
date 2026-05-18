import torch
from PIL import Image  # <--- 补上这个关键的导入
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration
from peft import PeftModel

# ===== 配置 =====
BASE_MODEL_PATH = "/root/autodl-tmp/models/Qwen2-VL-2B-Instruct"
LORA_PATH = "./qwen_detection_minimal/final"  # 你极简训练的权重
TEST_IMAGE = "/root/autodl-tmp/yolo-agent-NEUTED/NEU-DET/train/images/crazing_101.jpg" # 用训练集图片测
# ==============

print("🚀 加载模型中...")

# 1. 加载 Processor
processor = AutoProcessor.from_pretrained(BASE_MODEL_PATH, trust_remote_code=True)

# 2. 加载基础模型
model = Qwen2VLForConditionalGeneration.from_pretrained(
    BASE_MODEL_PATH,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True
)

# 3. 加载 LoRA 权重 (关键步骤)
print(f"📦 正在加载 LoRA 权重: {LORA_PATH}")
model = PeftModel.from_pretrained(model, LORA_PATH)
model.eval()  # 设置为评估模式
print("✅ 模型加载完成！")

# 4. 检查 LoRA 是否真的生效
print("\n🔍 检查 LoRA 权重状态...")
lora_active = False
for name, param in model.named_parameters():
    if "lora" in name and param.requires_grad:
        # 打印第一个找到的 lora 参数名，确认存在
        print(f"   ✅ 发现活跃 LoRA 参数: {name}")
        lora_active = True
        break

if not lora_active:
    print("   ❌ 危险！没有发现活跃的 LoRA 参数，模型可能在用原始权重瞎猜！")

# 5. 推理测试
print("\n🖼️ 开始推理测试...")
image = Image.open(TEST_IMAGE).convert("RGB")

# 使用极简 Prompt
messages = [
    {"role": "system", "content": "你是一个工业缺陷检测器。请只输出缺陷类别和坐标。"},
    {"role": "user", "content": [
        {"type": "image", "image": image},
        {"type": "text", "text": "请检测这张图片中的所有钢材表面缺陷，给出类别和位置。"}
    ]}
]

text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = processor(text=text, images=image, return_tensors="pt").to(model.device)

print("   🤖 模型思考中...")
with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=128,
        do_sample=False  # 关闭采样，保证结果稳定
    )

response = processor.decode(outputs[0], skip_special_tokens=True)

print("\n" + "="*60)
print("📢 模型原始输出:")
print("="*60)
# 只打印 assistant 部分
if "assistant" in response:
    print(response.split("assistant")[-1].strip())
else:
    print(response)
print("="*60)

# 6. 判断结果
if "crazing" in response.lower() or "inclusion" in response.lower():
    print("🎉 诊断结果：模型似乎学会了看图！请继续训练。")
else:
    print("⚠️ 诊断结果：模型还在乱说（没学会看图），建议重新训练或检查数据。")
# LoRA 微调技术详解

## 一、LoRA 基础概念

### 1.1 什么是 LoRA

**LoRA (Low-Rank Adaptation)** 是一种高效的大模型微调技术，由 Microsoft 于 2021 年提出。其核心思想是：

> **冻结预训练模型的权重，只训练少量的低秩矩阵来模拟参数更新**

### 1.2 LoRA 的工作原理

传统微调需要更新模型的所有参数，而 LoRA 只在 Transformer 的注意力层插入低秩矩阵：

```
原始权重: W (d_model × d_model)
LoRA 分解: W = W_0 + A × B
           A: d_model × r (随机初始化，训练)
           B: r × d_model (初始化为0，训练)
           r: rank (远小于 d_model)
```

**优势**：
- **参数量少**：只训练 2 × d_model × r 个参数
- **显存占用低**：不需要存储完整的优化器状态
- **训练速度快**：减少计算量
- **模型合并简单**：训练完成后可合并到原模型

### 1.3 适用场景

| 场景 | 说明 |
|------|------|
| 小样本微调 | 数据量少，防止过拟合 |
| 显存受限 | 大模型微调必备 |
| 多任务适配 | 快速切换任务 |
| 轻量化部署 | LoRA 权重文件小 |

---

## 二、本项目中的 LoRA 配置

### 2.1 核心配置参数

项目中使用 PEFT 库配置 LoRA，核心参数如下：

```python
from peft import LoraConfig

lora_config = LoraConfig(
    r=16,                    # 低秩矩阵的秩 (rank)
    lora_alpha=32,           # 缩放因子 (通常设为 2×r)
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # 目标模块
    lora_dropout=0.05,       # Dropout 比例
    bias="none",             # 是否训练 bias
    task_type="CAUSAL_LM"    # 任务类型
)
```

### 2.2 参数详解

| 参数 | 作用 | 推荐值 |
|------|------|--------|
| `r` | 低秩矩阵的秩，控制 LoRA 的表达能力 | 8-64，任务越复杂越大 |
| `lora_alpha` | 缩放因子，影响更新幅度 | 通常设为 2×r |
| `target_modules` | 指定哪些层应用 LoRA | 注意力层的 q/k/v/o 投影 |
| `lora_dropout` | 防止过拟合 | 0.05-0.1 |
| `bias` | 是否训练 bias 参数 | "none" 或 "lora_only" |
| `task_type` | 任务类型标识 | "CAUSAL_LM"、"SEQ_CLS" 等 |

### 2.3 不同脚本的配置对比

| 脚本 | r | lora_alpha | target_modules | 场景 |
|------|---|------------|----------------|------|
| `train_qwen_vl_lora.py` | 16 | 32 | q_proj, k_proj, v_proj, o_proj | 完整任务（检测+分析） |
| `train_qwen_vl_minimal.py` | 8 | 16 | q_proj, k_proj, v_proj, o_proj | 简单任务（仅检测） |
| `run_qlora_simple.py` | 8 | 16 | q_proj, v_proj | 调试/小数据 |
| `run_qlora.py` | 64 | 16 | q_proj, k_proj, v_proj, o_proj | 完整 QLoRA |

---

## 三、项目中的 LoRA 训练流程

### 3.1 完整流程概览

```
┌─────────────────────────────────────────────────────────────┐
│                    LoRA 训练流程                            │
├─────────────────────────────────────────────────────────────┤
│  1. 加载预训练模型 (Qwen2-VL)                               │
│                    ↓                                        │
│  2. 配置量化 (可选，4-bit/8-bit)                            │
│                    ↓                                        │
│  3. 准备模型训练 (prepare_model_for_kbit_training)          │
│                    ↓                                        │
│  4. 配置 LoRA (LoraConfig)                                  │
│                    ↓                                        │
│  5. 应用 LoRA (get_peft_model)                              │
│                    ↓                                        │
│  6. 加载数据集并预处理                                      │
│                    ↓                                        │
│  7. 配置 TrainingArguments                                  │
│                    ↓                                        │
│  8. 启动训练 (Trainer.train())                              │
│                    ↓                                        │
│  9. 保存模型 (save_pretrained)                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 关键代码解析

#### 步骤1：加载模型并配置量化

```python
from transformers import Qwen2VLForConditionalGeneration, BitsAndBytesConfig

# 4-bit 量化配置（显存优化）
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",  # Normalized Float 4-bit
    bnb_4bit_compute_dtype=torch.bfloat16
)

model = Qwen2VLForConditionalGeneration.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_config,  # 启用量化
    device_map="auto",
    trust_remote_code=True
)
```

**量化的作用**：将模型参数从 FP32 压缩到 4-bit，显存占用降低约 8 倍。

#### 步骤2：准备模型训练

```python
from peft import prepare_model_for_kbit_training

# 确保量化模型的梯度流正常
model = prepare_model_for_kbit_training(model)
```

**关键操作**：
- 将某些层转换为 FP32 以稳定梯度
- 启用梯度检查点（Gradient Checkpointing）

#### 步骤3：应用 LoRA

```python
from peft import get_peft_model

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()  # 查看可训练参数比例
```

**输出示例**：
```
trainable params: 1,048,576 || all params: 2,097,152,000 || trainable%: 0.05%
```

仅训练约 0.05% 的参数！

---

## 四、数据集处理

### 4.1 数据格式要求

本项目使用 JSONL 格式存储训练数据：

```json
{
    "image": "NEU-DET/IMAGES/crazing_1.jpg",
    "conversations": [
        {"role": "system", "content": "你是一个工业缺陷检测专家..."},
        {"role": "user", "content": "<|image|>\n请分析这张图片中的缺陷..."},
        {"role": "assistant", "content": "检测到缺陷：crazing，位置：(x1,y1)-(x2,y2)..."}
    ]
}
```

### 4.2 预处理流程

```python
def preprocess(example):
    # 1. 加载图片
    image = Image.open(img_path).convert("RGB")
    
    # 2. 构建对话消息
    messages = [
        {"role": "user", "content": "<|vision_start|><|image_pad|><|vision_end|>\n分析图片"},
        {"role": "assistant", "content": example["conversations"][2]["content"]}
    ]
    
    # 3. 应用 Chat Template
    text = processor.apply_chat_template(messages, tokenize=False)
    
    # 4. 处理多模态输入
    inputs = processor(
        text=text,
        images=image,
        padding="max_length",
        truncation=True,
        max_length=1024,
        return_tensors="pt"
    )
    
    # 5. 设置 Labels（只计算 assistant 部分的 loss）
    labels = inputs["input_ids"].clone()
    labels[labels == processor.tokenizer.pad_token_id] = -100  # mask padding
    inputs["labels"] = labels
    
    return inputs
```

**关键点**：
- 使用 `-100` 标记不需要计算损失的位置
- 图片通过 `<|vision_start|><|image_pad|><|vision_end|>` 占位符嵌入文本

---

## 五、训练参数配置

### 5.1 推荐配置

```python
training_args = TrainingArguments(
    output_dir="./qwen_detection_lora_final",
    per_device_train_batch_size=1,      # 根据显存调整
    gradient_accumulation_steps=16,     # 有效批次 = 1×16=16
    learning_rate=5e-5,                 # LoRA 学习率通常较小
    num_train_epochs=3,                 # 避免过拟合
    logging_steps=10,
    save_steps=500,
    save_total_limit=3,
    eval_strategy="steps",
    eval_steps=500,
    bf16=True,                          # 混合精度训练
    gradient_checkpointing=True,        # 显存优化
    gradient_checkpointing_kwargs={"use_reentrant": False},
    report_to="none",
    remove_unused_columns=False,        # 必须保持 False
    optim="adamw_torch",
    lr_scheduler_type="linear",
    warmup_ratio=0.03,                  # 学习率预热
)
```

### 5.2 参数选择指南

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `per_device_train_batch_size` | 单卡批次大小 | 1-4（根据显存） |
| `gradient_accumulation_steps` | 梯度累积步数 | 8-32 |
| `learning_rate` | 学习率 | 1e-5 ~ 1e-4 |
| `num_train_epochs` | 训练轮数 | 2-5 |
| `bf16/fp16` | 混合精度 | True（需支持） |
| `gradient_checkpointing` | 梯度检查点 | True（显存紧张时） |

---

## 六、进阶技巧

### 6.1 两阶段训练策略

项目采用"先简后繁"的训练策略：

**第一阶段（极简模式）**：只训练缺陷检测和定位
```python
# 配置
lora_config = LoraConfig(
    r=8,  # 较小的 rank
    learning_rate=1e-5,  # 较低的学习率
    ...
)
# 数据：只有类别和坐标，无原因分析
```

**第二阶段（完整模式）**：添加原因分析和建议
```python
# 配置
lora_config = LoraConfig(
    r=16,  # 较大的 rank
    learning_rate=5e-5,
    ...
)
# 数据：包含完整分析内容
```

### 6.2 显存优化技巧

| 方法 | 效果 | 适用场景 |
|------|------|----------|
| 4-bit 量化 | 显存降低 80%+ | 必须 |
| Gradient Checkpointing | 显存降低 30-50% | 显存紧张 |
| Gradient Accumulation | 保持批次大小 | 小批次训练 |
| bf16 混合精度 | 显存降低 50% | 支持的 GPU |
| 冻结部分层 | 减少计算量 | 任务简单时 |

### 6.3 常见问题与解决方案

| 问题 | 现象 | 解决方案 |
|------|------|----------|
| 显存不足 | `CUDA out of memory` | 减小 batch_size，启用量化 |
| Loss 不下降 | 训练无进展 | 增大 r，检查数据格式 |
| 过拟合 | 训练 Loss 低，验证 Loss 高 | 增大 dropout，减少 epoch |
| 模型幻觉 | 输出无意义内容 | 使用干净数据，降低学习率 |

---

## 七、推理与部署

### 7.1 加载 LoRA 模型

```python
from peft import PeftModel

# 加载基础模型
base_model = Qwen2VLForConditionalGeneration.from_pretrained(BASE_MODEL_PATH)

# 加载 LoRA 权重
peft_model = PeftModel.from_pretrained(base_model, LORA_PATH)

# 合并模型（可选，加速推理）
merged_model = peft_model.merge_and_unload()
```

### 7.2 推理示例

```python
# 准备输入
messages = [
    {"role": "user", "content": "<|vision_start|><|image_pad|><|vision_end|>\n请分析这张图片"}
]
text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

# 推理
inputs = processor(text=text, images=image, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=512)
response = processor.decode(outputs[0], skip_special_tokens=True)
```

---

## 八、总结

### 8.1 LoRA 核心优势

1. **高效微调**：只训练 0.05% 左右的参数
2. **显存友好**：配合量化可在消费级 GPU 上训练大模型
3. **灵活适配**：同一基础模型可适配多个任务
4. **易于部署**：LoRA 权重文件小，可动态切换

### 8.2 本项目最佳实践

| 配置 | 推荐值 |
|------|--------|
| rank (r) | 8-16（视任务复杂度） |
| 学习率 | 1e-5 ~ 5e-5 |
| 批次大小 | 1（配合梯度累积） |
| 训练轮数 | 2-5 |
| 量化 | 4-bit（nf4） |

### 8.3 参考资料

- [LoRA 论文](https://arxiv.org/abs/2106.09685)
- [PEFT 官方文档](https://huggingface.co/docs/peft)
- [QLoRA 论文](https://arxiv.org/abs/2305.14314)

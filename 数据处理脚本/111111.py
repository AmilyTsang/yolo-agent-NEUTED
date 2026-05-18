import json

def fix_jsonl_for_qwen2vl(input_path, output_path):
    count = 0
    with open(input_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            data = json.loads(line)
            for msg in data["conversations"]:
                # 替换错误的标记
                if "<|image|>" in msg["content"]:
                    msg["content"] = msg["content"].replace(
                        "<|image|>", 
                        "<|vision_start|><|image_pad|><|vision_end|>"
                    )
                    count += 1
            f_out.write(json.dumps(data, ensure_ascii=False) + '\n')
    print(f"✅ 修复完成！共替换 {count} 处标记。")
    print(f"📄 新文件: {output_path}")

# 运行修复（请确认你的文件路径）
fix_jsonl_for_qwen2vl(
    "/root/autodl-tmp/yolo-agent-NEUTED/qwen_finetune_train.jsonl",
    "/root/autodl-tmp/yolo-agent-NEUTED/qwen_finetune_train_fixed.jsonl"
)
fix_jsonl_for_qwen2vl(
    "/root/autodl-tmp/yolo-agent-NEUTED/qwen_finetune_valid.jsonl",
    "/root/autodl-tmp/yolo-agent-NEUTED/qwen_finetune_valid_fixed.jsonl"
)
import json
import re

def clean_jsonl(input_path, output_path):
    """
    清洗训练数据：
    1. 移除 '原因:'、'建议:' 等冗长文本。
    2. 移除 'markdown'、'Explanation' 等噪声。
    3. 只保留 '缺陷X: 类别 | (x1,y1)-(x2,y2)' 格式。
    """
    count = 0
    kept = 0
    new_data = []

    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                conversations = data["conversations"]
                
                # 只处理 assistant 的回复
                for msg in conversations:
                    if msg["role"] == "assistant":
                        original_content = msg["content"]
                        
                        # 1. 提取所有的缺陷块 (匹配 "缺陷X: 类别 | (x1,y1)-(x2,y2)")
                        # 我们只保留括号内的坐标和前面的类别，去掉后面的原因建议
                        pattern = r'(缺陷\d+:\s*\w+\s*\|\s*\(\s*\d+\s*,\s*\d+\s*\)-\(\s*\d+\s*,\s*\d+\s*\))'
                        matches = re.findall(pattern, original_content)
                        
                        if matches:
                            # 重组为干净的格式
                            clean_content = "; ".join(matches)
                            msg["content"] = clean_content
                            kept += 1
                        else:
                            # 如果连基本格式都没匹配到，说明这条数据太脏了，清空它
                            msg["content"] = "未检测到缺陷。"
                        
                new_data.append(data)
                count += 1
            except Exception as e:
                print(f"处理失败: {line[:50]}... 错误: {e}")

    # 保存清洗后的数据
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in new_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"✅ 清洗完成！共处理 {count} 条数据。")
    print(f"📄 输出文件: {output_path}")
    print(f"💡 提示: 已移除所有'原因'和'建议'，只保留坐标信息。")

if __name__ == "__main__":
    # 运行清洗
    clean_jsonl(
        "/root/autodl-tmp/yolo-agent-NEUTED/qwen_finetune_train_fixed.jsonl",
        "/root/autodl-tmp/yolo-agent-NEUTED/qwen_finetune_train_clean.jsonl"
    )
    clean_jsonl(
        "/root/autodl-tmp/yolo-agent-NEUTED/qwen_finetune_valid_fixed.jsonl",
        "/root/autodl-tmp/yolo-agent-NEUTED/qwen_finetune_valid_clean.jsonl"
    )
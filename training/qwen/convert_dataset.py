import os
import json

def convert_to_qwen_format(input_dir, output_file):
    samples = []
    
    for json_file in os.listdir(input_dir):
        if not json_file.endswith('.json'):
            continue
        
        with open(os.path.join(input_dir, json_file), 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        sample = {
            'image': data['image_path'],
            'conversations': [
                {
                    'from': 'user',
                    'value': f"请分析这张图片中的缺陷。缺陷类型：{data['defect_type']}，置信度：{data['confidence']}"
                },
                {
                    'from': 'assistant',
                    'value': data['analysis']
                }
            ]
        }
        samples.append(sample)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    convert_to_qwen_format('datasets/qwen/raw', 'datasets/qwen/train.json')
import os
import json

def clean_dataset(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    for file in os.listdir(input_dir):
        if file.endswith('.json'):
            with open(os.path.join(input_dir, file), 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            cleaned = {}
            for key, value in data.items():
                if value and str(value).strip():
                    cleaned[key] = value
            
            with open(os.path.join(output_dir, file), 'w', encoding='utf-8') as f:
                json.dump(cleaned, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    clean_dataset('datasets/qwen/raw', 'datasets/qwen/cleaned')
#!/usr/bin/env python
import os
import subprocess

def main():
    # 确保所有目录存在
    dirs = ['models', 'uploads', 'static', 'reports']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    
    print("🚀 启动 YOLO-Agent 工业缺陷分析助手...")
    print("📡 服务地址: http://localhost:5000")
    print("🔄 按 Ctrl+C 停止服务")
    print()
    
    # 启动 Flask 应用
    subprocess.run(['python', 'backend/app.py'])

if __name__ == '__main__':
    main()
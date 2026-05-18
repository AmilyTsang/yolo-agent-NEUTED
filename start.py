#!/usr/bin/env python3
import os
import sys
import subprocess

def main():
    # 🔧 修复 libgomp 警告
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    
    # 确保所有目录存在
    dirs = ['models', 'uploads', 'reports', 'backend', 'frontend']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    
    print("🚀 启动 YOLO-Agent 工业缺陷分析助手...")
    print("📡 服务地址: http://localhost:5000")
    print("🔄 按 Ctrl+C 停止服务")
    print()
    
    # 启动 Flask 应用
    subprocess.run([sys.executable, 'backend/app.py'])

if __name__ == '__main__':
    main()
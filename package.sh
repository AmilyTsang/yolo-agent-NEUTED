#!/bin/bash
set -e

echo "📦 正在打包 YOLO 缺陷检测项目..."

# 切换到项目目录
cd /root/autodl-tmp/yolo-agent-NEUTED

# 创建输出目录
mkdir -p ../packages

# 打包核心文件
tar -czvf ../packages/yolo-agent-NEUTED_$(date +%Y%m%d).tar.gz \
    --exclude='./.git' \
    --exclude='./ultralytics-8.0' \
    --exclude='./models' \
    --exclude='./NEU-DET/images' \
    --exclude='./NEU-DET/labels' \
    --exclude='./runs' \
    --exclude='./qlora_500steps_output' \
    --exclude='./qlora_500steps_output_final' \
    --exclude='./__pycache__' \
    --exclude='./.ipynb_checkpoints' \
    --exclude='*.pyc' \
    --exclude='*.pt' \
    --exclude='*.bin' \
    --exclude='*.jsonl' \
    .

echo ""
echo "✅ 打包完成！"
echo "📁 输出文件: ../packages/yolo-agent-NEUTED_$(date +%Y%m%d).tar.gz"
echo ""
echo "📋 打包内容："
tar -tzf ../packages/yolo-agent-NEUTED_$(date +%Y%m%d).tar.gz | head -20
echo "... (共 $(tar -tzf ../packages/yolo-agent-NEUTED_$(date +%Y%m%d).tar.gz | wc -l) 个文件)"

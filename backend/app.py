#!/usr/bin/env python3
"""
YOLO-Agent 工业缺陷分析助手 - 后端服务
适配前端 index.html 的所有 API 请求
"""

import os
import sys
import json
import uuid
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import cv2
import numpy as np

# 🔧 关键修复：添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# 导入检测管道
from yolo_qwen_pipeline import run_pipeline

# 🔧 关键修复：设置静态文件夹为 frontend 目录
app = Flask(__name__, 
            static_folder=os.path.join(project_root, 'frontend'),
            static_url_path='/static')

# 配置
UPLOAD_FOLDER = os.path.join(project_root, 'uploads')
REPORTS_FOLDER = os.path.join(project_root, 'reports')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# 确保目录存在
for folder in [UPLOAD_FOLDER, REPORTS_FOLDER]:
    Path(folder).mkdir(parents=True, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """根路由：返回前端页面"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """处理图片上传和检测"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '未上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': '未选择文件'}), 400
    
    if file and allowed_file(file.filename):
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
        file.save(original_path)
        
        try:
            start_time = time.time()
            
            # 调用检测管道
            result = run_pipeline(original_path)
            
            if not result.get('success'):
                return jsonify({
                    'success': False,
                    'error': result.get('error', '检测失败')
                }), 500
            
            process_time = time.time() - start_time
            
            # 构建响应数据
            response_data = {
                'success': True,
                'file_id': file_id,
                'result_image': f"/static/{file_id}_result.jpg",
                'defects': [],
                'analysis': []
            }
            
            # 格式化缺陷数据
            for i, defect in enumerate(result.get('defects', [])):
                defect_info = {
                    'type': defect.get('类别', '未知'),
                    'confidence': defect.get('置信度', 0),
                    'bbox': defect.get('坐标', []),
                    'description': f"{defect.get('类别', '未知')}缺陷",
                    'analysis': defect.get('详细分析', '')
                }
                response_data['defects'].append(defect_info)
                
                # 构建分析数据
                analysis_item = {
                    'type': defect.get('类别', '未知'),
                    'confidence': defect.get('置信度', 0),
                    'description': f"{defect.get('类别', '未知')}缺陷",
                    'causes': [{'cause': '热轧工艺不当', 'source': 'YOLO-Agent'}],
                    'solutions': [{'solution': '优化轧制参数', 'source': 'YOLO-Agent'}],
                    'prevention': [{'method': '定期设备维护', 'source': 'YOLO-Agent'}]
                }
                response_data['analysis'].append(analysis_item)
            
            return jsonify(response_data)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'处理失败: {str(e)}'
            }), 500
    
    return jsonify({'success': False, 'error': '不支持的文件格式'}), 400

@app.route('/api/analyze_image', methods=['POST'])
def analyze_image():
    """分析图片内容"""
    data = request.json
    file_id = data.get('file_id')
    
    # 简单返回分析结果
    analysis = {
        'quality_score': 85,
        'summary': '检测到轻微表面缺陷，建议进行工艺优化。',
        'defect_details': [],
        'suggestions': [
            {'suggestion': '优化轧制工艺参数，减少表面缺陷产生'},
            {'suggestion': '加强原材料质量控制，确保成分均匀'},
            {'suggestion': '定期进行设备维护和校准'}
        ]
    }
    
    return jsonify({'success': True, 'analysis': analysis})

@app.route('/api/generate_report', methods=['POST'])
def generate_report():
    """生成检测报告"""
    data = request.json
    file_id = data.get('file_id')
    
    # 生成简单的HTML报告
    report_html = f"""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>缺陷检测报告</title></head>
    <body>
        <h1>缺陷检测报告</h1>
        <p>文件ID: {file_id}</p>
        <p>检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>检测到缺陷，建议进一步分析。</p>
    </body></html>
    """
    
    report_filename = f"report_{file_id}.html"
    report_path = os.path.join(REPORTS_FOLDER, report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_html)
    
    return jsonify({
        'success': True,
        'report_path': report_filename
    })

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """处理智能问答"""
    data = request.json
    question = data.get('question', '')
    
    # 简单的问题回答逻辑
    answer = "我是工业缺陷分析助手，可以回答关于缺陷检测的问题。"
    
    return jsonify({
        'success': True,
        'answer': answer,
        'sources': ['YOLO-Agent 系统']
    })

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传文件的访问"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/reports/<filename>')
def report_file(filename):
    """提供报告文件的访问"""
    return send_from_directory(REPORTS_FOLDER, filename)

if __name__ == '__main__':
    print("🚀 启动 YOLO-Agent 工业缺陷分析助手...")
    print("📡 服务地址: http://localhost:5000")
    print("🔄 按 Ctrl+C 停止服务")
    app.run(host='0.0.0.0', port=5000, debug=False)
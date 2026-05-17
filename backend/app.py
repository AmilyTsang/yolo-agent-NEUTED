import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import uuid
import shutil

from yolo_detector import YOLODetector
from knowledge_base import KnowledgeBase
from report_generator import ReportGenerator

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = '../uploads'
STATIC_FOLDER = '../static'
REPORTS_FOLDER = '../reports'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER

# 初始化模块
yolo_detector = YOLODetector()
knowledge_base = KnowledgeBase()
report_generator = ReportGenerator()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        file_id = str(uuid.uuid4())
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{file_id}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            results = yolo_detector.detect(filepath)
            
            result_image_path = os.path.join(app.config['STATIC_FOLDER'], f"{file_id}_result.{ext}")
            yolo_detector.draw_boxes(filepath, results, result_image_path)
            
            defect_info = knowledge_base.analyze_defects(results)
            
            return jsonify({
                'success': True,
                'file_id': file_id,
                'original_filename': file.filename,
                'defects': results,
                'analysis': defect_info,
                'result_image': f"/static/{file_id}_result.{ext}"
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/generate_report', methods=['POST'])
def generate_report():
    data = request.json
    file_id = data.get('file_id')
    defects = data.get('defects')
    analysis = data.get('analysis')
    
    if not file_id or not defects or not analysis:
        return jsonify({'error': 'Missing parameters'}), 400
    
    try:
        report_path = report_generator.generate(file_id, defects, analysis)
        return jsonify({
            'success': True,
            'report_path': report_path
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/defect_info/<defect_type>', methods=['GET'])
def get_defect_info(defect_type):
    info = knowledge_base.get_defect_info(defect_type)
    if info:
        return jsonify({'success': True, 'info': info})
    return jsonify({'success': False, 'message': 'Defect type not found'})

@app.route('/api/search_knowledge', methods=['POST'])
def search_knowledge():
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({'error': 'Missing query'}), 400
    
    results = knowledge_base.search(query)
    return jsonify({'success': True, 'results': results})

@app.route('/api/ask', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question')
    file_id = data.get('file_id')
    defects = data.get('defects', [])
    analysis = data.get('analysis', [])
    
    if not question:
        return jsonify({'error': 'Missing question'}), 400
    
    answer = generate_answer(question, defects, analysis)
    
    return jsonify({
        'success': True,
        'answer': answer['content'],
        'sources': answer['sources']
    })

def generate_answer(question, defects, analysis):
    question_lower = question.lower()
    
    # 统计类问题
    if '多少' in question_lower or '几个' in question_lower or \
       '数量' in question_lower or '有多少' in question_lower:
        
        if defects:
            count = len(defects)
            types = list(set(d['type'] for d in defects))
            return {
                'content': f"图片中检测到 {count} 个缺陷，包含 {len(types)} 种类型：{'、'.join(types)}",
                'sources': ['YOLO检测结果']
            }
        else:
            return {
                'content': "图片中未检测到任何缺陷，产品质量良好！",
                'sources': ['YOLO检测结果']
            }
    
    # 特定缺陷类型问题
    defect_type_map = {
        '划痕': '划痕', '裂纹': '裂纹', '凹陷': '凹陷', '凸起': '凸起',
        '腐蚀': '腐蚀', '磨损': '磨损', '变形': '变形', '污渍': '污渍',
        '气泡': '气泡', '断裂': '断裂'
    }
    
    defect_type = None
    for key, value in defect_type_map.items():
        if key in question_lower:
            defect_type = value
            break
    
    if defect_type:
        has_defect = defects and any(d['type'] == defect_type for d in defects)
        info = knowledge_base.get_defect_info(defect_type)
        sources = ['知识库']
        
        if has_defect:
            content = f"图片中检测到 {defect_type} 缺陷。\n"
        else:
            content = f"图片中未检测到 {defect_type} 缺陷。\n"
        
        if info:
            content += f"{defect_type}的描述：{info['description']}\n"
            
            if '原因' in question_lower and info.get('causes'):
                content += "\n可能的原因：\n"
                for i, c in enumerate(info['causes'], 1):
                    content += f"{i}. {c['cause']}（来源：{c['source']}）\n"
                    sources.append(c['source'])
            
            elif '解决' in question_lower or '怎么修' in question_lower:
                content += "\n解决方案：\n"
                for i, s in enumerate(info['solutions'], 1):
                    content += f"{i}. {s['solution']}（来源：{s['source']}）\n"
                    sources.append(s['source'])
            
            elif '预防' in question_lower or '避免' in question_lower:
                content += "\n预防措施：\n"
                for i, p in enumerate(info['prevention'], 1):
                    content += f"{i}. {p['method']}（来源：{p['source']}）\n"
                    sources.append(p['source'])
        
        return {
            'content': content,
            'sources': list(set(sources))
        }
    
    # 综合分析问题
    if '分析' in question_lower or '怎么样' in question_lower:
        if defects:
            content = "检测结果分析：\n\n"
            content += f"共检测到 {len(defects)} 个缺陷。\n\n"
            
            type_counts = {}
            for d in defects:
                type_counts[d['type']] = type_counts.get(d['type'], 0) + 1
            
            content += "缺陷类型分布：\n"
            for defect_type, count in type_counts.items():
                content += f"- {defect_type}: {count}个\n"
            
            content += "\n严重程度评估：\n"
            for i, defect in enumerate(defects, 1):
                severity = get_severity(defect['type'])
                content += f"{i}. {defect['type']} - {severity}\n"
            
            return {
                'content': content,
                'sources': ['YOLO检测结果', '知识库']
            }
        else:
            return {
                'content': "图片中未检测到缺陷，产品质量良好！建议定期进行质量检查以保持产品稳定性。",
                'sources': ['YOLO检测结果']
            }
    
    # 默认回答
    return {
        'content': "我来帮你分析这个问题。\n\n" +
                   "如果你有具体问题，可以问我：\n" +
                   "- 图片中有多少个缺陷？\n" +
                   "- 某个缺陷是什么原因造成的？\n" +
                   "- 如何解决/预防某个缺陷？\n" +
                   "- 帮我分析一下检测结果。",
        'sources': ['系统']
    }

def get_severity(defect_type):
    if defect_type in ['断裂', '裂纹']:
        return '高'
    elif defect_type in ['腐蚀', '变形', '凹陷']:
        return '中'
    else:
        return '低'

@app.route('/api/analyze_image', methods=['POST'])
def analyze_image():
    data = request.json
    file_id = data.get('file_id')
    defects = data.get('defects', [])
    
    if not file_id:
        return jsonify({'error': 'Missing file_id'}), 400
    
    analysis = analyze_image_content(file_id, defects)
    
    return jsonify({
        'success': True,
        'analysis': analysis
    })

def analyze_image_content(file_id, defects):
    result = {
        'summary': '',
        'defect_details': [],
        'suggestions': [],
        'quality_score': 100
    }
    
    if defects:
        score = 100
        for defect in defects:
            severity = get_severity(defect['type'])
            if severity == '高':
                score -= 20
            elif severity == '中':
                score -= 10
            else:
                score -= 5
        score = max(0, score)
        result['quality_score'] = score
        
        type_counts = {}
        for d in defects:
            type_counts[d['type']] = type_counts.get(d['type'], 0) + 1
        
        result['summary'] = f"图片分析完成。共检测到 {len(defects)} 个缺陷，包含 {len(type_counts)} 种类型。"
        
        if score >= 80:
            result['summary'] += " 整体质量良好。"
        elif score >= 60:
            result['summary'] += " 建议进行进一步检查和修复。"
        else:
            result['summary'] += " 质量较差，需要立即处理。"
        
        for i, defect in enumerate(defects, 1):
            info = knowledge_base.get_defect_info(defect['type'])
            result['defect_details'].append({
                'index': i,
                'type': defect['type'],
                'confidence': defect['confidence'],
                'severity': get_severity(defect['type']),
                'bbox': defect['bbox'],
                'description': info['description'] if info else '未知缺陷'
            })
        
        unique_types = list(set(d['type'] for d in defects))
        for defect_type in unique_types:
            info = knowledge_base.get_defect_info(defect_type)
            if info and info.get('solutions'):
                for s in info['solutions'][:2]:
                    result['suggestions'].append({
                        'defect': defect_type,
                        'suggestion': s['solution'],
                        'source': s['source']
                    })
    else:
        result['summary'] = "图片分析完成。未检测到任何缺陷，产品质量优秀！"
        result['quality_score'] = 100
    
    return result

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.config['STATIC_FOLDER'], filename)

@app.route('/uploads/<path:filename>')
def upload_files(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/reports/<path:filename>')
def report_files(filename):
    return send_from_directory(REPORTS_FOLDER, filename)

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(STATIC_FOLDER, exist_ok=True)
    os.makedirs(REPORTS_FOLDER, exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
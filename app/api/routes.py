from datetime import datetime
from flask import Blueprint, request, jsonify, send_from_directory

from app.api.dependencies import (
    save_uploaded_file, get_uploaded_file_path, get_config,
    get_cache_entry, set_cache_entry
)
from app.pipeline.inference_pipeline import InferencePipeline
from app.report.report_generator import ReportGenerator
from app.rag.retriever import RAGRetriever

api_bp = Blueprint('api', __name__)

@api_bp.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': '未上传图片'}), 400
    
    image_file = request.files['image']
    
    result = save_uploaded_file(image_file)
    if not result:
        return jsonify({'success': False, 'error': '不支持的文件格式'}), 400
    
    file_id, image_path = result
    
    return jsonify({
        'success': True,
        'file_id': file_id,
        'image_path': image_path,
        'message': '图片上传成功'
    })

@api_bp.route('/detect', methods=['POST'])
def detect_defects():
    data = request.json
    file_id = data.get('file_id')
    
    if not file_id:
        return jsonify({'success': False, 'error': '缺少file_id'}), 400
    
    image_path = get_uploaded_file_path(file_id)
    if not image_path:
        return jsonify({'success': False, 'error': '未找到图片文件'}), 404
    
    config = get_config()
    pipeline = InferencePipeline(config)
    result = pipeline.run(image_path, file_id)
    
    set_cache_entry(file_id, {
        'result': result,
        'final_decision': result.get('decision', 'pending'),
        'confirmed_by': None,
        'confirmed_at': None
    })
    
    return jsonify(result)

@api_bp.route('/confirm', methods=['POST'])
def confirm_defect():
    data = request.json
    file_id = data.get('file_id')
    user_id = data.get('user_id')
    confirm_decision = data.get('confirm_decision')
    
    cache_entry = get_cache_entry(file_id)
    if not cache_entry:
        return jsonify({'success': False, 'error': '未找到分析记录'}), 404
    
    if confirm_decision not in ['pass', 'reject']:
        return jsonify({'success': False, 'error': '无效的确认决策'}), 400
    
    cache_entry['final_decision'] = 'auto_pass' if confirm_decision == 'pass' else 'auto_reject'
    cache_entry['confirmed_by'] = user_id
    cache_entry['confirmed_at'] = datetime.now().isoformat()
    
    decision_text = '通过' if confirm_decision == 'pass' else '不通过'
    
    return jsonify({
        'success': True,
        'message': f'人工确认成功，判定结果：{decision_text}',
        'decision': cache_entry['final_decision']
    })

@api_bp.route('/auto_decision', methods=['POST'])
def auto_decision():
    data = request.json
    file_id = data.get('file_id')
    
    cache_entry = get_cache_entry(file_id)
    if not cache_entry:
        return jsonify({'success': False, 'error': '未找到分析记录'}), 404
    
    result = cache_entry['result']
    
    if result.get('decision') in ['auto_pass', 'auto_reject']:
        cache_entry['final_decision'] = result['decision']
        cache_entry['confirmed_by'] = 'auto'
        cache_entry['confirmed_at'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'decision': result['decision'],
            'reason': result['decision_reason']
        })
    
    return jsonify({
        'success': False,
        'error': '当前状态需要人工审核',
        'decision': result.get('decision', 'pending')
    })

@api_bp.route('/generate_report', methods=['POST'])
def generate_report():
    data = request.json
    file_id = data.get('file_id')
    
    cache_entry = get_cache_entry(file_id)
    if not cache_entry:
        return jsonify({'success': False, 'error': '未找到分析记录'}), 404
    
    result = cache_entry['result']
    fused_results = result.get('fused_results', [])
    decision = cache_entry.get('final_decision', result.get('decision', 'pending'))
    decision_reason = result.get('decision_reason', '')
    confirmed_by = cache_entry.get('confirmed_by', None)
    confirmed_at = cache_entry.get('confirmed_at', None)
    
    config = get_config()
    report_generator = ReportGenerator(config['system'])
    reports = report_generator.generate(file_id, fused_results, decision, decision_reason, confirmed_by, confirmed_at)
    
    return jsonify({
        'success': True,
        'json_report': reports.get('json'),
        'pdf_report': reports.get('pdf'),
        'message': '报告生成成功' if reports else '报告生成失败'
    })

@api_bp.route('/get_knowledge', methods=['GET'])
def get_knowledge():
    defect_type = request.args.get('defect_type', '')
    
    if not defect_type:
        return jsonify({'success': False, 'error': '缺少defect_type参数'}), 400
    
    config = get_config()
    retriever = RAGRetriever(config['rag'])
    
    return jsonify({
        'success': True,
        'defect_type': defect_type,
        'enterprise_standard': retriever.get_standard(defect_type),
        'historical_cases': retriever.search_cases(defect_type)
    })

@api_bp.route('/reports/<filename>', methods=['GET'])
def download_report(filename):
    from app.core.constants import REPORTS_DIR
    return send_from_directory(REPORTS_DIR, filename, as_attachment=True)
import os
import json
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        self.report_dir = '../reports'
        os.makedirs(self.report_dir, exist_ok=True)
    
    def generate(self, file_id, defects, analysis):
        """生成分析报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"report_{file_id}_{timestamp}.html"
        report_path = os.path.join(self.report_dir, report_filename)
        
        html_content = self._generate_html(file_id, defects, analysis)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_filename
    
    def _generate_html(self, file_id, defects, analysis):
        """生成HTML报告内容"""
        timestamp = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        
        # 统计信息
        defect_counts = {}
        for defect in defects:
            defect_type = defect['type']
            defect_counts[defect_type] = defect_counts.get(defect_type, 0) + 1
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>工业缺陷分析报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
        .report-container {{ max-width: 1000px; margin: 0 auto; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        .report-header {{ background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); color: white; padding: 30px; text-align: center; }}
        .report-header h1 {{ font-size: 24px; margin-bottom: 10px; }}
        .report-header p {{ opacity: 0.9; }}
        .report-body {{ padding: 30px; }}
        .section {{ margin-bottom: 30px; }}
        .section-title {{ color: #2c3e50; font-size: 18px; font-weight: bold; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 2px solid #3498db; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; }}
        .stat-card {{ background: #ecf0f1; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 28px; font-weight: bold; color: #3498db; }}
        .stat-label {{ font-size: 14px; color: #7f8c8d; margin-top: 5px; }}
        .defect-list {{ list-style: none; }}
        .defect-item {{ background: #f8f9fa; border-radius: 8px; padding: 20px; margin-bottom: 15px; border-left: 4px solid #e74c3c; }}
        .defect-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
        .defect-type {{ font-size: 16px; font-weight: bold; color: #2c3e50; }}
        .defect-conf {{ color: #7f8c8d; font-size: 14px; }}
        .defect-desc {{ color: #555; margin-bottom: 15px; }}
        .sub-section {{ margin-bottom: 15px; }}
        .sub-section-title {{ font-size: 14px; font-weight: bold; color: #3498db; margin-bottom: 10px; }}
        .info-list {{ list-style: none; padding-left: 20px; }}
        .info-item {{ position: relative; padding-left: 20px; margin-bottom: 8px; color: #555; }}
        .info-item::before {{ content: '•'; position: absolute; left: 0; color: #3498db; }}
        .source {{ font-size: 12px; color: #95a5a6; margin-left: 10px; }}
        .image-section {{ text-align: center; }}
        .result-image {{ max-width: 100%; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        .report-footer {{ background: #ecf0f1; padding: 20px; text-align: center; color: #7f8c8d; font-size: 14px; }}
        .severity-low {{ border-left-color: #27ae60; }}
        .severity-medium {{ border-left-color: #f39c12; }}
        .severity-high {{ border-left-color: #e74c3c; }}
    </style>
</head>
<body>
    <div class="report-container">
        <div class="report-header">
            <h1>工业缺陷分析报告</h1>
            <p>生成时间: {timestamp}</p>
            <p>检测ID: {file_id}</p>
        </div>
        
        <div class="report-body">
            <div class="section">
                <div class="section-title">📊 检测概览</div>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{len(defects)}</div>
                        <div class="stat-label">检测到的缺陷数量</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{len(defect_counts)}</div>
                        <div class="stat-label">缺陷类型种类</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">📷 检测图像</div>
                <div class="image-section">
                    <img src="/static/{file_id}_result.jpg" alt="检测结果" class="result-image">
                    <p style="margin-top: 10px; color: #7f8c8d; font-size: 14px;">图中标记为检测到的缺陷位置</p>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">🔍 缺陷详细分析</div>
                <ul class="defect-list">
"""
        
        for idx, (defect, info) in enumerate(zip(defects, analysis), 1):
            severity = self._get_severity(defect['type'])
            severity_class = f"severity-{severity}"
            
            html += f"""                    <li class="defect-item {severity_class}">
                        <div class="defect-header">
                            <span class="defect-type">缺陷 #{idx}: {defect['type']}</span>
                            <span class="defect-conf">置信度: {defect['confidence']:.2f}</span>
                        </div>
                        <div class="defect-desc">{info['description']}</div>
                        <div class="defect-desc" style="font-size: 12px; color: #95a5a6;">
                            位置: ({defect['bbox'][0]}, {defect['bbox'][1]}) - ({defect['bbox'][2]}, {defect['bbox'][3]}) 
                            | 面积: {defect['area']} 像素
                        </div>
"""
            
            if info['causes']:
                html += """                        <div class="sub-section">
                            <div class="sub-section-title">💡 可能原因</div>
                            <ul class="info-list>
"""
                for cause in info['causes']:
                    html += f"""                            <li class="info-item">{cause['cause']}<span class="source">[来源: {cause['source']}]</span></li>
"""
                html += """                            </ul>
                        </div>
"""
            
            if info['solutions']:
                html += """                        <div class="sub-section">
                            <div class="sub-section-title">🛠️ 解决方案</div>
                            <ul class="info-list>
"""
                for solution in info['solutions']:
                    html += f"""                            <li class="info-item">{solution['solution']}<span class="source">[来源: {solution['source']}]</span></li>
"""
                html += """                            </ul>
                        </div>
"""
            
            if info['prevention']:
                html += """                        <div class="sub-section">
                            <div class="sub-section-title">✅ 预防措施</div>
                            <ul class="info-list>
"""
                for prevention in info['prevention']:
                    html += f"""                            <li class="info-item">{prevention['method']}<span class="source">[来源: {prevention['source']}]</span></li>
"""
                html += """                            </ul>
                        </div>
"""
            
            html += """                    </li>
"""
        
        html += """                </ul>
            </div>
            
            <div class="section">
                <div class="section-title">📈 缺陷类型统计</div>
                <div style="display: flex; flex-wrap: wrap; gap: 10px;">
"""
        
        for defect_type, count in defect_counts.items():
            html += f"""                    <span style="background: #3498db; color: white; padding: 8px 16px; border-radius: 20px; font-size: 14px;">
                        {defect_type}: {count}个
                    </span>
"""
        
        html += """                </div>
            </div>
        </div>
        
        <div class="report-footer">
            <p>© 2024 YOLO-Agent 工业缺陷分析助手</p>
            <p>本报告仅供参考，请结合实际情况进行判断</p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _get_severity(self, defect_type):
        """判断缺陷严重程度"""
        high_severity = ['断裂', '裂纹']
        medium_severity = ['腐蚀', '变形', '凹陷']
        
        if defect_type in high_severity:
            return 'high'
        elif defect_type in medium_severity:
            return 'medium'
        else:
            return 'low'
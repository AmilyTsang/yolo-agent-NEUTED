HTML_TEMPLATE = """<!DOCTYPE html>
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
        .sub-section {{ margin-bottom: 15px; }}
        .sub-section-title {{ font-size: 14px; font-weight: bold; color: #3498db; margin-bottom: 10px; }}
        .info-list {{ list-style: none; padding-left: 20px; }}
        .info-item {{ position: relative; padding-left: 20px; margin-bottom: 8px; color: #555; }}
        .info-item::before {{ content: '•'; position: absolute; left: 0; color: #3498db; }}
        .report-footer {{ background: #ecf0f1; padding: 20px; text-align: center; color: #7f8c8d; font-size: 14px; }}
        .severity-low {{ border-left-color: #27ae60; }}
        .severity-medium {{ border-left-color: #f39c12; }}
        .severity-high {{ border-left-color: #e74c3c; }}
        .decision-badge {{ display: inline-block; padding: 8px 20px; border-radius: 20px; font-weight: bold; }}
        .decision-pass {{ background: #27ae60; color: white; }}
        .decision-reject {{ background: #e74c3c; color: white; }}
        .decision-review {{ background: #f39c12; color: white; }}
        .decision-pending {{ background: #7f8c8d; color: white; }}
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
                        <div class="stat-value">{total_defects}</div>
                        <div class="stat-label">检测到的缺陷数量</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{defect_types_count}</div>
                        <div class="stat-label">缺陷类型种类</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{high_severity}</div>
                        <div class="stat-label">高风险缺陷</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{medium_severity}</div>
                        <div class="stat-label">中风险缺陷</div>
                    </div>
                </div>
                <div style="margin-top: 20px; text-align: center;">
                    <span class="decision-badge decision-{decision}">{decision_text}</span>
                </div>
                <div style="margin-top: 10px; text-align: center; color: #666; font-size: 14px;">
                    {decision_reason}
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">🔍 缺陷详细分析</div>
                <ul class="defect-list">
                    {defect_items}
                </ul>
            </div>
            
            <div class="section">
                <div class="section-title">📈 缺陷类型统计</div>
                <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                    {defect_stats}
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">📝 判定信息</div>
                <div style="background: #ecf0f1; padding: 20px; border-radius: 8px;">
                    <p><strong>判定方式:</strong> {confirm_method}</p>
                    <p><strong>判定结果:</strong> {decision_text}</p>
                    <p><strong>确认时间:</strong> {confirmed_at}</p>
                    <p><strong>确认人员:</strong> {confirmed_by}</p>
                </div>
            </div>
        </div>
        
        <div class="report-footer">
            <p>© 2024 YOLO-Agent 工业缺陷分析助手</p>
            <p>本报告仅供参考，请结合实际情况进行判断</p>
        </div>
    </div>
</body>
</html>"""

PDF_STYLE = {
    'title': {
        'font_name': 'SimHei',
        'font_size': 18,
        'alignment': 1,
        'space_after': 20
    },
    'heading': {
        'font_name': 'SimHei',
        'font_size': 14,
        'space_after': 10
    },
    'normal': {
        'font_name': 'SimHei',
        'font_size': 12,
        'leading': 18
    },
    'small': {
        'font_name': 'SimHei',
        'font_size': 10,
        'leading': 14
    }
}
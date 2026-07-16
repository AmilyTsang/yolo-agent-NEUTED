import os
from datetime import datetime

from app.report.serializers import ReportSerializer
from app.report.report_template import HTML_TEMPLATE, PDF_STYLE
from app.core.logging import logger

class ReportGenerator:
    def __init__(self, config):
        self.report_dir = config['directories']['reports']
        os.makedirs(self.report_dir, exist_ok=True)
        
        self.formats = config['report']['format']
    
    def generate(self, file_id, fused_results, decision, decision_reason, 
                confirmed_by=None, confirmed_at=None):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        report_paths = {}
        
        if 'json' in self.formats:
            json_path = self._generate_json(file_id, fused_results, decision, 
                                           decision_reason, confirmed_by, confirmed_at, timestamp)
            report_paths['json'] = os.path.basename(json_path)
        
        if 'pdf' in self.formats:
            pdf_path = self._generate_pdf(file_id, fused_results, decision, 
                                         decision_reason, confirmed_by, confirmed_at, timestamp)
            if pdf_path:
                report_paths['pdf'] = os.path.basename(pdf_path)
        
        return report_paths
    
    def _generate_json(self, file_id, fused_results, decision, decision_reason, 
                      confirmed_by, confirmed_at, timestamp):
        report_data = ReportSerializer.serialize_report(
            file_id, fused_results, decision, decision_reason, confirmed_by, confirmed_at
        )
        
        json_path = os.path.join(self.report_dir, f"report_{file_id}_{timestamp}.json")
        ReportSerializer.to_json(report_data, json_path)
        
        return json_path
    
    def _generate_pdf(self, file_id, fused_results, decision, decision_reason, 
                     confirmed_by, confirmed_at, timestamp):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            
            pdfmetrics.registerFont(TTFont('SimHei', 'SimHei.ttf'))
            
            pdf_path = os.path.join(self.report_dir, f"report_{file_id}_{timestamp}.pdf")
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, alignment=1, spaceAfter=20, fontName='SimHei')
            heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, spaceAfter=10, fontName='SimHei')
            normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=12, leading=18, fontName='SimHei')
            small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=10, leading=14, fontName='SimHei')
            
            elements = []
            
            elements.append(Paragraph('工业缺陷分析报告', title_style))
            elements.append(Paragraph(f'生成时间: {datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}', normal_style))
            elements.append(Paragraph(f'检测ID: {file_id}', normal_style))
            elements.append(Spacer(1, 20))
            
            elements.append(Paragraph('📊 检测概览', heading_style))
            
            defect_summary = ReportSerializer.serialize_defect_summary(fused_results)
            
            stats_data = [
                ['统计项', '数值'],
                ['检测到的缺陷数量', str(defect_summary['total'])],
                ['缺陷类型种类', str(len(defect_summary['types']))],
                ['高风险缺陷', str(defect_summary['high_severity'])],
                ['中风险缺陷', str(defect_summary['medium_severity'])]
            ]
            
            stats_table = Table(stats_data, colWidths=[2*inch, 2*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'SimHei'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(stats_table)
            elements.append(Spacer(1, 15))
            
            decision_text_map = {'auto_pass': '自动通过', 'auto_reject': '自动判NG', 'manual_review': '人工审核', 'pending': '待确认'}
            decision_colors = {'auto_pass': colors.green, 'auto_reject': colors.red, 'manual_review': colors.orange, 'pending': colors.grey}
            
            decision_data = [['判定结果', decision_text_map.get(decision, '待确认')], ['判定理由', decision_reason]]
            decision_table = Table(decision_data, colWidths=[2*inch, 4*inch])
            decision_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), decision_colors.get(decision, colors.grey)),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'SimHei'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(decision_table)
            elements.append(Spacer(1, 20))
            
            if fused_results:
                elements.append(Paragraph('🔍 缺陷详细分析', heading_style))
                for idx, defect in enumerate(fused_results, 1):
                    severity = defect.get('severity', 'medium')
                    severity_text = {'high': '高', 'medium': '中', 'low': '低'}.get(severity, '中')
                    
                    elements.append(Paragraph(f'缺陷 #{idx}: {defect.get("defect_type", "unknown")}', normal_style))
                    elements.append(Paragraph(f'置信度: {defect.get("confidence_level", 0):.4f} | 风险等级: {severity_text}', small_style))
                    
                    if defect.get('evidence'):
                        elements.append(Paragraph('分析依据:', small_style))
                        for evidence in defect.get('evidence', []):
                            elements.append(Paragraph(f'• {evidence}', small_style))
                    
                    if defect.get('causes'):
                        elements.append(Paragraph(f'成因分析: {defect["causes"]}', small_style))
                    if defect.get('measures'):
                        elements.append(Paragraph(f'解决措施: {defect["measures"]}', small_style))
                    if defect.get('suggestions'):
                        elements.append(Paragraph(f'预防建议: {defect["suggestions"]}', small_style))
                    if defect.get('recommendation'):
                        elements.append(Paragraph(f'处理建议: {defect["recommendation"]}', small_style))
                    
                    elements.append(Spacer(1, 10))
            
            if defect_summary['types']:
                elements.append(Paragraph('📈 缺陷类型统计', heading_style))
                count_data = [['缺陷类型', '数量']]
                for defect_type, count in defect_summary['types'].items():
                    count_data.append([defect_type, str(count)])
                
                count_table = Table(count_data, colWidths=[3*inch, 2*inch])
                count_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'SimHei'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(count_table)
                elements.append(Spacer(1, 15))
            
            elements.append(Paragraph('📝 判定信息', heading_style))
            
            confirm_data = [
                ['判定方式', '人工确认' if confirmed_by and confirmed_by != 'auto' else '自动决策'],
                ['确认人员', confirmed_by if confirmed_by else '未确认'],
                ['确认时间', confirmed_at if confirmed_at else '未确认']
            ]
            
            confirm_table = Table(confirm_data, colWidths=[2*inch, 4*inch])
            confirm_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'SimHei'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(confirm_table)
            elements.append(Spacer(1, 20))
            
            elements.append(Paragraph('© 2024 YOLO-Agent 工业缺陷分析助手', small_style))
            elements.append(Paragraph('本报告仅供参考，请结合实际情况进行判断', small_style))
            
            doc.build(elements)
            return pdf_path
            
        except ImportError:
            logger.warning("reportlab库未安装，无法生成PDF报告")
            return None
        except Exception as e:
            logger.error(f"生成PDF报告失败: {str(e)}")
            return None
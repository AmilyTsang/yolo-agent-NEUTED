class PromptBuilder:
    def __init__(self, system_prompt=None):
        self.system_prompt = system_prompt or "你是宝钢热轧产线资深工程师，精通钢板表面缺陷分析与处理。"
    
    def build_defect_prompt(self, yolo_category, yolo_confidence, threshold, 
                           enterprise_standard, historical_cases):
        prompt_text = f"""你是宝钢热轧产线资深工程师，专业从事钢板表面缺陷分析。

【检测信息】
- YOLO预测类别: {yolo_category}
- YOLO置信度: {yolo_confidence:.4f}
- 置信度阈值: {threshold}

【企业缺陷标准】
{enterprise_standard}

【历史相似案例】
{historical_cases}

【任务要求】
请仔细分析ROI区域和整图，结合上述信息，输出结构化分析结果。

【输出格式】
{{
  "defect_type": "缺陷类别名称",
  "evidence": ["分析依据1", "分析依据2"],
  "severity": "high/medium/low",
  "causes": "产线成因分析",
  "measures": "解决措施",
  "suggestions": "预防建议"
}}

注意：风险等级判断标准-high：影响产品使用安全；medium：影响外观或性能；low：轻微瑕疵可忽略。"""
        
        return prompt_text
    
    def build_chat_messages(self, images, prompt_text):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": []}
        ]
        
        for i, img in enumerate(images):
            messages[1]["content"].append({"type": "image", "image": img})
            if i == 0:
                messages[1]["content"].append({"type": "text", "text": "【缺陷区域图片(ROI)】"})
        
        messages[1]["content"].append({"type": "text", "text": prompt_text})
        
        return messages
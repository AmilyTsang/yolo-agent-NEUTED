import os
import json
from app.utils.logger import logger

class KnowledgeLoader:
    def __init__(self, config):
        self.standard_dir = config['knowledge']['enterprise_standard']
        self.cases_dir = config['knowledge']['historical_cases']
        self.guidelines_dir = config['knowledge']['repair_guidelines']
        self.manual_dir = config['knowledge']['defect_manual']
        
        self.standards = {}
        self.cases = {}
        self._load_knowledge()
    
    def _load_knowledge(self):
        self._load_standards()
        self._load_cases()
    
    def _load_standards(self):
        try:
            standard_files = [f for f in os.listdir(self.standard_dir) if f.endswith('.json')]
            for file in standard_files:
                filepath = os.path.join(self.standard_dir, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.standards.update(data)
            logger.info(f"加载企业标准成功，共{len(self.standards)}种缺陷类型")
        except Exception as e:
            logger.error(f"加载企业标准失败: {str(e)}")
    
    def _load_cases(self):
        try:
            case_files = [f for f in os.listdir(self.cases_dir) if f.endswith('.json')]
            for file in case_files:
                filepath = os.path.join(self.cases_dir, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cases.update(data)
            logger.info(f"加载历史案例成功，共{len(self.cases)}种缺陷类型")
        except Exception as e:
            logger.error(f"加载历史案例失败: {str(e)}")
    
    def get_standard(self, defect_type):
        return self.standards.get(defect_type, {})
    
    def get_cases(self, defect_type, top_k=2):
        cases = self.cases.get(defect_type, [])
        sorted_cases = sorted(cases, key=lambda x: x.get('similarity', 0), reverse=True)
        return sorted_cases[:top_k]
    
    def get_standard_text(self, defect_type):
        info = self.get_standard(defect_type)
        if info:
            return f"名称: {info.get('name', '')}\n描述: {info.get('description', '')}\n判定标准: {info.get('standard', '')}\n严重等级: {info.get('severity', '')}\n来源: {info.get('source', '')}"
        return "未找到相关企业标准"
    
    def get_cases_text(self, defect_type):
        cases = self.get_cases(defect_type)
        if cases:
            cases_text = []
            for i, case in enumerate(cases, 1):
                cases_text.append(f"案例{i}: {case.get('description', '')}\n解决方案: {case.get('solution', '')}")
            return "\n".join(cases_text)
        return "未找到历史相似案例"
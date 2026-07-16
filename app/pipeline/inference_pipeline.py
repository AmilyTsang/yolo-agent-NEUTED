from app.detector.preprocess import Preprocessor
from app.detector.yolo_detector import YOLODetector
from app.detector.postprocess import parse_detections
from app.verifier.qwen_verifier import QwenVerifier
from app.verifier.prompt_builder import PromptBuilder
from app.rag.retriever import RAGRetriever
from app.fusion.fusion_engine import FusionEngine
from app.decision.decision_engine import DecisionEngine
from app.report.report_generator import ReportGenerator
from app.pipeline.context import PipelineContext
from app.pipeline.exceptions import (
    PipelineException, PreprocessingException, DetectionException,
    VerificationException, FusionException, DecisionException, ReportException
)
from app.core.constants import CONFIDENCE_THRESHOLD, ROI_EXPANSION_RATIO
from app.core.logging import logger
from app.utils.image_utils import crop_roi, image_to_pil

class InferencePipeline:
    def __init__(self, config):
        self.yolo_config = config['yolo']
        self.qwen_config = config['qwen']
        self.rag_config = config['rag']
        self.decision_rules_config = config['decision_rules']
        self.system_config = config['system']
        
        self.preprocessor = Preprocessor()
        self.detector = YOLODetector(self.yolo_config)
        self.verifier = QwenVerifier(self.qwen_config)
        self.retriever = RAGRetriever(self.rag_config)
        self.fusion_engine = FusionEngine(self.rag_config)
        self.decision_engine = DecisionEngine(self.decision_rules_config)
        self.report_generator = ReportGenerator(self.system_config)
        
        self.confidence_threshold = self.yolo_config['confidence'].get('threshold', CONFIDENCE_THRESHOLD)
        self.expansion_ratio = ROI_EXPANSION_RATIO
        self.classes = self.yolo_config.get('classes', [])
    
    def run(self, image_path: str, file_id: str = None) -> dict:
        logger.info(f"开始缺陷检测流程: {image_path}")
        
        context = PipelineContext(
            file_id=file_id,
            image_path=image_path,
            config={'yolo': self.yolo_config, 'qwen': self.qwen_config}
        )
        
        try:
            self._preprocess(context)
            self._detect(context)
            
            if not context.detections:
                context.success = True
                context.decision = 'auto_pass'
                context.decision_reason = '未检测到缺陷，自动通过'
                logger.info("未检测到缺陷，自动通过")
                return context.to_dict()
            
            self._verify(context)
            self._fusion(context)
            self._decision(context)
            
            if file_id:
                self._report(context)
            
            context.success = True
            logger.info(f"缺陷检测流程完成，判定结果: {context.decision}")
            
        except PipelineException as e:
            logger.error(f"缺陷检测流程失败({e.step}): {e.message}")
            context.error = e.message
        except Exception as e:
            logger.error(f"缺陷检测流程失败: {str(e)}")
            context.error = str(e)
        
        return context.to_dict()
    
    def _preprocess(self, context: PipelineContext):
        try:
            logger.info(f"开始图像预处理: {context.image_path}")
            context.preprocessed = self.preprocessor.process(context.image_path)
            logger.info("图像预处理完成")
        except Exception as e:
            raise PreprocessingException(f"图像预处理失败: {str(e)}")
    
    def _detect(self, context: PipelineContext):
        try:
            logger.info(f"开始YOLO检测: {context.image_path}")
            results = self.detector.detect(context.image_path)
            context.detections = parse_detections(results, self.classes)
            logger.info(f"YOLO检测完成，检测到{len(context.detections)}个缺陷")
        except Exception as e:
            raise DetectionException(f"YOLO检测失败: {str(e)}")
    
    def _verify(self, context: PipelineContext):
        try:
            logger.info("开始Qwen2-VL验证")
            full_image = context.preprocessed.get('rgb')
            pil_image = image_to_pil(full_image) if full_image else None
            
            context.qwen_results = []
            for detection in context.detections:
                if detection['confidence'] >= self.confidence_threshold:
                    logger.info(f"置信度{self.confidence_threshold}以上，跳过Qwen验证")
                    context.qwen_results.append(None)
                    continue
                
                bbox = detection['bbox']
                roi_image = crop_roi(pil_image, bbox, self.expansion_ratio) if pil_image else None
                
                enterprise_standard = self.retriever.get_standard_text(detection['defect_type'])
                historical_cases = self.retriever.get_cases_text(detection['defect_type'])
                
                if roi_image:
                    result = self.verifier.verify(
                        roi_image, pil_image,
                        detection['defect_type'],
                        detection['confidence'],
                        enterprise_standard,
                        historical_cases,
                        self.confidence_threshold
                    )
                    context.qwen_results.append(result)
                    logger.info(f"Qwen2-VL验证完成，结果: {result.get('defect_type', 'unknown')}")
                else:
                    context.qwen_results.append(None)
            
        except Exception as e:
            raise VerificationException(f"Qwen2-VL验证失败: {str(e)}")
    
    def _fusion(self, context: PipelineContext):
        try:
            logger.info("开始Detection Fusion")
            context.fused_results = self.fusion_engine.fuse(
                context.detections, context.qwen_results
            )
            logger.info(f"Detection Fusion完成，共{len(context.fused_results)}个融合结果")
        except Exception as e:
            raise FusionException(f"Detection Fusion失败: {str(e)}")
    
    def _decision(self, context: PipelineContext):
        try:
            logger.info("开始Decision Engine")
            result = self.decision_engine.decide(context.fused_results)
            context.decision = result['decision']
            context.decision_reason = result['decision_reason']
            context.needs_review = result['needs_review']
            logger.info(f"Decision Engine完成，判定结果: {context.decision}")
        except Exception as e:
            raise DecisionException(f"决策引擎失败: {str(e)}")
    
    def _report(self, context: PipelineContext):
        try:
            logger.info("开始报告生成")
            context.reports = self.report_generator.generate(
                context.file_id,
                context.fused_results,
                context.decision,
                context.decision_reason
            )
            logger.info(f"报告生成完成: {context.reports}")
        except Exception as e:
            raise ReportException(f"报告生成失败: {str(e)}")
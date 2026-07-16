import os
import torch
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration
from peft import PeftModel
from app.verifier.base import BaseVerifier
from app.verifier.prompt_builder import PromptBuilder
from app.verifier.parser import OutputParser
from app.core.logging import logger

class QwenVerifier(BaseVerifier):
    def __init__(self, config):
        self.base_path = config['model']['base_path']
        self.adapter_path = config['model'].get('adapter_path', '')
        self.device = config['inference']['device']
        self.max_new_tokens = config['inference']['max_new_tokens']
        self.temperature = config['inference']['temperature']
        self.do_sample = config['inference'].get('do_sample', False)
        self.system_prompt = config['prompt'].get('system', '')
        
        self.model = None
        self.processor = None
        self.prompt_builder = PromptBuilder(self.system_prompt)
        self.parser = OutputParser()
    
    def load_model(self):
        if self.model is None:
            try:
                self.processor = AutoProcessor.from_pretrained(self.base_path, trust_remote_code=True)
                self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                    self.base_path,
                    torch_dtype=torch.bfloat16,
                    device_map=self.device,
                    trust_remote_code=True
                )
                
                if self.adapter_path and os.path.exists(self.adapter_path):
                    self.model = PeftModel.from_pretrained(self.model, self.adapter_path)
                
                self.model.eval()
                logger.info(f"Qwen2-VL模型加载成功: {self.base_path}")
            except Exception as e:
                logger.error(f"Qwen2-VL模型加载失败: {str(e)}")
                raise
    
    def verify(self, roi_image, full_image, defect_type, confidence, 
              enterprise_standard, historical_cases, threshold=0.6):
        self.load_model()
        
        prompt_text = self.prompt_builder.build_defect_prompt(
            defect_type, confidence, threshold,
            enterprise_standard, historical_cases
        )
        
        messages = self.prompt_builder.build_chat_messages([roi_image, full_image], prompt_text)
        
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.processor(text=text, images=[roi_image, full_image], return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                temperature=self.temperature,
                do_sample=self.do_sample
            )
        
        response = self.processor.decode(outputs[0], skip_special_tokens=True)
        if "assistant" in response:
            response = response.split("assistant")[-1].strip()
        
        return self.parser.parse_json(response)
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.pipeline.inference_pipeline import InferencePipeline
from app.core.config import get_all_configs
from app.core.logging import setup_logging

logger = setup_logging('evaluate_pipeline')

def main(image_path):
    logger.info(f"开始评估检测流程: {image_path}")
    
    try:
        config = get_all_configs()
        pipeline = InferencePipeline(config)
        
        result = pipeline.run(image_path)
        
        logger.info(f"评估完成，结果:")
        logger.info(f"  成功: {result['success']}")
        logger.info(f"  缺陷数量: {len(result['defects'])}")
        logger.info(f"  融合结果数量: {len(result['fused_results'])}")
        logger.info(f"  决策: {result['decision']}")
        logger.info(f"  决策理由: {result['decision_reason']}")
        
        if result.get('error'):
            logger.error(f"错误: {result['error']}")
            
        return result
        
    except Exception as e:
        logger.error(f"评估失败: {str(e)}")
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python evaluate_pipeline.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    main(image_path)
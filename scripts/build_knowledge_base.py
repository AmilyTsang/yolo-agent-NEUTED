import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.knowledge_loader import KnowledgeLoader
from app.rag.vector_store import VectorStore
from app.rag.embedding import EmbeddingModel
from app.core.logging import setup_logging

logger = setup_logging('build_knowledge_base')

def main():
    logger.info("开始构建知识库...")
    
    try:
        embedding_model = EmbeddingModel()
        vector_store = VectorStore(embedding_model)
        knowledge_loader = KnowledgeLoader()
        
        logger.info("加载企业标准...")
        standards = knowledge_loader.load_enterprise_standards()
        logger.info(f"加载了{len(standards)}条企业标准")
        
        logger.info("加载历史案例...")
        cases = knowledge_loader.load_historical_cases()
        logger.info(f"加载了{len(cases)}条历史案例")
        
        logger.info("构建向量索引...")
        vector_store.build_index(standards + cases)
        
        logger.info("保存索引...")
        vector_store.save_index()
        
        logger.info("知识库构建完成！")
        
    except Exception as e:
        logger.error(f"构建知识库失败: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
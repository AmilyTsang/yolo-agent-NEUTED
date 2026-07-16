from app.rag.knowledge_loader import KnowledgeLoader
from app.rag.embedding import EmbeddingModel
from app.rag.vector_store import SimpleVectorStore
from app.utils.logger import logger

class RAGRetriever:
    def __init__(self, config):
        self.knowledge_loader = KnowledgeLoader(config)
        self.embedding = EmbeddingModel(config['embedding']['model'])
        self.top_k = config['vector_store']['top_k']
        
        self.vector_store = SimpleVectorStore()
        self._build_index()
    
    def _build_index(self):
        defect_types = list(self.knowledge_loader.standards.keys())
        if defect_types:
            vectors = self.embedding.encode(defect_types)
            for defect_type, vector in zip(defect_types, vectors):
                self.vector_store.add(
                    defect_type,
                    vector,
                    self.knowledge_loader.get_standard(defect_type)
                )
            logger.info(f"RAG索引构建完成，共{len(defect_types)}个缺陷类型")
    
    def search_standard(self, defect_type):
        if not self.vector_store.vectors:
            return self.knowledge_loader.get_standard(defect_type)
        
        query_vector = self.embedding.encode([defect_type])[0]
        results = self.vector_store.search(query_vector, top_k=1)
        
        if results:
            return results[0]['metadata']
        return self.knowledge_loader.get_standard(defect_type)
    
    def search_cases(self, defect_type):
        return self.knowledge_loader.get_cases(defect_type, self.top_k)
    
    def get_standard_text(self, defect_type):
        return self.knowledge_loader.get_standard_text(defect_type)
    
    def get_cases_text(self, defect_type):
        return self.knowledge_loader.get_cases_text(defect_type)
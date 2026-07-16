from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def encode(self, texts):
        return self.model.encode(texts)
    
    def similarity(self, vec1, vec2):
        from sklearn.metrics.pairwise import cosine_similarity
        return cosine_similarity([vec1], [vec2])[0][0]
class SimpleVectorStore:
    def __init__(self):
        self.vectors = {}
        self.data = {}
    
    def add(self, key, vector, metadata):
        self.vectors[key] = vector
        self.data[key] = metadata
    
    def search(self, query_vector, top_k=3):
        from sklearn.metrics.pairwise import cosine_similarity
        
        results = []
        for key, vector in self.vectors.items():
            similarity = cosine_similarity([query_vector], [vector])[0][0]
            results.append({
                'key': key,
                'similarity': similarity,
                'metadata': self.data[key]
            })
        
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
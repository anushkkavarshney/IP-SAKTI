import json
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

class LegalSearchEngine:
    def __init__(self, corpus_path="rag_engine/processed_data/corpus.json"):
        with open(corpus_path, "r", encoding="utf-8") as f:
            self.corpus = json.load(f)
            
        self.contents = [doc["content"] for doc in self.corpus]
        
        tokenized_corpus = [doc.lower().split(" ") for doc in self.contents]
        self.bm25 = BM25Okapi(tokenized_corpus)
        
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.embeddings = self.model.encode(self.contents, convert_to_tensor=False)

    def search_bm25(self, query, top_k=10):
        tokenized_query = query.lower().split(" ")
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [(idx, float(scores[idx])) for idx in top_indices if scores[idx] > 0]

    def search_vector(self, query, top_k=10):
        query_embedding = self.model.encode(query, convert_to_tensor=False)
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        top_indices = np.argsort(similarities)[::-1][:top_k]
        return [(idx, float(similarities[idx])) for idx in top_indices]

    def hybrid_search(self, query, jurisdiction="India", top_k=5, k_rrf=60):
        bm25_results = self.search_bm25(query, top_k=20)
        vector_results = self.search_vector(query, top_k=20)

        rrf_scores = {}
        
        for rank, (idx, _) in enumerate(bm25_results):
            rrf_scores[idx] = rrf_scores.get(idx, 0) + 1.0 / (k_rrf + rank + 1)
            
        for rank, (idx, _) in enumerate(vector_results):
            rrf_scores[idx] = rrf_scores.get(idx, 0) + 1.0 / (k_rrf + rank + 1)

        sorted_indices = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        
        final_results = []
        for idx in sorted_indices:
            doc = self.corpus[idx]
            if doc["jurisdiction"].lower() == jurisdiction.lower():
                final_results.append(doc)
            if len(final_results) == top_k:
                break
                
        return final_results

if __name__ == "__main__":
    engine = LegalSearchEngine()
    test_query = "traditional knowledge patent exclusions"
    results = engine.hybrid_search(test_query, jurisdiction="India", top_k=3)
    
    print(f"\n--- Top {len(results)} Results for Query: '{test_query}' ---")
    for r in results:
        print(f"[{r['act_name']} | {r['section']}] -> {r['content'][:150]}...\n")
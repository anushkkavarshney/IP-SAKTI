import json
import os
import re
import hashlib
import pickle
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer


def _tokenize(text):
    """Lowercase, alphanumeric-only tokenizer. Strips punctuation so
    'section,' matches 'section' instead of being treated as a distinct token."""
    return re.findall(r"[a-z0-9]+", text.lower())


class LegalSearchEngine:
    def __init__(self, corpus_path="rag_engine/processed_data/corpus.json"):
        with open(corpus_path, "r", encoding="utf-8") as f:
            self.corpus = json.load(f)

        self.contents = [doc["content"] for doc in self.corpus]

        tokenized_corpus = [_tokenize(doc) for doc in self.contents]
        self.bm25 = BM25Okapi(tokenized_corpus)

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # --- Embedding persistence: avoid re-encoding all chunks on every restart ---
        cache_dir = os.path.dirname(corpus_path)
        corpus_fingerprint = hashlib.md5(
            json.dumps(self.contents, sort_keys=False).encode("utf-8")
        ).hexdigest()
        cache_file = os.path.join(cache_dir, f"embeddings_cache_{corpus_fingerprint}.pkl")

        if os.path.exists(cache_file):
            with open(cache_file, "rb") as f:
                self.embeddings = pickle.load(f)
        else:
            self.embeddings = self.model.encode(self.contents, convert_to_tensor=False)
            os.makedirs(cache_dir, exist_ok=True)
            with open(cache_file, "wb") as f:
                pickle.dump(self.embeddings, f)
            # Remove stale cache files left over from older corpus versions
            for fname in os.listdir(cache_dir):
                if fname.startswith("embeddings_cache_") and fname != os.path.basename(cache_file):
                    try:
                        os.remove(os.path.join(cache_dir, fname))
                    except OSError:
                        pass

    def search_bm25(self, query, top_k=10):
        tokenized_query = _tokenize(query)
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

    def hybrid_search(self, query, jurisdiction="India", category=None, top_k=5, k_rrf=60):
        """
        category: optional legal-domain filter (e.g. "ABS_BIODIVERSITY", "IP_PATENT",
        "REGULATORY_AYUSH", "REGULATORY_COSMETICS", "REGULATORY_NUTRACEUTICAL").
        When provided, only chunks whose corpus 'category' field matches exactly
        are eligible for return. When None (default), behavior is unchanged from
        before — jurisdiction-only filtering.
        """
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
            if doc["jurisdiction"].lower() != jurisdiction.lower():
                continue
            if category is not None and doc.get("category") != category:
                continue
            final_results.append(doc)
            if len(final_results) == top_k:
                break

        return final_results


if __name__ == "__main__":
    engine = LegalSearchEngine()

    test_query = "traditional knowledge patent exclusions"
    results = engine.hybrid_search(test_query, jurisdiction="India", top_k=3)
    print(f"\n--- Top {len(results)} Results for Query: '{test_query}' (no category filter) ---")
    for r in results:
        print(f"[{r['act_name']} | {r['section']}] -> {r['content'][:150]}...\n")

    test_query2 = "benefit sharing biodiversity access"
    results2 = engine.hybrid_search(test_query2, jurisdiction="India", category="ABS_BIODIVERSITY", top_k=3)
    print(f"\n--- Top {len(results2)} Results for Query: '{test_query2}' (category=ABS_BIODIVERSITY) ---")
    for r in results2:
        assert r["category"] == "ABS_BIODIVERSITY", "Category filter leaked a non-matching doc!"
        print(f"[{r['act_name']} | {r['section']}] -> {r['content'][:150]}...\n")
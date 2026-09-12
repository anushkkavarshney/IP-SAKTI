import json
import os
import sys

# Make this module importable/runnable from any location, without requiring
# the caller to manually add rag_engine to sys.path first.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from search import LegalSearchEngine


class LegalRetriever:
    def __init__(self):
        self.engine = LegalSearchEngine()

    def get_relevant_context(
        self,
        query: str,
        jurisdiction: str = "India",
        category: str = None,
        top_k: int = 3
    ) -> list:
        """
        category: optional legal-domain filter passed through to hybrid_search
        (e.g. "ABS_BIODIVERSITY", "IP_PATENT", "REGULATORY_AYUSH",
        "REGULATORY_COSMETICS", "REGULATORY_NUTRACEUTICAL"). Leave as None
        for unfiltered retrieval (existing callers are unaffected).
        """
        raw_results = self.engine.hybrid_search(
            query=query,
            jurisdiction=jurisdiction,
            category=category,
            top_k=top_k
        )

        formatted_chunks = []
        for res in raw_results:
            formatted_chunks.append({
                "doc_id": res.get("doc_id"),
                "act_name": res.get("act_name"),
                "section": res.get("section"),
                "as_of_date": res.get("as_of_date"),
                "effective_date": res.get("effective_date"),
                "jurisdiction": res.get("jurisdiction"),
                "category": res.get("category"),
                "authority": res.get("authority"),
                "source_url": res.get("source_url"),
                "content": res.get("content")
            })
        return formatted_chunks


if __name__ == "__main__":
    retriever = LegalRetriever()

    test_data = retriever.get_relevant_context("Biological resource access permission", top_k=2)
    print("--- No category filter ---")
    print(json.dumps(test_data, indent=2))

    test_data_filtered = retriever.get_relevant_context(
        "Biological resource access permission",
        category="ABS_BIODIVERSITY",
        top_k=2
    )
    print("\n--- category=ABS_BIODIVERSITY ---")
    print(json.dumps(test_data_filtered, indent=2))
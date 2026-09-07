import json
from search import LegalSearchEngine

class LegalRetriever:
    def __init__(self):
        self.engine = LegalSearchEngine()

    def get_relevant_context(self, query: str, jurisdiction: str = "India", top_k: int = 3) -> list:
        raw_results = self.engine.hybrid_search(query=query, jurisdiction=jurisdiction, top_k=top_k)
        
        formatted_chunks = []
        for res in raw_results:
            formatted_chunks.append({
                "doc_id": res.get("doc_id"),
                "act_name": res.get("act_name"),
                "section": res.get("section"),
                "as_of_date": res.get("as_of_date"),
                "jurisdiction": res.get("jurisdiction"),
                "category": res.get("category"),
                "content": res.get("content")
            })
        return formatted_chunks

if __name__ == "__main__":
    retriever = LegalRetriever()
    test_data = retriever.get_relevant_context("Biological resource access permission", top_k=2)
    print(json.dumps(test_data, indent=2))
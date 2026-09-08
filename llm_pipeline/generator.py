"""
LLM Generator & Orchestrator for IP-SAKTI Module 3.
Pairs RAG retrieved evidence with legal reasoning prompts to formulate legal compliance outputs.
"""

import sys
import os
from typing import Dict, Any

# Ensure root directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_engine.retriever import LegalRetriever
from llm_pipeline.prompts import SYSTEM_PROMPT_LEGAL_EXPERT, LEGAL_ANALYSIS_PROMPT_TEMPLATE


class LegalReasoningPipeline:
    def __init__(self, corpus_path: str = "rag_engine/processed_data/corpus.json"):
        self.retriever = LegalRetriever(corpus_path=corpus_path)

    def format_evidence_block(self, evidence_list: list) -> str:
        """Formats evidence objects into readable text block for LLM context."""
        if not evidence_list:
            return "No specific statutory evidence found."

        formatted_blocks = []
        for item in evidence_list:
            hierarchy = item.get("citation_hierarchy", {}) or {}
            section_info = hierarchy.get("clause") or hierarchy.get("section") or item.get("section", "N/A")
            
            block = (
                f"[{item.get('evidence_id')}] Document: {item.get('document')}\n"
                f"Section/Provision: {section_info}\n"
                f"Domain: {item.get('legal_domain')}\n"
                f"Text Excerpt: {item.get('text', '').strip()}\n"
            )
            formatted_blocks.append(block)

        return "\n---\n".join(formatted_blocks)

    def generate_prompt_payload(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Retrieves evidence via RAG and constructs the complete LLM prompt payload.
        """
        # Step 1: Retrieve enriched evidence
        rag_response = self.retriever.retrieve_evidence(query, top_k=top_k)
        
        evidence_text = self.format_evidence_block(rag_response.get("evidence", []))
        matched_entities = ", ".join(rag_response.get("matched_entities", [])) or "None detected"

        # Step 2: Construct Prompt
        user_prompt = LEGAL_ANALYSIS_PROMPT_TEMPLATE.format(
            user_query=query,
            retrieved_evidence=evidence_text,
            matched_entities=matched_entities
        )

        return {
            "system_prompt": SYSTEM_PROMPT_LEGAL_EXPERT,
            "user_prompt": user_prompt,
            "rag_metadata": {
                "jurisdiction": rag_response.get("jurisdiction"),
                "matched_entities": rag_response.get("matched_entities"),
                "evidence_count": len(rag_response.get("evidence", []))
            },
            "raw_evidence": rag_response.get("evidence", [])
        }


if __name__ == "__main__":
    pipeline = LegalReasoningPipeline()
    sample_query = "The formulation uses Ashwagandha root extract as a biological resource."
    payload = pipeline.generate_prompt_payload(sample_query, top_k=2)

    print("================ SYSTEM PROMPT ================")
    print(payload["system_prompt"])
    print("\n================ CONSTRUCTED USER PROMPT ================")
    print(payload["user_prompt"])
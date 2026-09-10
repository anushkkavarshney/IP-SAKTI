"""
LLM Generator & Orchestrator for IP-SAKTI Module 3.
Pairs RAG retrieved evidence with legal reasoning prompts to formulate legal compliance outputs.

FIXED (per backend/app/services/rag_adapter.py + rag_engine/retriever.py, confirmed
2026-09-10): Member 4's real interface is `LegalRetriever()` (no constructor args)
with `.get_relevant_context(query, jurisdiction=..., top_k=...)`, returning a plain
list of dicts with keys `doc_id`, `act_name`, `section`, `as_of_date`, `jurisdiction`,
`category`, `content` — NOT the `.retrieve_evidence()` / `{"evidence": [...]}` shape
this file used to assume. This version normalizes evidence to a consistent shape
(mirroring what backend's rag_adapter.py already does) so the rest of this module,
guardrails.py, and interface.py don't need to know about Member 4's raw field names.
"""

import sys
import os
from typing import Dict, Any, List

# Ensure root directory is in path (so `rag_engine.retriever` resolves)
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.append(_REPO_ROOT)

# rag_engine/retriever.py does a bare `from search import LegalSearchEngine`,
# which only works if rag_engine/'s own directory is on sys.path too.
_RAG_ENGINE_DIR = os.path.join(_REPO_ROOT, "rag_engine")
if _RAG_ENGINE_DIR not in sys.path:
    sys.path.append(_RAG_ENGINE_DIR)

from rag_engine.retriever import LegalRetriever
from llm_pipeline.prompts import (
    SYSTEM_PROMPT_LEGAL_EXPERT,
    LEGAL_ANALYSIS_PROMPT_TEMPLATE,
    SYSTEM_PROMPT_ROADMAP_GENERATOR,
    ROADMAP_GENERATION_PROMPT_TEMPLATE,
)
from llm_pipeline.llm_client import call_llm_json
from llm_pipeline.classification import classify_formulation
from llm_pipeline.routing import route
from llm_pipeline.guardrails import verify_grounding, check_cautious_language


NOT_PROVIDED = "Not provided by the legal corpus yet"


def _normalize_evidence(raw_results: List[dict]) -> List[Dict[str, Any]]:
    """
    Converts Member 4's raw evidence dicts (doc_id, act_name, section,
    as_of_date, jurisdiction, category, content) into the normalized shape
    used everywhere else in this module — same field names as
    backend/app/services/rag_adapter.py uses, so both sides of the system
    agree on evidence shape.

    LEGAL SAFETY: never invents a value for a missing field — uses an
    honest NOT_PROVIDED placeholder instead (e.g. authority, source_url).
    """
    normalized = []
    for item in raw_results:
        normalized.append(
            {
                "id": item.get("doc_id"),
                "jurisdiction": item.get("jurisdiction") or "India",
                "legal_domain": item.get("category") or NOT_PROVIDED,
                "document_name": item.get("act_name") or NOT_PROVIDED,
                "section": item.get("section") or NOT_PROVIDED,
                "authority": NOT_PROVIDED,
                "effective_date": item.get("as_of_date"),
                "source_url": NOT_PROVIDED,
                "text": item.get("content") or "",
            }
        )
    return normalized


def _fetch_evidence(retriever: LegalRetriever, query: str, jurisdiction: str = "India", top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Calls Member 4's real retriever and returns normalized evidence.
    Returns an empty list (never raises) if retrieval fails — callers must
    treat "no evidence" as a trigger for safe abstention (Roadmap Section 22).
    """
    try:
        raw_results = retriever.get_relevant_context(query, jurisdiction=jurisdiction, top_k=top_k)
    except Exception:
        return []
    return _normalize_evidence(raw_results)


class LegalReasoningPipeline:
    """
    Free-text legal Q&A helper (not part of the structured roadmap flow —
    see RoadmapOrchestrator below for that). Kept for ad-hoc legal analysis.
    """

    def __init__(self):
        self.retriever = LegalRetriever()

    def format_evidence_block(self, evidence_list: List[dict]) -> str:
        """Formats normalized evidence objects into a readable text block for LLM context."""
        if not evidence_list:
            return "No specific statutory evidence found."

        formatted_blocks = []
        for item in evidence_list:
            block = (
                f"[{item.get('id')}] Document: {item.get('document_name')}\n"
                f"Section/Provision: {item.get('section')}\n"
                f"Domain: {item.get('legal_domain')}\n"
                f"Text Excerpt: {item.get('text', '').strip()}\n"
            )
            formatted_blocks.append(block)

        return "\n---\n".join(formatted_blocks)

    def generate_prompt_payload(self, query: str, jurisdiction: str = "India", top_k: int = 3) -> Dict[str, Any]:
        """Retrieves evidence via RAG and constructs the complete LLM prompt payload."""
        evidence_list = _fetch_evidence(self.retriever, query, jurisdiction=jurisdiction, top_k=top_k)
        evidence_text = self.format_evidence_block(evidence_list)

        user_prompt = LEGAL_ANALYSIS_PROMPT_TEMPLATE.format(
            user_query=query,
            retrieved_evidence=evidence_text,
            matched_entities="None detected",  # Member 4's retriever doesn't expose this yet
        )

        return {
            "system_prompt": SYSTEM_PROMPT_LEGAL_EXPERT,
            "user_prompt": user_prompt,
            "rag_metadata": {
                "jurisdiction": jurisdiction,
                "evidence_count": len(evidence_list),
            },
            "raw_evidence": evidence_list,
        }


# ---------------------------------------------------------------------------
# Full Member 3 orchestration: classify -> route -> retrieve -> generate
# ---------------------------------------------------------------------------

def _format_evidence_for_generation(evidence_list: List[dict]) -> str:
    """Evidence block formatted specifically so the LLM can cite evidence id values."""
    if not evidence_list:
        return "No specific statutory evidence found."

    blocks = []
    for item in evidence_list:
        blocks.append(
            f"[{item.get('id')}] Document: {item.get('document_name')} | "
            f"Section: {item.get('section')} | Domain: {item.get('legal_domain')}\n"
            f"{item.get('text', '').strip()}"
        )
    return "\n---\n".join(blocks)


def _format_answers(clarification_answers: List[Dict[str, str]]) -> str:
    if not clarification_answers:
        return "No clarification answers provided."
    return "\n".join(f"- {a['id']}: {a['answer']}" for a in clarification_answers)


class RoadmapOrchestrator:
    """
    This is the Section 4 pipeline, owned end-to-end by Member 3:

        Classification -> Decision Router -> Hybrid Retrieval (M4) ->
        LLM Structured Generation -> (handed off to M5 for verification)
    """

    def __init__(self):
        self.retriever = LegalRetriever()

    def build_roadmap_draft(
        self,
        innovation_text: str,
        clarification_answers: List[Dict[str, str]] = None,
        jurisdiction: str = "India",
        top_k: int = 5,
    ) -> Dict[str, Any]:
        clarification_answers = clarification_answers or []

        # 1. Classification (Section 6)
        classification = classify_formulation(innovation_text, clarification_answers)

        # 2. Decision Router (Section 8)
        routing_result = route(classification, clarification_answers)

        # 3. Hybrid Retrieval (Member 4's real retriever, normalized)
        evidence_list = _fetch_evidence(self.retriever, innovation_text, jurisdiction=jurisdiction, top_k=top_k)

        # 4. Guardrail pre-check: is there any evidence to ground on?
        grounding = verify_grounding(innovation_text, evidence_list)

        # 5. LLM Structured Generation (Sections 18, 24, 33)
        user_prompt = ROADMAP_GENERATION_PROMPT_TEMPLATE.format(
            innovation_text=innovation_text,
            clarification_answers=_format_answers(clarification_answers),
            classification=classification,
            routing=routing_result,
            retrieved_evidence=_format_evidence_for_generation(evidence_list),
        )

        try:
            generated = call_llm_json(SYSTEM_PROMPT_ROADMAP_GENERATOR, user_prompt)
        except (ValueError, RuntimeError) as e:
            # Safe abstention at generation stage (Section 22) —
            # never silently fail, return an explicit abstain flag instead.
            return {
                "classification": classification,
                "routing": routing_result,
                "ip": {"analysis": "", "flags": [], "evidence_ids": []},
                "abs": {"applicable": False, "analysis": "", "evidence_ids": []},
                "regulatory": {"jurisdiction": jurisdiction, "pathway": "", "steps": [], "evidence_ids": []},
                "claims": [],
                "evidence": evidence_list,
                "grounding": grounding,
                "abstain": True,
                "abstain_reason": f"Generation failed: {e}",
                "disclaimer": (
                    "This output is AI-generated decision support, not legal advice. "
                    "Please consult a qualified patent attorney or regulatory expert."
                ),
            }

        # 6. Guardrail post-check: flag any absolute/guarantee language
        cautious_check = check_cautious_language(generated)

        return {
            "classification": classification,
            "routing": routing_result,
            "ip": generated.get("ip", {"analysis": "", "flags": [], "evidence_ids": []}),
            "abs": generated.get("abs", {"applicable": False, "analysis": "", "evidence_ids": []}),
            "regulatory": generated.get(
                "regulatory", {"jurisdiction": jurisdiction, "pathway": "", "steps": [], "evidence_ids": []}
            ),
            "claims": generated.get("claims", []),
            "evidence": evidence_list,
            "grounding": grounding,
            "cautious_language_check": cautious_check,
            "abstain": not grounding["grounded"],
            "abstain_reason": None if grounding["grounded"] else grounding["note"],
            "disclaimer": (
                "This output is AI-generated decision support, not legal advice. "
                "Please consult a qualified patent attorney or regulatory expert "
                "before taking formal action."
            ),
        }


if __name__ == "__main__":
    # Demo 1: free-text legal analysis prompt
    pipeline = LegalReasoningPipeline()
    sample_query = "The formulation uses Ashwagandha root extract as a biological resource."
    payload = pipeline.generate_prompt_payload(sample_query, top_k=2)

    print("================ SYSTEM PROMPT ================")
    print(payload["system_prompt"])
    print("\n================ CONSTRUCTED USER PROMPT ================")
    print(payload["user_prompt"])

    # Demo 2: full structured roadmap pipeline
    print("\n\n================ FULL STRUCTURED ROADMAP ================")
    orchestrator = RoadmapOrchestrator()
    sample_answers = [
        {"id": "q1", "answer": "Medicine / therapeutic use"},
        {"id": "q2", "answer": "Based on a classical formulation but modified"},
        {"id": "q3", "answer": "Yes, a new process/technique"},
        {"id": "q4", "answer": "Yes"},
        {"id": "q5", "answer": "India"},
    ]
    draft = orchestrator.build_roadmap_draft(
        "A modified Ashwagandha formulation using a new extraction technique for stress relief.",
        sample_answers,
    )
    import json
    print(json.dumps(draft, indent=2))
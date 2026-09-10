"""
INTEGRATION INTERFACE for Member 2 (Backend/FastAPI).

Member 2 should ONLY import from this file, not from classification.py,
routing.py, clarification.py, or generator.py directly. This keeps the
internal implementation free to change without breaking the API layer.

Maps directly to the three backend endpoints (Roadmap.md Section 26):
    POST /clarify   -> get_clarification_questions()
    POST /analyze   -> build_roadmap()          (does classify + route + generate)
    GET  /report     -> (M2 just returns the stored result of /analyze)
"""

from typing import Dict, Any, List

from llm_pipeline.clarification import get_clarification_questions as _get_questions
from llm_pipeline.generator import RoadmapOrchestrator

_orchestrator = RoadmapOrchestrator()


# ---------------------------------------------------------------------------
# Endpoint: POST /clarify
# ---------------------------------------------------------------------------

def get_clarification_questions(innovation_text: str) -> List[Dict[str, Any]]:
    """
    Called when the user first submits their innovation description.

    Input  (from request body):
        innovation_text: str

    Returns (send straight back as JSON array to frontend):
        [
          {"id": "q1", "question": "...", "purpose": "...",
           "input_type": "single_select", "options": [...]},
          ...
        ]
    """
    return _get_questions(innovation_text)


# ---------------------------------------------------------------------------
# Endpoint: POST /analyze
# ---------------------------------------------------------------------------

def build_roadmap(
    innovation_text: str,
    clarification_answers: List[Dict[str, str]],
) -> Dict[str, Any]:
    """
    Called after the user answers the clarification questions.
    Runs the full Member 3 pipeline: classify -> route -> retrieve (M4) -> generate.

    Input (from request body):
        innovation_text: str
        clarification_answers: [{"id": "q1", "answer": "..."}, ...]

    Returns (M2 should store this + forward to Member 5 for verification
    before sending the final response to the frontend):
        {
          "classification": {"category": str, "reason": str, "confidence": int},
          "routing": {"category": str, "ip_required": bool, "abs_check": bool,
                      "regulatory_path": str, "jurisdiction": "india",
                      "routing_reason": str},
          "ip": {"analysis": str, "flags": [...], "evidence_ids": [...]},
          "abs": {"applicable": bool, "analysis": str, "evidence_ids": [...]},
          "regulatory": {"jurisdiction": "India", "pathway": str,
                          "steps": [...], "evidence_ids": [...]},
          "claims": [{"id": "claim_1", "text": "..."}, ...],
          "grounding": {"grounded": bool, "retrieved_sections": [...], "note": str},
          "abstain": bool,
          "abstain_reason": str | None,
          "disclaimer": str
        }

    IMPORTANT for M2: check "abstain" first. If True, show the abstain_reason
    to the user instead of the (likely empty/partial) ip/abs/regulatory sections.

    IMPORTANT for M2->M5 handoff: pass "claims" + the raw evidence list
    (available via _orchestrator.retriever if needed) into Member 5's
    verifier before this goes to the frontend as final.
    """
    return _orchestrator.build_roadmap_draft(innovation_text, clarification_answers)
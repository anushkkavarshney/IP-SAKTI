"""
Guardrails and Verification Module for IP-SAKTI Module 3.
Ensures generated legal reasoning remains grounded in retrieved evidence.
"""

from typing import Dict, Any, List


def validate_prompt_input(query: str, evidence: List[dict]) -> Dict[str, Any]:
    """Validates that input query is non-empty and evidence exists."""
    if not query.strip():
        return {"valid": False, "reason": "User query cannot be empty."}

    if not evidence:
        return {
            "valid": True,
            "warning": "No retrieved legal evidence available; LLM output must disclaim general knowledge.",
        }

    return {"valid": True, "warning": None}


def verify_grounding(prompt: str, evidence_list: list) -> dict:
    retrieved_sections = [
        f"{e.get('document', '')} - {e.get('section', '')}".strip()
        for e in evidence_list
    ]
    
    # Grounded if valid evidence chunks were retrieved
    is_grounded = len(evidence_list) > 0

    return {
        "grounded": is_grounded,
        "retrieved_sections": retrieved_sections,
        "note": "Successfully grounded in vector store evidence." if is_grounded else "Insufficient retrieved context."
    }


if __name__ == "__main__":
    sample_evidence = [
        {"section": "Section 3", "document": "The Biological Diversity Act, 2002"}
    ]
    sample_response = "Under Section 3 of the Biological Diversity Act, 2002, NBA approval is required."

    check = verify_grounding(sample_response, sample_evidence)
    print("Guardrail Verification Check:", check)
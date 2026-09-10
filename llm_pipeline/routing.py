"""
Decision Router for IP-SAKTI Module 3.
Roadmap.md Section 8.

MVP DECISION: routing is RULE-BASED, not LLM-based.
Why: routing flags feed directly into which legal corpus filters get used
downstream (Member 4) — this must be deterministic and auditable, not
subject to LLM variance. Classification already used the LLM; routing just
maps that decided category (+ a couple of clarification answers) to fixed
boolean/enum flags per Section 8's example rules.
"""

from typing import Dict, Any, List


CATEGORY_TO_PATHWAY = {
    "classical_ayurvedic_medicine": "ayush",
    "proprietary_ayurvedic_medicine": "ayush",
    "phytopharmaceutical": "drug_phytopharma",
    "nutraceutical": "fssai",
    "cosmetic": "cosmetic",
    "unknown_insufficient_information": "unclear",
}


def _answer_for(clarification_answers: List[Dict[str, str]], qid: str) -> str:
    for a in clarification_answers:
        if a.get("id") == qid:
            return a.get("answer", "")
    return ""


def route(
    classification: Dict[str, Any],
    clarification_answers: List[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Takes the classification result + clarification answers and returns
    routing flags per the Section 8 example output shape:

    {
      "category": "...",
      "ip_required": bool,
      "abs_check": bool,
      "regulatory_path": "...",
      "jurisdiction": "india",
      "routing_reason": "..."
    }
    """
    clarification_answers = clarification_answers or []
    category = classification.get("category", "unknown_insufficient_information")

    # --- ABS check: biological resource involved? (q4) ---
    bio_resource_answer = _answer_for(clarification_answers, "q4").strip().lower()
    abs_check = bio_resource_answer == "yes"

    # --- IP check: novel process/formulation involved? (q3, or proprietary category) ---
    novel_process_answer = _answer_for(clarification_answers, "q3").strip().lower()
    ip_required = (
        novel_process_answer.startswith("yes")
        or category == "proprietary_ayurvedic_medicine"
        or category == "phytopharmaceutical"
    )

    # --- Regulatory pathway: driven by classification category ---
    regulatory_path = CATEGORY_TO_PATHWAY.get(category, "unclear")

    reasons = []
    reasons.append(f"Category '{category}' maps to regulatory pathway '{regulatory_path}'.")
    reasons.append(
        "Biological resource use indicated -> ABS check enabled."
        if abs_check
        else "No biological resource use indicated -> ABS check not triggered."
    )
    reasons.append(
        "Novel process/formulation indicated -> IP path enabled."
        if ip_required
        else "No novel process/formulation clearly indicated -> IP path not triggered."
    )

    return {
        "category": category,
        "ip_required": ip_required,
        "abs_check": abs_check,
        "regulatory_path": regulatory_path,
        "jurisdiction": "india",
        "routing_reason": " ".join(reasons),
    }


if __name__ == "__main__":
    sample_classification = {
        "category": "proprietary_ayurvedic_medicine",
        "reason": "Modified classical formulation with a new extraction process.",
        "confidence": 82,
    }
    sample_answers = [
        {"id": "q3", "answer": "Yes, a new process/technique"},
        {"id": "q4", "answer": "Yes"},
    ]
    print(route(sample_classification, sample_answers))
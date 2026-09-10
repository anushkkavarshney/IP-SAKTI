"""
Formulation Classification module for IP-SAKTI Module 3.
Roadmap.md Section 6.
"""

from typing import Dict, Any, List

from llm_pipeline.llm_client import call_llm_json
from llm_pipeline.prompts import (
    SYSTEM_PROMPT_CLASSIFIER,
    CLASSIFICATION_PROMPT_TEMPLATE,
)

VALID_CATEGORIES = {
    "classical_ayurvedic_medicine",
    "proprietary_ayurvedic_medicine",
    "phytopharmaceutical",
    "nutraceutical",
    "cosmetic",
    "unknown_insufficient_information",
}


def _format_answers(clarification_answers: List[Dict[str, str]]) -> str:
    if not clarification_answers:
        return "No clarification answers provided yet."
    return "\n".join(f"- {a['id']}: {a['answer']}" for a in clarification_answers)


def classify_formulation(
    innovation_text: str,
    clarification_answers: List[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Classifies the innovation into one of 6 categories.
    Returns: {"category": str, "reason": str, "confidence": int}

    On any failure (bad JSON, invalid category, API error), falls back to a
    safe "unknown_insufficient_information" result with confidence 0 rather
    than crashing the pipeline — this IS the safe-abstention behavior applied
    at the classification stage (Section 22 principle).
    """
    clarification_answers = clarification_answers or []

    user_prompt = CLASSIFICATION_PROMPT_TEMPLATE.format(
        innovation_text=innovation_text,
        clarification_answers=_format_answers(clarification_answers),
    )

    try:
        result = call_llm_json(SYSTEM_PROMPT_CLASSIFIER, user_prompt)
    except (ValueError, RuntimeError) as e:
        return {
            "category": "unknown_insufficient_information",
            "reason": f"Classification failed due to a system error: {e}",
            "confidence": 0,
        }

    category = result.get("category", "unknown_insufficient_information")
    if category not in VALID_CATEGORIES:
        # LLM hallucinated a category outside our fixed set — don't trust it.
        return {
            "category": "unknown_insufficient_information",
            "reason": (
                f"Model returned an unrecognized category ('{category}'); "
                "defaulting to unknown pending human review."
            ),
            "confidence": 0,
        }

    confidence = result.get("confidence", 0)
    try:
        confidence = max(0, min(100, int(confidence)))
    except (TypeError, ValueError):
        confidence = 0

    return {
        "category": category,
        "reason": result.get("reason", ""),
        "confidence": confidence,
    }


if __name__ == "__main__":
    sample_text = "A modified Ashwagandha formulation using a new extraction technique for stress relief."
    sample_answers = [
        {"id": "q1", "answer": "Medicine / therapeutic use"},
        {"id": "q2", "answer": "Based on a classical formulation but modified"},
        {"id": "q3", "answer": "Yes, a new process/technique"},
        {"id": "q4", "answer": "Yes"},
        {"id": "q5", "answer": "India"},
    ]
    print(classify_formulation(sample_text, sample_answers))
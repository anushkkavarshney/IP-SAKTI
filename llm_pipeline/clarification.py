"""
Clarification Engine for IP-SAKTI Module 3.
Roadmap.md Section 7.

MVP DECISION: questions are FIXED (not LLM-generated).
Why: deterministic, fast, no extra API call, and reliable for the demo.
If time remains (Section 40), this can be upgraded to dynamically pick a
subset of questions based on the innovation_text using the LLM.
"""

from typing import Dict, Any, List


CLARIFICATION_QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": "q1",
        "question": "What is the intended use of the product? (e.g., medicine, dietary supplement, cosmetic)",
        "purpose": "Determines whether this leans medicinal, nutraceutical, or cosmetic.",
        "input_type": "single_select",
        "options": ["Medicine / therapeutic use", "Dietary supplement / food", "Cosmetic", "Not sure"],
    },
    {
        "id": "q2",
        "question": "Is this based on an existing/classical Ayurvedic formulation, or something new?",
        "purpose": "Distinguishes classical Ayurvedic medicine from proprietary/novel formulations.",
        "input_type": "single_select",
        "options": [
            "Based on a classical formulation (as-is)",
            "Based on a classical formulation but modified",
            "Entirely new formulation",
            "Not sure",
        ],
    },
    {
        "id": "q3",
        "question": "Is there a new extraction technique, process, or delivery method involved?",
        "purpose": "Signals possible novelty/patentability (IP path trigger).",
        "input_type": "single_select",
        "options": ["Yes, a new process/technique", "No, standard/traditional method", "Not sure"],
    },
    {
        "id": "q4",
        "question": "Does the innovation use a biological resource sourced from India (plant, herb, microorganism, etc.)?",
        "purpose": "Triggers ABS / Biological Diversity Act consideration.",
        "input_type": "single_select",
        "options": ["Yes", "No", "Not sure"],
    },
    {
        "id": "q5",
        "question": "Which country/market is this primarily intended for right now?",
        "purpose": "Confirms jurisdiction. MVP only supports India (Section 13).",
        "input_type": "text",
        "options": None,
    },
]


def get_clarification_questions(innovation_text: str = "") -> List[Dict[str, Any]]:
    """
    Returns the fixed clarification question set.
    innovation_text is accepted (per the shared API contract) but unused in the
    MVP fixed-question approach — kept so this can be upgraded later without
    breaking M2's call signature.
    """
    return CLARIFICATION_QUESTIONS
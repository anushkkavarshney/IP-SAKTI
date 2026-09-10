"""
*** TEMPORARY PLACEHOLDER -- OWNED BY MEMBER 2, MEANT TO BE REPLACED ***

Roadmap.md assigns "Clarification logic" and "Product classification" to
MEMBER 3 (Section 27), but no such module exists in the repo yet. Without
*something* here, /clarify and /analyze have nothing to call and the
frontend can never get a live (non-mock) response.

This file is a simple, honest, rule-based stand-in:
- get_clarification_questions() returns the same 4 questions the frontend
  already ships as its own fallback mock data (frontend/src/lib/mockData.ts
  CLARIFICATION_QUESTIONS) -- so behaviour doesn't change when the real
  backend comes online instead of the frontend's offline fallback.
- classify() is keyword matching, not an LLM. It picks one of the 6
  categories fixed by Roadmap.md Section 6 and says plainly that this is a
  preliminary/rule-based classification.

WHEN MEMBER 3 IS READY: replace the body of classify() (and, if needed,
get_clarification_questions()) with real logic. Nothing else in the
backend needs to change -- app/services/pipeline.py only calls the two
functions below.
"""

from typing import Dict, List, Tuple

CATEGORIES = [
    "Classical Ayurvedic Medicine",
    "Proprietary Ayurvedic Medicine",
    "Phytopharmaceutical",
    "Nutraceutical",
    "Cosmetic",
    "Unknown / Insufficient Information",
]


def get_clarification_questions() -> List[Dict]:
    """Same 4-question shape as frontend/src/lib/mockData.ts CLARIFICATION_QUESTIONS."""
    return [
        {
            "id": "intended_use",
            "field_key": "intended_use",
            "question": "1. What is the primary intended use and form of your product?",
            "description": (
                "Helps differentiate between medicinal (therapeutic), health "
                "supplement (food), or external cosmetic classification under "
                "Indian regulations."
            ),
            "options": [
                {
                    "value": "therapeutic_internal",
                    "label": "Therapeutic / Medicinal Treatment (Internal Consumption)",
                    "hint": "Intended to diagnose, treat, or alleviate disease/stress symptoms",
                },
                {
                    "value": "supplement_food",
                    "label": "General Health & Dietary Supplement / Wellness",
                    "hint": "Daily nutrition/wellness enhancement (FSSAI domain)",
                },
                {
                    "value": "cosmetic_external",
                    "label": "External Application / Cosmetic & Personal Care",
                    "hint": "Skincare, hair oil, cleansing without medical cure claims",
                },
            ],
        },
        {
            "id": "classical_heritage",
            "field_key": "classical_heritage",
            "question": "2. Is this product based on an authoritative classical Ayurvedic text?",
            "description": (
                "Classical Ayurvedic drugs strictly follow formulas from texts "
                "listed in the First Schedule of the Drugs & Cosmetics Act, 1940."
            ),
            "options": [
                {"value": "yes_classical", "label": "Yes, follows a classical formula exactly"},
                {"value": "modified_classical", "label": "Based on a classical formula but modified"},
                {"value": "no_new", "label": "No, this is a new formulation"},
            ],
        },
        {
            "id": "novel_process",
            "field_key": "novel_process",
            "question": "3. Does the innovation involve a new extraction, processing, or manufacturing technique?",
            "description": "Novel processes are a key patentability signal for the IP module.",
            "options": [
                {"value": "yes_novel_process", "label": "Yes, a new process/technique is involved"},
                {"value": "no_standard_process", "label": "No, standard/known methods are used"},
            ],
        },
        {
            "id": "biological_resource",
            "field_key": "biological_resource",
            "question": "4. Does the formulation use plants, animals, microorganisms, or other biological resources?",
            "description": "Determines whether ABS (Access and Benefit Sharing) considerations may apply.",
            "options": [
                {"value": "yes_biological", "label": "Yes, biological resources are used"},
                {"value": "no_biological", "label": "No biological resources involved"},
                {"value": "unsure_biological", "label": "Not sure"},
            ],
        },
    ]


def classify(description: str, clarifications: Dict[str, str]) -> Tuple[str, str, float]:
    """
    Returns (category, reason, confidence). Keyword/rule based -- NOT an
    LLM, and confidence is capped below what a real classifier should
    claim, to avoid overstating certainty (Roadmap.md Section 42).
    """
    text = f"{description} {' '.join(clarifications.values())}".lower()

    intended_use = clarifications.get("intended_use", "")
    classical = clarifications.get("classical_heritage", "")

    if classical == "yes_classical":
        return (
            "Classical Ayurvedic Medicine",
            "Marked by the user as following a classical formula exactly.",
            0.6,
        )

    if intended_use == "cosmetic_external":
        return (
            "Cosmetic",
            "User indicated external/cosmetic application as the intended use.",
            0.55,
        )

    if intended_use == "supplement_food":
        if "extract" in text or classical == "modified_classical":
            return (
                "Nutraceutical",
                "User indicated a food/supplement use with a modified or extracted formulation.",
                0.5,
            )
        return (
            "Nutraceutical",
            "User indicated general health/supplement/food use.",
            0.55,
        )

    if intended_use == "therapeutic_internal":
        if classical == "modified_classical" or "extract" in text or "process" in text:
            return (
                "Phytopharmaceutical",
                "Therapeutic internal use with a modified formulation or novel extraction process.",
                0.5,
            )
        if classical == "no_new":
            return (
                "Proprietary Ayurvedic Medicine",
                "Therapeutic internal use with a new (non-classical) Ayurvedic formulation.",
                0.5,
            )

    return (
        "Unknown / Insufficient Information",
        "Not enough information was provided to confidently assign a category.",
        0.2,
    )

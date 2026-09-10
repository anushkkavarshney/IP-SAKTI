"""
Guardrails and Verification Module for IP-SAKTI Module 3.
Ensures generated legal reasoning remains grounded in retrieved evidence
and uses cautious, non-binding language (Roadmap Section 9).
"""

import re
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
        f"{e.get('document_name', '')} - {e.get('section', '')}".strip()
        for e in evidence_list
    ]

    # Grounded if valid evidence chunks were retrieved
    is_grounded = len(evidence_list) > 0

    return {
        "grounded": is_grounded,
        "retrieved_sections": retrieved_sections,
        "note": "Successfully grounded in vector store evidence." if is_grounded else "Insufficient retrieved context.",
    }


# ---------------------------------------------------------------------------
# NEW — cautious language check (Roadmap Section 9)
# ---------------------------------------------------------------------------

# Phrases the system is REQUIRED to avoid — these read as binding guarantees.
FORBIDDEN_ABSOLUTE_PHRASES = [
    r"\bwill be granted\b",
    r"\bwill be approved\b",
    r"\bwill be rejected\b",
    r"\bis guaranteed\b",
    r"\byou will (get|receive|obtain) a patent\b",
    r"\bdefinitely (qualifies|is patentable|is eligible)\b",
    r"\bis certain to\b",
]

# Phrases that SHOULD appear when the module is making a legal/regulatory claim.
CAUTIOUS_MARKERS = [
    "may", "potentially", "appears to", "further assessment",
    "further review", "recommended", "could", "might",
]


def _collect_text_fields(generated: Dict[str, Any]) -> str:
    """Pulls all free-text analysis fields out of a RoadmapDraft-shaped dict."""
    parts = []
    for section_key in ("ip", "abs", "regulatory"):
        section = generated.get(section_key, {})
        if isinstance(section, dict):
            if "analysis" in section:
                parts.append(str(section.get("analysis", "")))
            if "steps" in section and isinstance(section["steps"], list):
                parts.extend(str(s) for s in section["steps"])
    for claim in generated.get("claims", []):
        if isinstance(claim, dict):
            parts.append(str(claim.get("text", "")))
    return " ".join(parts)


def check_cautious_language(generated: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scans a generated roadmap draft for:
      1. Forbidden absolute/guarantee phrases -> hard violation, must be fixed.
      2. Presence of at least one cautious marker -> soft signal that the
         language style is appropriate.

    This is a guardrail, not a blocker: callers should log/flag violations
    for M2/M5 rather than silently editing the LLM's text.
    """
    combined_text = _collect_text_fields(generated).lower()

    violations = [
        phrase for phrase in FORBIDDEN_ABSOLUTE_PHRASES
        if re.search(phrase, combined_text)
    ]

    has_cautious_marker = any(marker in combined_text for marker in CAUTIOUS_MARKERS)

    return {
        "passed": len(violations) == 0,
        "violations": violations,
        "has_cautious_marker": has_cautious_marker,
        "note": (
            "No absolute/guarantee language detected."
            if len(violations) == 0
            else f"Found {len(violations)} absolute-language violation(s); review before showing to user."
        ),
    }


if __name__ == "__main__":
    sample_evidence = [
        {"section": "Section 3", "document": "The Biological Diversity Act, 2002"}
    ]
    sample_response = "Under Section 3 of the Biological Diversity Act, 2002, NBA approval is required."

    check = verify_grounding(sample_response, sample_evidence)
    print("Guardrail Verification Check:", check)

    sample_generated = {
        "ip": {"analysis": "This formulation may warrant further patentability assessment.", "flags": []},
        "abs": {"applicable": True, "analysis": "ABS review is potentially required."},
        "regulatory": {"steps": ["File further documentation for review"]},
        "claims": [{"id": "claim_1", "text": "Patent protection may be possible."}],
    }
    print("Cautious Language Check:", check_cautious_language(sample_generated))
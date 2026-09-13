"""
Adapter for Member 5's verification module.

This one needs almost no adaptation -- Member 5 documented the exact
call pattern in verification/HANDOFF.md, so we just follow it.

Update (2026-09-12): as of Member 5's confidence.py rewrite, verify_claims()
now returns "confidence", "abstain", and "abstain_reason" as part of its own
payload (computed with real authority-list scoring), superseding backend's
old homebrew confidence calculation. The exception fallback below now
matches that fuller shape so pipeline.py can read confidence/abstain
uniformly whether verify_claims() succeeded or not.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List


import logging

logger = logging.getLogger("ip_sakti_backend")

# parents[0]=services, [1]=app, [2]=backend, [3]=repo root

_REPO_ROOT = str(Path(__file__).resolve().parents[3])
_VERIFICATION_DIR = os.path.join(_REPO_ROOT, "verification")

# verification/__init__.py does `from verifier import ...` / `from schemas
# import ...` (bare imports, same pattern as rag_engine/retriever.py) --
# these only resolve if verification/'s own directory is on sys.path.
if _VERIFICATION_DIR not in sys.path:
    sys.path.append(_VERIFICATION_DIR)
if _REPO_ROOT not in sys.path:
    sys.path.append(_REPO_ROOT)

from verification import verify_claims  # type: ignore  # noqa: E402


def verify(
    claims: List[Dict[str, Any]],
    evidence: List[Dict[str, Any]],
    jurisdiction: str = "India",
    top_k: int = 3,
    classification: Any = None,
    input_completeness: float | None = None,
    required_domains: List[str] | None = None,
) -> Dict[str, Any]:
    """
    claims: list of {"id": "...", "text": "..."}
    evidence: list of the normalized evidence dicts from rag_adapter.fetch_evidence
              (this backend adds "source" as an alias of "source_url" so
              verification/schemas.py's normalizer picks it up either way)

    Optional evidence-sufficiency context forwarded to Member 5's confidence
    / safe-abstention engine:
      classification     — the M3 classification result (category confidence
                           feeds the "unknown product" abstain gate).
      input_completeness — fraction (0..1) of informative clarification answers.
      required_domains   — legal domains expected for this product type; an
                           empty list means the product type is unknown.

    Returns Member 5's full payload:
        {"verification": [...], "summary": {...}, "confidence": {...},
         "abstain": bool, "abstain_reason": str, "abstain_reasons": [...]}
    """
    evidence_payload = {
        "jurisdiction": jurisdiction,
        "evidence": [
            {**item, "source": item.get("source_url"), "document": item.get("document_name")}
            for item in evidence
        ],
    }
    claims_payload = {"jurisdiction": jurisdiction, "claims": claims}

    try:
        return verify_claims(
            claims=claims_payload,
            evidence=evidence_payload,
            top_k=top_k,
            target_jurisdiction=jurisdiction,
            classification=classification,
            input_completeness=input_completeness,
            required_domains=required_domains,
        )
    except Exception:
         # Debugging fix (2026-09-13): this used to swallow the real error
        # completely -- confidence would silently come back as 0 with no
        # trace of why. Now the actual exception is logged server-side so
        # "why is confidence always 0" has an answer instead of a guess.
        logger.exception("verify_claims() failed -- falling back to abstain-only payload")
        
        return {
            "verification": [],
            "summary": {
                "total_claims": len(claims),
                "supported_claims": 0,
                "partially_supported_claims": 0,
                "unsupported_claims": [{"claim": c.get("text", "")} for c in claims],
            },
            "confidence": {
                "score": 0.0,
                "level": "LOW",
                "signals": {
                    "retrieval_quality": 0.0,
                    "source_authority": 0.0,
                    "claim_support": 0.0,
                    "jurisdiction_match": 0.0,
                },
                "note": None,
            },
            "abstain": True,
            "abstain_reason": (
                "The verification service is currently unavailable, so no confident "
                "analysis could be produced."
            ),
        }
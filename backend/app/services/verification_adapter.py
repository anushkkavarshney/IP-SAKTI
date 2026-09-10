"""
Adapter for Member 5's verification module.

This one needs almost no adaptation -- Member 5 documented the exact
call pattern in verification/HANDOFF.md, so we just follow it.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List

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
) -> Dict[str, Any]:
    """
    claims: list of {"id": "...", "text": "..."}
    evidence: list of the normalized evidence dicts from rag_adapter.fetch_evidence
              (this backend adds "source" as an alias of "source_url" so
              verification/schemas.py's normalizer picks it up either way)

    Returns Member 5's payload:
        {"support_type", "note", "verification": [...], "summary": {...}}
    """
    evidence_payload = {
        "jurisdiction": jurisdiction,
        "evidence": [
            {**item, "source": item.get("source_url"), "document": item.get("document_name")}
            for item in evidence
        ],
    }
    claims_payload = {"jurisdiction": jurisdiction, "claims": claims}

    # return verify_claims(
    #     claims=claims_payload,
    #     evidence=evidence_payload,
    #     top_k=top_k,
    #     target_jurisdiction=jurisdiction,
    # )

    try:
        return verify_claims(
            claims=claims_payload,
            evidence=evidence_payload,
            top_k=top_k,
            target_jurisdiction=jurisdiction,
        )
    except Exception:
        return {
            "verification": [],
            "summary": {
                "total_claims": len(claims),
                "supported_claims": 0,
                "partially_supported_claims": 0,
                "unsupported_claims": [{"claim": c.get("text", "")} for c in claims],
            },
        }

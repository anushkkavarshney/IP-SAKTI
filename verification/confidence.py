"""
IP-SAKTI Navigator — Member 5 — Confidence + Safe Abstention Engine.

Ownership (Roadmap §19-23, §29, §44-48):
  - T7:  Confidence engine.
  - T8:  Safe abstention.
  - T9:  Unsupported claims are flagged, never presented as fact.
  - T10: NO fake contradiction detection.  This module intentionally does
         NOT attempt NLI/contradiction detection.  A claim that looks
         unsupported is reported as "insufficient evidence / unsupported",
         never as "evidence contradicts the claim".  Contradiction
         detection is out of scope for M5 and documented as a limitation.

Scale note: the canonical M5 confidence score is on a **0 - 100** scale.
Signals are also 0 - 100, so each contribution is  signal * weight
(e.g. retrieval_quality 90 * 0.30 = 27).  Thresholds:
  HIGH   = 80 - 100
  MEDIUM = 50 - 79
  LOW    = < 50
The old M2 0-1 scale with 0.7/0.4 thresholds is superseded here.

This module deliberately does not import the embedding model — it only
consumes the per-claim verification results produced by verifier.py.
"""

from __future__ import annotations

from typing import Any

from .schemas import (
    CONFIDENCE_HIGH,
    CONFIDENCE_LOW,
    CONFIDENCE_MEDIUM,
    DEFAULT_JURISDICTION,
    STATUS_PARTIAL,
    STATUS_SUPPORTED,
    _is_known_authority,
)

# Confidence weights (sum to 1.0) — Roadmap §19-23.
CONFIDENCE_WEIGHTS: dict[str, float] = {
    "retrieval_quality": 0.30,
    "source_authority": 0.25,
    "claim_support": 0.25,
    "jurisdiction_match": 0.20,
}

LEVEL_HIGH_MIN = 80.0
LEVEL_MEDIUM_MIN = 50.0

# A score below this is too weak to present as analysis → abstain.
ABSTAIN_SCORE_MIN = 30.0

# Baseline evidence count used to normalise retrieval quality.
RETRIEVAL_TARGET = 6.0

ABSTAIN_REASON_NO_EVIDENCE = (
    "Insufficient authoritative legal evidence was retrieved to support a "
    "confident roadmap. This is a preliminary, AI-generated analysis — "
    "please consult a qualified professional."
)
ABSTAIN_REASON_LOW_CONFIDENCE = (
    "Overall confidence is below the safe-decision threshold. The analysis "
    "is being withheld pending further review."
)
ABSTAIN_REASON_NO_CLAIMS = (
    "No claims were provided, so no verification analysis could be produced."
)


def _best_authority_score(claim_result: dict[str, Any]) -> float:
    """100 when the best evidence's authority is on the known-authority
    list, 40 when an authority is present but unrecognised, 0 when the
    evidence has no authority at all."""
    best = claim_result.get("best_evidence") or {}
    authority = (best.get("authority") or "").strip()
    if not authority:
        return 0.0
    return 100.0 if _is_known_authority(authority) else 40.0


def confidence_level(score: float) -> str:
    """Map a 0-100 confidence score to HIGH / MEDIUM / LOW."""
    if score >= LEVEL_HIGH_MIN:
        return CONFIDENCE_HIGH
    if score >= LEVEL_MEDIUM_MIN:
        return CONFIDENCE_MEDIUM
    return CONFIDENCE_LOW


def calculate_confidence(
    verification_results: list[dict[str, Any]],
    *,
    evidence: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Compute the M5 confidence bundle on a 0-100 scale.

    Four signals (Roadmap §19-23):
      retrieval_quality (30%): how much evidence was provided (≤ 6 items → 100).
      source_authority   (25%): how authoritative the best evidence is.
      claim_support      (25%): share of claims supported / partially supported.
      jurisdiction_match (20%): share of claims whose best evidence matches
                                the claim's jurisdiction.

    Returns {"score", "level", "signals", "note"}.
    """
    total = len(verification_results) or 1

    supported_or_partial = sum(
        1
        for result in verification_results
        if result.get("status") in (STATUS_SUPPORTED, STATUS_PARTIAL)
    )
    jurisdiction_ok = sum(
        1 for result in verification_results if result.get("jurisdiction_match")
    )

    evidence_count = len(evidence) if evidence is not None else 0
    retrieval_quality = min(evidence_count / RETRIEVAL_TARGET, 1.0) * 100.0

    if verification_results:
        source_authority = sum(
            _best_authority_score(result) for result in verification_results
        ) / len(verification_results)
    else:
        source_authority = 0.0

    claim_support = (supported_or_partial / total) * 100.0
    jurisdiction_match = (jurisdiction_ok / total) * 100.0

    signals: dict[str, float] = {
        "retrieval_quality": round(retrieval_quality, 1),
        "source_authority": round(source_authority, 1),
        "claim_support": round(claim_support, 1),
        "jurisdiction_match": round(jurisdiction_match, 1),
    }

    score = sum(signals[key] * CONFIDENCE_WEIGHTS[key] for key in CONFIDENCE_WEIGHTS)
    score = round(score, 1)

    note = None
    if signals["source_authority"] == 0.0 and confidence_level(score) == CONFIDENCE_HIGH:
        note = (
            "High similarity alone does not confirm legal authority, which is "
            "derived from recognized Indian sources."
        )

    return {
        "score": score,
        "level": confidence_level(score),
        "signals": signals,
        "note": note,
    }


def _has_flagged_citation(verification_results: list[dict[str, Any]]) -> bool:
    """True if any claim's best evidence carries UNKNOWN_CITATION."""
    for result in verification_results:
        if "UNKNOWN_CITATION" in (result.get("flags") or []):
            return True
    return False


def calculate_abstention(
    verification_results: list[dict[str, Any]],
    *,
    evidence: list[dict[str, Any]] | None = None,
    confidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Safe abstention decision (Roadmap §44-48).

    Abstain when:
      - no evidence was provided, OR
      - no claims were provided, OR
      - confidence score is below ABSTAIN_SCORE_MIN (default 30).

    A UNKNOWN_CITATION on the best evidence raises a strong warning but is
    not a hard abstention by itself — the low source_authority it produces
    typically pushes the score low anyway.

    Returns {"abstain", "abstain_reason", "reasons"}.
    """
    confidence = confidence or calculate_confidence(verification_results, evidence=evidence)

    reasons: list[str] = []

    if evidence is not None and len(evidence) == 0:
        reasons.append("no_evidence")
    if not verification_results:
        reasons.append("no_claims")
    if confidence.get("score", 0.0) < ABSTAIN_SCORE_MIN:
        reasons.append("low_confidence")
    if _has_flagged_citation(verification_results):
        reasons.append("unknown_citation")

    if reasons:
        reason = None
        if "no_evidence" in reasons:
            reason = ABSTAIN_REASON_NO_EVIDENCE
        elif "no_claims" in reasons:
            reason = ABSTAIN_REASON_NO_CLAIMS
        elif "unknown_citation" in reasons:
            reason = (
                "Some supporting evidence cites an authority not currently "
                "recognized by the platform. Confidence was adjusted downward "
                "and the analysis is being withheld pending verification."
            )
        else:
            reason = ABSTAIN_REASON_LOW_CONFIDENCE

        return {"abstain": True, "abstain_reason": reason, "reasons": reasons}

    return {"abstain": False, "abstain_reason": None, "reasons": []}


def validate_no_contradiction_detection() -> str:
    """
    Explicit documentation of the T10 contract: M5 performs semantic
    relevance ranking only, never automatic contradiction detection.
    """
    return (
        "M5 reports semantic support only. Statements such as 'the evidence "
        "contradicts the claim' are intentionally NOT produced: the engine "
        "does not yet perform NLI-based contradiction detection. Unsupported "
        "claims are reported as lacking supporting evidence, never as "
        "contradicted."
    )
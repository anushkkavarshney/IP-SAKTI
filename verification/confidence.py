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

import logging
import re
from typing import Any

from .schemas import (
    CONFIDENCE_HIGH,
    CONFIDENCE_LOW,
    CONFIDENCE_MEDIUM,
    DEFAULT_JURISDICTION,
    FLAG_UNKNOWN_CITATION,
    FLAG_UNKNOWN_CITATION_REFERENCE,
    STATUS_PARTIAL,
    STATUS_SUPPORTED,
    STATUS_UNSUPPORTED,
    _is_known_authority,
)

logger = logging.getLogger("ip_sakti_verification")

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
# LOW confidence starts below 50, so abstaining at the bottom of MEDIUM
# means "score is not even convincingly MEDIUM yet". Safe abstention must
# only show a roadmap when the evidence genuinely supports it.
ABSTAIN_SCORE_MIN = 50.0

# Similarity at or above this reference is treated as "fully relevant"
# evidence for a claim (mirrors verifier.SUPPORTED_MIN = 0.70).
RELEVANCE_REFERENCE_SCORE = 0.70

# A score above this cap is not acceptable when the product type could not
# be classified at all (unknown_insufficient_information): an analysis that
# cannot say WHAT the product is must never present itself as high-confidence.
UNKNOWN_CLASSIFICATION_SCORE_CAP = 25.0

# Minimum share of clarification answers that must be informative
# (non-"Not sure", non-empty) before the system takes the input seriously.
INPUT_COMPLETENESS_MIN = 0.5

# Above this share of unsupported claims, the analysis is too shaky to show.
MAX_UNSUPPORTED_SHARE = 0.5

# Sub-factor weights for the evidence-quality (retrieval) signal, which sum
# to 1.0. Relevance dominates because a pile of relevant evidence with one
# weakly-matching claim is not a confident basis.
RETRIEVAL_WEIGHTS: dict[str, float] = {
    "relevance": 0.55,
    "meaningful": 0.20,
    "on_domain": 0.25,
}

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


ABSTAIN_REASON_UNKNOWN_CITATION = (
    "Some claims cite evidence references or authorities that could not be "
    "verified against the supplied legal corpus. Confidence was adjusted "
    "downward and the analysis is being withheld pending verification."
)


ABSTAIN_REASON_CLASSIFICATION_UNKNOWN = (
    "The system could not confidently determine what type of product or "
    "innovation this is from the provided information. Without a reliable "
    "classification, no confident regulatory roadmap can be produced."
)


ABSTAIN_REASON_TOO_MANY_UNSUPPORTED = (
    "Too many of the generated claims lack supporting statutory evidence. "
    "The retrieved legal corpus does not sufficiently ground this analysis, "
    "so the roadmap is being withheld."
)


ABSTAIN_REASON_INSUFFICIENT_INPUT = (
    "Most clarification answers were 'Not sure' or left incomplete. The "
    "input is too vague to classify reliably, so the roadmap is being "
    "withheld pending more information."
)


# Classification categories / display names that mean "we could not figure
# out what the product is at all" — a fundamental input insufficiency.
UNKNOWN_CLASSIFICATION_CATEGORIES = {
    "unknown_insufficient_information",
    "unknown / insufficient information",
    "unknown",
    "insufficient information",
}


# Phrases/words that indicate an authority field carries NO usable
# information (placeholder values filled by upstream adapters), as opposed
# to a real (recognized or unrecognized) authority.
AUTHORITY_UNKNOWN_PHRASES = ("not provided", "not listed", "not available", "not yet available")
AUTHORITY_UNKNOWN_TOKENS = {"unknown", "unavailable", "tbd", "na"}


def _is_authority_unknown(authority: str) -> bool:
    """True when the authority value is empty or a placeholder such as
    'Not provided by the legal corpus yet' / 'unknown' / 'unavailable'.

    These carry no authority information and must NEVER earn authority credit.
    """
    norm = (authority or "").strip().casefold()
    if not norm:
        return True
    if any(phrase in norm for phrase in AUTHORITY_UNKNOWN_PHRASES):
        return True
    tokens = set(re.findall(r"[a-z0-9]+", norm))
    return bool(tokens & AUTHORITY_UNKNOWN_TOKENS)


def _best_authority_score(claim_result: dict[str, Any]) -> float:
    """Authority credit for the best evidence of one claim.

    Scoring is honest and documented:
      100 — authority is on the known-authority list.
        0 — authority is empty, None, or a placeholder ('Not provided by
            the legal corpus yet', 'unknown', 'unavailable', ...): absence
            of information earns no credit.
       40 — a real-looking authority present but NOT on the known list.
            Conservative credit: it is not assumed to be fake, but it is
            not treated as verified either.
    """
    best = claim_result.get("best_evidence") or {}
    authority = (best.get("authority") or "").strip()
    if _is_authority_unknown(authority):
        return 0.0
    return 100.0 if _is_known_authority(authority) else 40.0


def confidence_level(score: float) -> str:
    """Map a 0-100 confidence score to HIGH / MEDIUM / LOW."""
    if score >= LEVEL_HIGH_MIN:
        return CONFIDENCE_HIGH
    if score >= LEVEL_MEDIUM_MIN:
        return CONFIDENCE_MEDIUM
    return CONFIDENCE_LOW


def _is_classification_unknown(classification: Any) -> bool:
    """True when the classification says the product type could not be
    determined (e.g. 'unknown_insufficient_information'). Accepts either a
    plain category string or the classification dict from the pipeline."""
    if classification is None:
        return False
    if isinstance(classification, str):
        category = classification.strip().casefold()
        return category in UNKNOWN_CLASSIFICATION_CATEGORIES
    if isinstance(classification, dict):
        category = str(classification.get("category") or "").strip().casefold()
        return category in UNKNOWN_CLASSIFICATION_CATEGORIES
    return False


def _classification_display(classification: Any) -> str:
    if isinstance(classification, dict):
        return str(classification.get("category") or "")
    return str(classification or "")


def _is_meaningful_domain(value: Any) -> bool:
    """A legal_domain is meaningful only when it carries real information —
    not empty and not a placeholder filled by an upstream adapter."""
    normed = str(value or "").strip().casefold()
    if not normed:
        return False
    return not any(
        phrase in normed
        for phrase in ("not provided", "not listed", "not available", "unknown")
    )


def _calculate_retrieval_quality(
    verification_results: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    *,
    required_domains: list[str] | None = None,
) -> float:
    """Relevance-weighted retrieval quality on the 0-100 scale.

    Sub-factors (weights from RETRIEVAL_WEIGHTS):
      relevance   (55%): mean best-similarity across claims, normalized so
                         that similarity >= RELEVANCE_REFERENCE_SCORE (0.70)
                         = 100%. This replaces the old count-only heuristic
                         (min(count/6, 1.0)) which rewarded ANY 6 chunks.
      meaningful  (20%): fraction of distinct evidence items actually used
                         as the best match for some claim. Evidence nobody
                         cites is not doing useful work.
      on_domain   (25%): fraction of used evidence whose legal_domain is in
                         the required_domains set. If required_domains is
                         None we fall back to the jurisdiction-match share;
                         if it is an empty list (product type unknown) the
                         score is 0 — domain coverage cannot be confirmed.

    Note: `relevance` uses PARTIALLY_SUPPORTED_MIN as the floor for
    "relevant at all"; below ~0.45 a claim is semantically unrelated to its
    best evidence and earns ~0 relevance credit.
    """
    if not verification_results:
        return 0.0

    relevance_floor = 0.45  # PARTIALLY_SUPPORTED_MIN floor for "relevant"

    best_scores: list[float] = []
    for result in verification_results:
        best = result.get("score") or result.get("similarity_score") or 0.0
        try:
            best_scores.append(float(best))
        except (TypeError, ValueError):
            best_scores.append(0.0)

    if best_scores:
        mean_similarity = sum(best_scores) / len(best_scores)
        if mean_similarity <= relevance_floor:
            relevance = 0.0
        else:
            relevance = min(
                mean_similarity / RELEVANCE_REFERENCE_SCORE, 1.0
            ) * 100.0
    else:
        relevance = 0.0

    used_ids: set[str] = set()
    for result in verification_results:
        best_ev = result.get("best_evidence") or {}
        eid = str(best_ev.get("id") or "").strip()
        if eid:
            used_ids.add(eid)

    unique_ids: set[str] = set()
    for item in evidence or []:
        eid = str(item.get("id") or "").strip()
        if eid:
            unique_ids.add(eid)
    unique_count = len(unique_ids) if unique_ids else max(len(evidence or []), 1)
    meaningful = (len(used_ids) / unique_count) * 100.0 if unique_count else 0.0

    if required_domains is not None:
        domain_set = {
            d.strip().casefold() for d in required_domains if str(d or "").strip()
        }
        if not domain_set:
            on_domain = 0.0
        else:
            matched = 0
            used_items = [
                item
                for item in evidence or []
                if str(item.get("id") or "").strip() in used_ids
            ]
            if not used_items:
                on_domain = 0.0
            else:
                for item in used_items:
                    domain = str(item.get("legal_domain") or "").strip().casefold()
                    if domain and domain in domain_set:
                        matched += 1
                on_domain = (matched / len(used_items)) * 100.0
    else:
        jurisdiction_ok = sum(
            1 for result in verification_results if result.get("jurisdiction_match")
        )
        on_domain = (
            jurisdiction_ok / len(verification_results) * 100.0
            if verification_results
            else 0.0
        )

    return (
        relevance * RETRIEVAL_WEIGHTS["relevance"]
        + meaningful * RETRIEVAL_WEIGHTS["meaningful"]
        + on_domain * RETRIEVAL_WEIGHTS["on_domain"]
    )


def calculate_confidence(
    verification_results: list[dict[str, Any]],
    *,
    evidence: list[dict[str, Any]] | None = None,
    classification: Any = None,
    input_completeness: float | None = None,
    required_domains: list[str] | None = None,
) -> dict[str, Any]:
    """
    Compute the M5 confidence bundle on a 0-100 scale.

    Four signals (Roadmap §19-23):
      retrieval_quality (30%): relevance-weighted evidence quality — how
                                well the retrieved evidence actually matches
                                and covers the claims, on-domain. No longer a
                                bare evidence-count.
      source_authority   (25%): how authoritative the best evidence is.
      claim_support      (25%): weighted share of claims supported
                                (SUPPORTED = 1.0, PARTIAL = 0.5, UNSUPPORTED
                                = 0.0) — partial is NOT treated as full.
      jurisdiction_match (20%): share of claims whose best evidence matches
                                the claim's jurisdiction.

    Evidence-sufficiency penalties:
      - classification == unknown → score is capped at
        UNKNOWN_CLASSIFICATION_SCORE_CAP: without knowing what the product
        is, a medium-to-high score would misrepresent the input. Documented
        enough to be LOW on purpose.
      - input_completeness below INPUT_COMPLETENESS_MIN acts similarly on
        retrieval_quality (vague answers → vague retrieval).

    Returns {"score", "level", "signals", "note"}.
    """
    total = len(verification_results) or 1

    claim_support_pct = sum(
        (1.0 if result.get("status") == STATUS_SUPPORTED else 0.5)
        for result in verification_results
        if result.get("status") in (STATUS_SUPPORTED, STATUS_PARTIAL)
    ) / total * 100.0

    jurisdiction_ok = sum(
        1 for result in verification_results if result.get("jurisdiction_match")
    )

    evidence_list = evidence if evidence is not None else []
    retrieval_quality = _calculate_retrieval_quality(
        verification_results,
        evidence_list,
        required_domains=required_domains,
    )

    if verification_results:
        source_authority = sum(
            _best_authority_score(result) for result in verification_results
        ) / len(verification_results)
    else:
        source_authority = 0.0

    jurisdiction_match = (jurisdiction_ok / total) * 100.0

    # Input-completeness adjustment on retrieval: a mostly-"Not sure" input
    # retrieves vague, poorly-anchored evidence. This is a documented
    # penalty, not a hidden fudge — it mirrors the guardrail philosophy of
    # Roadmap §22.
    if input_completeness is not None and input_completeness < 1.0:
        retrieval_quality *= max(input_completeness, 0.0)

    signals: dict[str, float] = {
        "retrieval_quality": round(retrieval_quality, 1),
        "source_authority": round(source_authority, 1),
        "claim_support": round(claim_support_pct, 1),
        "jurisdiction_match": round(jurisdiction_match, 1),
    }

    score = sum(signals[key] * CONFIDENCE_WEIGHTS[key] for key in CONFIDENCE_WEIGHTS)

    note = None
    if _is_classification_unknown(classification):
        score = min(score, UNKNOWN_CLASSIFICATION_SCORE_CAP)
        note = (
            "The innovation could not be reliably classified from the "
            "provided information, so the confidence score is capped to LOW "
            "regardless of how similar the retrieved evidence looks."
        )
    elif input_completeness is not None and input_completeness < INPUT_COMPLETENESS_MIN:
        note = (
            "Most clarification answers were 'Not sure' or incomplete. The "
            "input is too vague for a confident roadmap."
        )

    score = round(score, 1)

    logger.info(
        "M5 confidence: score=%s level=%s signals=%s unknown_classification=%s input_completeness=%s",
        score,
        confidence_level(score),
        signals,
        _is_classification_unknown(classification),
        input_completeness,
    )

    return {
        "score": score,
        "level": confidence_level(score),
        "signals": signals,
        "note": note,
    }


def _has_flagged_citation(verification_results: list[dict[str, Any]]) -> bool:
    """True if any claim carries a citation-integrity flag:
    - UNKNOWN_CITATION: the best evidence's authority is unrecognized, or
    - UNKNOWN_CITATION_REFERENCE: the claim declared an evidence id that is
      not present in the supplied evidence set (fabricated/stale citation).
    Both are treated as warnings that the citation chain is not fully
    verifiable, not as legal contradiction detection."""
    citation_flags = {FLAG_UNKNOWN_CITATION, FLAG_UNKNOWN_CITATION_REFERENCE}
    for result in verification_results:
        if citation_flags & set(result.get("flags") or []):
            return True
    return False


def calculate_abstention(
    verification_results: list[dict[str, Any]],
    *,
    evidence: list[dict[str, Any]] | None = None,
    confidence: dict[str, Any] | None = None,
    classification: Any = None,
    input_completeness: float | None = None,
    required_domains: list[str] | None = None,
) -> dict[str, Any]:
    """
    Safe abstention decision (Roadmap §44-48).

    Abstain when any of these evidence-sufficiency conditions hold:
      - no evidence was provided, OR
      - no claims were provided, OR
      - confidence score is below ABSTAIN_SCORE_MIN (default 50), OR
      - the product type could not be classified at all
        (unknown_insufficient_information) → the analysis never has a solid
        basis, so it is always withheld, OR
      - more than half the claims are UNSUPPORTED → the corpus does not
        ground the roadmap, OR
      - most clarification answers were "Not sure" / incomplete, OR
      - a UNKNOWN_CITATION / UNKNOWN_CITATION_REFERENCE flag is present.

    A UNKNOWN_CITATION / UNKNOWN_CITATION_REFERENCE flag is a material
    warning: the citation chain cannot be fully verified, so the analysis is
    withheld pending verification. Recognized authorities never raise it.

    Returns {"abstain", "abstain_reason", "reasons"}.
    """
    confidence = confidence or calculate_confidence(
        verification_results,
        evidence=evidence,
        classification=classification,
        input_completeness=input_completeness,
        required_domains=required_domains,
    )

    reasons: list[str] = []

    if evidence is not None and len(evidence) == 0:
        reasons.append("no_evidence")
    if not verification_results:
        reasons.append("no_claims")
    if confidence.get("score", 0.0) < ABSTAIN_SCORE_MIN:
        reasons.append("low_confidence")
    if _has_flagged_citation(verification_results):
        reasons.append("unknown_citation")
    if _is_classification_unknown(classification):
        reasons.append("classification_unknown")
    if verification_results:
        unsupported_share = sum(
            1
            for result in verification_results
            if result.get("status") == STATUS_UNSUPPORTED
        ) / len(verification_results)
        if unsupported_share > MAX_UNSUPPORTED_SHARE:
            reasons.append("too_many_unsupported")
        incomplete_input = (
            input_completeness is not None
            and input_completeness < INPUT_COMPLETENESS_MIN
        )
        if incomplete_input:
            reasons.append("insufficient_input")

    if reasons:
        reason = None
        if "no_evidence" in reasons:
            reason = ABSTAIN_REASON_NO_EVIDENCE
        elif "no_claims" in reasons:
            reason = ABSTAIN_REASON_NO_CLAIMS
        elif "classification_unknown" in reasons:
            reason = ABSTAIN_REASON_CLASSIFICATION_UNKNOWN
        elif "insufficient_input" in reasons:
            reason = ABSTAIN_REASON_INSUFFICIENT_INPUT
        elif "too_many_unsupported" in reasons:
            reason = ABSTAIN_REASON_TOO_MANY_UNSUPPORTED
        elif "unknown_citation" in reasons:
            reason = ABSTAIN_REASON_UNKNOWN_CITATION
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
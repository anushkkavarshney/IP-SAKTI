"""
IP-SAKTI Navigator — Member 5 (Verification + Confidence) Package.

Public entry points:
    extract_claims          — TASK 1: canonical claim extraction interface.
    verify_claims           — full batch verification (alias of verify_claims_batch).
    verify_claim            — single-claim verification.
    calculate_confidence    — 0-100 confidence engine (four signals).
    calculate_abstention    — safe abstention decision.
"""

from .verifier import (
    DEFAULT_TOP_K,
    MODEL_NAME,
    PARTIALLY_SUPPORTED_MIN,
    SUPPORTED_MIN,
    load_model,
    verify_claim,
    verify_claims,
    verify_claims_batch,
)

from .schemas import (
    DEFAULT_JURISDICTION,
    FLAG_EMPTY_CLAIM,
    FLAG_EMPTY_EVIDENCE_PASSAGE,
    FLAG_JURISDICTION_MISMATCH,
    FLAG_LONG_CLAIM,
    FLAG_MODEL_ERROR,
    FLAG_NO_EVIDENCE,
    FLAG_UNKNOWN_CITATION,
    SAFETY_NOTE,
    STATUS_PARTIAL,
    STATUS_SUPPORTED,
    STATUS_UNSUPPORTED,
    SUPPORT_TYPE,
    build_summary,
    deduplicate_claims,
    extract_claims,
    normalize_claim,
    normalize_claims_payload,
    normalize_evidence_item,
    normalize_evidence_payload,
    wrap_verification_payload,
)

from .confidence import (
    CONFIDENCE_HIGH,
    CONFIDENCE_LOW,
    CONFIDENCE_MEDIUM,
    CONFIDENCE_WEIGHTS,
    ABSTAIN_SCORE_MIN,
    calculate_abstention,
    calculate_confidence,
    confidence_level,
    validate_no_contradiction_detection,
)

__all__ = [
    "verify_claims",
    "verify_claims_batch",
    "verify_claim",
    "load_model",
    "extract_claims",
    "calculate_confidence",
    "calculate_abstention",
    "confidence_level",
    "validate_no_contradiction_detection",
    "normalize_claims_payload",
    "normalize_evidence_payload",
    "normalize_claim",
    "normalize_evidence_item",
    "wrap_verification_payload",
    "build_summary",
    "deduplicate_claims",
    "STATUS_SUPPORTED",
    "STATUS_PARTIAL",
    "STATUS_UNSUPPORTED",
    "FLAG_NO_EVIDENCE",
    "FLAG_EMPTY_CLAIM",
    "FLAG_EMPTY_EVIDENCE_PASSAGE",
    "FLAG_LONG_CLAIM",
    "FLAG_MODEL_ERROR",
    "FLAG_JURISDICTION_MISMATCH",
    "FLAG_UNKNOWN_CITATION",
    "CONFIDENCE_HIGH",
    "CONFIDENCE_MEDIUM",
    "CONFIDENCE_LOW",
    "CONFIDENCE_WEIGHTS",
    "ABSTAIN_SCORE_MIN",
    "DEFAULT_JURISDICTION",
    "SUPPORT_TYPE",
    "SAFETY_NOTE",
    "MODEL_NAME",
    "SUPPORTED_MIN",
    "PARTIALLY_SUPPORTED_MIN",
    "DEFAULT_TOP_K",
]
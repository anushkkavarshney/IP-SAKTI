"""
IP-SAKTI Navigator — Member 5 (Verification + Confidence) Package.

Public entry points for claim-to-evidence verification.
"""

from verifier import (
    verify_claims,
    verify_claims_batch,
    verify_claim,
    load_model,
    MODEL_NAME,
    SUPPORTED_MIN,
    PARTIALLY_SUPPORTED_MIN,
    DEFAULT_TOP_K,
)

from schemas import (
    normalize_claims_payload,
    normalize_evidence_payload,
    normalize_claim,
    normalize_evidence_item,
    wrap_verification_payload,
    STATUS_SUPPORTED,
    STATUS_PARTIAL,
    STATUS_UNSUPPORTED,
    FLAG_NO_EVIDENCE,
    FLAG_EMPTY_CLAIM,
    FLAG_JURISDICTION_MISMATCH,
    DEFAULT_JURISDICTION,
    SUPPORT_TYPE,
    SAFETY_NOTE,
)

__all__ = [
    "verify_claims",
    "verify_claims_batch",
    "verify_claim",
    "load_model",
    "normalize_claims_payload",
    "normalize_evidence_payload",
    "normalize_claim",
    "normalize_evidence_item",
    "wrap_verification_payload",
    "STATUS_SUPPORTED",
    "STATUS_PARTIAL",
    "STATUS_UNSUPPORTED",
    "FLAG_NO_EVIDENCE",
    "FLAG_EMPTY_CLAIM",
    "FLAG_JURISDICTION_MISMATCH",
    "DEFAULT_JURISDICTION",
    "SUPPORT_TYPE",
    "SAFETY_NOTE",
    "MODEL_NAME",
    "SUPPORTED_MIN",
    "PARTIALLY_SUPPORTED_MIN",
    "DEFAULT_TOP_K",
]

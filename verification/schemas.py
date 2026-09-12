"""
Member 5 — JSON data contracts, normalization, and flags.

M3 claims  →  M5  ←  M4 evidence
                 ↓
         verification result

These helpers normalize field names, fill safe defaults, and validate
inputs.  They do NOT run embeddings, batch verification, confidence,
or abstention.
"""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

DEFAULT_JURISDICTION = "India"

SUPPORT_TYPE = "preliminary_semantic_support"
SAFETY_NOTE = (
    "Similarity is a first-stage relevance signal only. "
    "It does not establish legal validity or legal proof."
)

STATUS_SUPPORTED = "SUPPORTED"
STATUS_PARTIAL = "PARTIALLY_SUPPORTED"
STATUS_UNSUPPORTED = "UNSUPPORTED"

FLAG_NO_EVIDENCE = "NO_EVIDENCE"
FLAG_EMPTY_CLAIM = "EMPTY_CLAIM"
FLAG_JURISDICTION_MISMATCH = "JURISDICTION_MISMATCH"
FLAG_UNKNOWN_CITATION = "UNKNOWN_CITATION"
FLAG_EMPTY_EVIDENCE_PASSAGE = "EMPTY_EVIDENCE_PASSAGE"
FLAG_LONG_CLAIM = "LONG_CLAIM"
FLAG_MODEL_ERROR = "MODEL_ERROR"

CONFIDENCE_HIGH = "HIGH"
CONFIDENCE_MEDIUM = "MEDIUM"
CONFIDENCE_LOW = "LOW"

# Proposed example payloads (synthetic / demo only).
EXAMPLE_M3_CLAIMS = {
    "jurisdiction": DEFAULT_JURISDICTION,
    "claims": [
        {
            "id": "claim_1",
            "text": "The innovation may involve a biological resource.",
            "jurisdiction": DEFAULT_JURISDICTION,
        },
        {
            "id": "claim_2",
            "text": "A new extraction process may warrant further patentability assessment.",
            "jurisdiction": DEFAULT_JURISDICTION,
        },
    ],
}

EXAMPLE_M4_EVIDENCE = {
    "jurisdiction": DEFAULT_JURISDICTION,
    "evidence": [
        {
            "id": "evidence_1",
            "text": "The innovation may involve a biological resource if it uses plants, animals, microorganisms, or parts of them.",
            "document": "SYNTHETIC DEMO — Biodiversity overview notes",
            "section": "demo-overview",
            "jurisdiction": DEFAULT_JURISDICTION,
            "source_url": "SYNTHETIC DEMO — not an official legal source",
            "legal_domain": "Biodiversity",
            "authority": "",
            "effective_date": "",
        },
        {
            "id": "evidence_2",
            "text": "A novel extraction or manufacturing process that is not already known may be considered for further patentability assessment by a qualified professional.",
            "document": "SYNTHETIC DEMO — Patent process notes",
            "section": "demo-process",
            "jurisdiction": DEFAULT_JURISDICTION,
            "source_url": "SYNTHETIC DEMO — not an official legal source",
            "legal_domain": "Patent",
            "authority": "",
            "effective_date": "",
        },
    ],
}

KNOWN_AUTHORITIES = {
    "india patent office", "ip india", "ipo",
    "indian patent office", "controller general of patents",
    "national biodiversity authority", "nba",
    "cdsco", "central drugs standard control organisation",
    "fssai", "food safety and standards authority of india",
    "ministry of ayush", "ayush",
    "ministry of commerce and industry", "dpiit",
    "indian council of medical research", "icmr",
    "ministry of environment forest and climate change",
    "ministry of environment, forest and climate change", "moefcc",
    "controller general of patents designs and trademarks",
    "office of the controller general of patents",
    "drug controller general of india", "dcgi",
    "sebi", "securities and exchange board of india",
    "central board of direct taxes", "cbdt",
    "ipsakti official", "department of industrial policy",
    "department for promotion of industry and internal trade",
}


def normalize_jurisdiction(value: Any, default: str = DEFAULT_JURISDICTION) -> str:
    text = str(value or "").strip()
    return text if text else default


def jurisdictions_match(claim_jurisdiction: str, evidence_jurisdiction: str) -> bool:
    """String compare only. Not a legal conflict check."""
    left = normalize_jurisdiction(claim_jurisdiction).casefold()
    right = normalize_jurisdiction(evidence_jurisdiction).casefold()
    return left == right


def _first_present(item: dict[str, Any], keys: list[str], default: str = "") -> str:
    for key in keys:
        if item.get(key) not in (None, ""):
            return str(item[key]).strip()
    return default


def _is_known_authority(authority: str) -> bool:
    """Check whether a string matches a known Indian legal authority.
    Empty/blank input is never treated as a known authority."""
    normed = (authority or "").strip().casefold()
    if not normed:
        return False
    return any(known in normed or normed in known for known in KNOWN_AUTHORITIES)


def extract_claims(
    claims: dict[str, Any] | list | None,
) -> dict[str, Any]:
    """
    TASK 1 — Canonical public API to extract and normalize claims from
    M3 output (or any upstream payload).

    Accepts:
      - { "claims": [...] }  with optional "jurisdiction"
      - [ claim_dict, ... ]
      - None / empty  → returns empty list
    """
    if not claims:
        return {"jurisdiction": DEFAULT_JURISDICTION, "claims": []}

    if isinstance(claims, list):
        raw_items = claims
        default_jurisdiction = DEFAULT_JURISDICTION
    elif isinstance(claims, dict):
        default_jurisdiction = normalize_jurisdiction(claims.get("jurisdiction"))
        raw_items = claims.get("claims") or []
    else:
        return {"jurisdiction": DEFAULT_JURISDICTION, "claims": []}

    out_claims = []
    for idx, raw in enumerate(raw_items, start=1):
        normed = normalize_claim(
            raw,
            default_id=f"claim_{idx}",
            default_jurisdiction=default_jurisdiction,
        )
        if normed.get("text"):
            out_claims.append(normed)
    return {"jurisdiction": default_jurisdiction, "claims": out_claims}


def normalize_claim(
    claim: str | dict[str, Any],
    *,
    default_id: str = "claim_1",
    default_jurisdiction: str = DEFAULT_JURISDICTION,
) -> dict[str, Any]:
    """
    Accept Day 1 claim strings or M3 claim objects.
    None-safe: any non-dict/non-string input returns an empty-text placeholder.

    M3 may send `id` (roadmap) or `claim_id` (alias).
    """
    if claim is None:
        return {
            "id": default_id,
            "text": "",
            "jurisdiction": normalize_jurisdiction(default_jurisdiction),
        }
    if isinstance(claim, str):
        return {
            "id": default_id,
            "text": claim.strip(),
            "jurisdiction": normalize_jurisdiction(default_jurisdiction),
        }
    if not isinstance(claim, dict):
        return {
            "id": default_id,
            "text": "",
            "jurisdiction": normalize_jurisdiction(default_jurisdiction),
        }

    payload_jurisdiction = normalize_jurisdiction(
        claim.get("jurisdiction"),
        default_jurisdiction,
    )
    return {
        "id": _first_present(claim, ["id", "claim_id"], default_id),
        "text": str(claim.get("text") or "").strip(),
        "jurisdiction": payload_jurisdiction,
    }


def normalize_claims_payload(payload: dict[str, Any] | list | None) -> dict[str, Any]:
    """Accept `{claims: [...]}` or a bare list of claims."""
    if payload is None:
        return {"jurisdiction": DEFAULT_JURISDICTION, "claims": []}
    if isinstance(payload, list):
        default_jurisdiction = DEFAULT_JURISDICTION
        raw_claims = payload
    elif isinstance(payload, dict):
        default_jurisdiction = normalize_jurisdiction(payload.get("jurisdiction"))
        raw_claims = payload.get("claims") or []
    else:
        return {"jurisdiction": DEFAULT_JURISDICTION, "claims": []}

    claims = []
    for index, raw in enumerate(raw_claims, start=1):
        claims.append(
            normalize_claim(
                raw,
                default_id=f"claim_{index}",
                default_jurisdiction=default_jurisdiction,
            )
        )
    return {"jurisdiction": default_jurisdiction, "claims": claims}


def normalize_evidence_item(
    item: dict[str, Any],
    *,
    default_id: str = "evidence_1",
    default_jurisdiction: str = DEFAULT_JURISDICTION,
) -> dict[str, Any]:
    """
    Accept Day 1 evidence (`source`) and M4 evidence (`source_url`, `id`).
    None/malformed-safe.  Keep original extra keys.
    """
    if item is None or not isinstance(item, dict):
        return {
            "id": default_id,
            "text": "",
            "document": "",
            "section": "",
            "jurisdiction": default_jurisdiction,
            "source_url": "",
            "source": "",
            "legal_domain": "",
            "authority": "",
            "effective_date": "",
        }

    normalized = deepcopy(item)
    source_url = _first_present(item, ["source_url", "source"])
    document = _first_present(item, ["document", "document_name"])
    jurisdiction = normalize_jurisdiction(item.get("jurisdiction"), default_jurisdiction)

    normalized["id"] = _first_present(item, ["id", "evidence_id"], default_id)
    normalized["text"] = str(item.get("text") or "").strip()
    normalized["document"] = document
    normalized["section"] = str(item.get("section") or "").strip()
    normalized["jurisdiction"] = jurisdiction
    normalized["source_url"] = source_url
    if not normalized.get("source"):
        normalized["source"] = source_url
    normalized.setdefault("legal_domain", item.get("legal_domain") or "")
    normalized.setdefault("authority", item.get("authority") or "")
    normalized.setdefault("effective_date", item.get("effective_date") or "")
    return normalized


def normalize_evidence_payload(payload: dict[str, Any] | list | None) -> dict[str, Any]:
    """Accept `{evidence: [...]}` or a bare evidence list."""
    if payload is None:
        return {"jurisdiction": DEFAULT_JURISDICTION, "evidence": []}
    if isinstance(payload, list):
        default_jurisdiction = DEFAULT_JURISDICTION
        raw_items = payload
    elif isinstance(payload, dict):
        default_jurisdiction = normalize_jurisdiction(payload.get("jurisdiction"))
        raw_items = payload.get("evidence") or []
    else:
        return {"jurisdiction": DEFAULT_JURISDICTION, "evidence": []}

    evidence = []
    for index, raw in enumerate(raw_items, start=1):
        evidence.append(
            normalize_evidence_item(
                raw,
                default_id=f"evidence_{index}",
                default_jurisdiction=default_jurisdiction,
            )
        )
    return {"jurisdiction": default_jurisdiction, "evidence": evidence}


def ranked_evidence_row(score: float, item: dict[str, Any]) -> dict[str, Any]:
    """Compact ranked row for M5 output. Metadata is not dropped."""
    return {
        "evidence_id": item.get("id", ""),
        "score": score,
        "document": item.get("document", ""),
        "section": item.get("section", ""),
        "jurisdiction": item.get("jurisdiction", ""),
        "source_url": item.get("source_url") or item.get("source", ""),
    }


def unknown_citation_flag_for(authority: str) -> str | None:
    """Return FLAG_UNKNOWN_CITATION if an authority is non-empty but
    not on the known-authority list."""
    if not authority:
        return None
    return None if _is_known_authority(authority) else FLAG_UNKNOWN_CITATION


def empty_claim_result(
    claim: dict[str, Any],
    flag: str,
    note: str,
    *,
    extra_flags: list[str] | None = None,
) -> dict[str, Any]:
    flags = [flag]
    for extra in extra_flags or []:
        if extra and extra not in flags:
            flags.append(extra)
    return {
        "claim_id": claim.get("id", "claim_1"),
        "claim": claim.get("text", ""),
        "status": STATUS_UNSUPPORTED,
        "score": 0.0,
        "similarity_score": 0.0,
        "support_type": SUPPORT_TYPE,
        "note": note,
        "best_evidence_id": None,
        "best_evidence": None,
        "ranked_evidence": [],
        "jurisdiction_match": False,
        "flags": flags,
    }


def build_claim_result(
    claim: dict[str, Any],
    status: str,
    score: float,
    ranked: list[dict[str, Any]],
    note: str = SAFETY_NOTE,
    *,
    jurisdiction_match: bool | None = None,
    extra_flags: list[str] | None = None,
) -> dict[str, Any]:
    """Build one M5 per-claim object. Does not decide legal truth."""
    best_row = ranked[0] if ranked else None
    best_evidence = best_row["evidence"] if best_row else None
    best_id = best_evidence.get("id") if best_evidence else None
    flags: list[str] = []
    if best_evidence:
        match = (
            jurisdictions_match(claim.get("jurisdiction", ""), best_evidence.get("jurisdiction", ""))
            if jurisdiction_match is None
            else jurisdiction_match
        )
        if not match:
            flags.append(FLAG_JURISDICTION_MISMATCH)
    else:
        match = False

    for extra in extra_flags or []:
        if extra and extra not in flags:
            flags.append(extra)

    return {
        "claim_id": claim.get("id", "claim_1"),
        "claim": claim.get("text", ""),
        "status": status,
        "score": score,
        "similarity_score": score,
        "support_type": SUPPORT_TYPE,
        "note": note,
        "best_evidence_id": best_id,
        "best_evidence": best_evidence,
        "ranked_evidence": [
            ranked_evidence_row(row["score"], row["evidence"]) for row in ranked
        ],
        "jurisdiction_match": match,
        "flags": flags,
    }


def build_summary(verification: list[dict[str, Any]]) -> dict[str, Any]:
    unsupported = [
        {
            "claim_id": row["claim_id"],
            "claim": row["claim"],
            "status": row["status"],
            "flags": row.get("flags", []),
        }
        for row in verification
        if row.get("status") == STATUS_UNSUPPORTED
    ]
    return {
        "total_claims": len(verification),
        "supported_claims": sum(1 for row in verification if row.get("status") == STATUS_SUPPORTED),
        "partially_supported_claims": sum(
            1 for row in verification if row.get("status") == STATUS_PARTIAL
        ),
        "unsupported_claims": unsupported,
    }


def wrap_verification_payload(verification: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "support_type": SUPPORT_TYPE,
        "note": SAFETY_NOTE,
        "verification": verification,
        "summary": build_summary(verification),
    }


LONG_CLAIM_WORD_THRESHOLD = 150
LONG_CLAIM_CHAR_THRESHOLD = 1200


def is_long_claim(text: str) -> bool:
    """Detect excessively long claims that may dilute similarity."""
    words = text.split()
    return len(words) > LONG_CLAIM_WORD_THRESHOLD or len(text) > LONG_CLAIM_CHAR_THRESHOLD


def deduplicate_claims(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove duplicate claims by normalized text, preserving first occurrence.
    Empty-text claims are preserved so the verifier can flag them."""
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for claim in claims:
        normed = (claim.get("text") or "").strip().casefold()
        if normed in seen:
            continue
        seen.add(normed)
        deduped.append(claim)
    return deduped


def print_contract_examples() -> None:
    print("M3 -> M5 (proposed)")
    print(json.dumps(EXAMPLE_M3_CLAIMS, indent=2))
    print()
    print("M4 -> M5 (proposed, SYNTHETIC DEMO evidence)")
    print(json.dumps(EXAMPLE_M4_EVIDENCE, indent=2))
    print()
    print("Normalized claims:")
    print(json.dumps(normalize_claims_payload(EXAMPLE_M3_CLAIMS), indent=2))
    print()
    print("Normalized evidence:")
    print(json.dumps(normalize_evidence_payload(EXAMPLE_M4_EVIDENCE), indent=2))


if __name__ == "__main__":
    print_contract_examples()

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
FLAG_UNKNOWN_CITATION_REFERENCE = "UNKNOWN_CITATION_REFERENCE"
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


def normalize_evidence_ids(value: Any) -> list[str]:
    """Normalize a claim's declared `evidence_ids` into a clean, de-duplicated
    list of non-empty id strings.

    Accepts None, a single id string, or an iterable of ids. Never raises.
    """
    if value is None:
        return []
    if isinstance(value, str):
        raw_items: list[Any] = [value]
    elif isinstance(value, (list, tuple, set, frozenset)):
        raw_items = list(value)
    else:
        return []

    out: list[str] = []
    for raw in raw_items:
        if raw is None:
            continue
        text = str(raw).strip()
        if text and text not in out:
            out.append(text)
    return out


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
    Claim-level `claim_type` and `evidence_ids` (explicit citations) are
    preserved so that downstream citation validation can detect fabricated
    or stale evidence references.
    """
    if claim is None:
        return {
            "id": default_id,
            "text": "",
            "jurisdiction": normalize_jurisdiction(default_jurisdiction),
            "claim_type": "",
            "evidence_ids": [],
        }
    if isinstance(claim, str):
        return {
            "id": default_id,
            "text": claim.strip(),
            "jurisdiction": normalize_jurisdiction(default_jurisdiction),
            "claim_type": "",
            "evidence_ids": [],
        }
    if not isinstance(claim, dict):
        return {
            "id": default_id,
            "text": "",
            "jurisdiction": normalize_jurisdiction(default_jurisdiction),
            "claim_type": "",
            "evidence_ids": [],
        }

    payload_jurisdiction = normalize_jurisdiction(
        claim.get("jurisdiction"),
        default_jurisdiction,
    )
    return {
        "id": _first_present(claim, ["id", "claim_id"], default_id),
        "text": str(claim.get("text") or "").strip(),
        "jurisdiction": payload_jurisdiction,
        "claim_type": str(claim.get("claim_type") or "").strip(),
        "evidence_ids": normalize_evidence_ids(claim.get("evidence_ids")),
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
    Normalize evidence from ANY upstream shape into the canonical M5 shape.

    Supported field aliases (both are always accepted):
      id  <- `id` | `evidence_id` | `doc_id`
      document <- `document` | `document_name` | `act_name`
      text <- `text` | `content`
      source_url <- `source_url` | `source`
      legal_domain  <- `legal_domain` | `category`
      section / authority / as_of_date / effective_date / jurisdiction

    This makes raw Member 4 corpus chunks (doc_id / act_name / section /
    as_of_date / category / authority / source_url / content) consumable
    directly, as well as the backend-normalized shape (id / document_name /
    text / legal_domain / ...). None/malformed-safe. Original extra keys are
    preserved and never invented.
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
            "as_of_date": "",
        }

    normalized = deepcopy(item)
    source_url = _first_present(item, ["source_url", "source"])
    document = _first_present(item, ["document", "document_name", "act_name"])
    legal_domain = _first_present(item, ["legal_domain", "category"])
    jurisdiction = normalize_jurisdiction(item.get("jurisdiction"), default_jurisdiction)
    raw_text = item.get("text")
    if raw_text is None:
        raw_text = item.get("content")

    normalized["id"] = _first_present(item, ["id", "evidence_id", "doc_id"], default_id)
    normalized["text"] = str(raw_text or "").strip()
    normalized["document"] = document
    normalized["section"] = str(item.get("section") or "").strip()
    normalized["jurisdiction"] = jurisdiction
    normalized["source_url"] = source_url
    if not normalized.get("source"):
        normalized["source"] = source_url
    normalized["legal_domain"] = legal_domain
    normalized["authority"] = str(item.get("authority") or "").strip()
    normalized["effective_date"] = str(item.get("effective_date") or "").strip()
    normalized["as_of_date"] = str(item.get("as_of_date") or "").strip()
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


def split_citation_ids(
    declared: list[str],
    valid_evidence_ids: set[str] | list[str],
) -> tuple[list[str], list[str]]:
    """Separate a claim's declared evidence ids into (valid, unknown).

    Citation identity is completely separate from semantic similarity: an
    id is only "valid" when it matches an evidence record actually supplied
    to M5. Unknown ids are never made valid by semantic overlap.
    """
    valid_set = {str(eid).strip() for eid in (valid_evidence_ids or []) if str(eid).strip()}
    valid: list[str] = []
    unknown: list[str] = []
    for eid in normalize_evidence_ids(declared):
        (valid if eid in valid_set else unknown).append(eid)
    return valid, unknown


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

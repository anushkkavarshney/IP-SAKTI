"""
Member 5 — Remaining-work regression suite.

Covers the audit-driven gaps and their required test groups:

  G1  raw M4 evidence vocabulary (doc_id / act_name / content / category /
      as_of_date) normalizes without information loss
  G2  backend-normalized evidence shape still works (no regression)
  G3  claim `evidence_ids` survive normalization
  G4  valid declared citation  -> no fabricated-citation flag
  G5  fabricated declared citation -> UNKNOWN_CITATION_REFERENCE flag, and
      the fake id is never presented as a valid citation
  G6  mixed citations (valid + fake) -> valid kept, fake explicitly flagged
  G7  no evidence_ids -> normal semantic verification, no forced flag
  G8  empty evidence_ids [] -> no flag
  G9  evidence_ids None -> no crash
  G10 honest authority scoring (recognized / missing / None / empty /
      placeholder / unrecognized)
  G11 confidence regression (30/25/25/20, 0-100, 80 HIGH / 50 MEDIUM / LOW)
  G12 raw M4 evidence end-to-end through the full M5 pipeline
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from verification import (
    FLAG_UNKNOWN_CITATION_REFERENCE,
    STATUS_PARTIAL,
    STATUS_SUPPORTED,
    STATUS_UNSUPPORTED,
    calculate_confidence,
    confidence_level,
    extract_claims,
    load_model,
    normalize_claim,
    normalize_evidence_item,
    normalize_evidence_payload,
    verify_claim,
    verify_claims_batch,
)

MODEL = load_model()

RAW_M4_EVIDENCE = {
    "doc_id": "e1",
    "act_name": "Example Indian Act",
    "section": "Section 3",
    "as_of_date": "2026-01-01",
    "effective_date": "2026-01-01",
    "jurisdiction": "India",
    "category": "Patent",
    "authority": "Indian Patent Office",
    "source_url": "https://example.gov.in/source",
    "content": (
        "An invention may not be a patentable invention if it is a mere "
        "discovery of a scientific principle or the formulation of an "
        "abstract theory."
    ),
}

SUPPORTED_CLAIM_TEXT = (
    "A mere discovery of a scientific principle is not a patentable invention."
)


def _normalized_evidence(eid: str = "e1", authority: str = "National Biodiversity Authority") -> list[dict]:
    return [
        {
            "id": eid,
            "text": SUPPORTED_CLAIM_TEXT,
            "document": "Example Indian Act",
            "section": "Section 3",
            "jurisdiction": "India",
            "authority": authority,
        }
    ]


# ---------------------------------------------------------------------------
# G1 — Raw M4 evidence vocabulary
# ---------------------------------------------------------------------------
def test_raw_m4_evidence_normalizes_without_information_loss():
    norm = normalize_evidence_item(RAW_M4_EVIDENCE)
    assert norm["id"] == "e1"                       # doc_id
    assert norm["document"] == "Example Indian Act"  # act_name
    assert norm["section"] == "Section 3"
    assert norm["text"] == RAW_M4_EVIDENCE["content"]  # content -> text, non-empty
    assert norm["legal_domain"] == "Patent"         # category -> legal_domain
    assert norm["authority"] == "Indian Patent Office"
    assert norm["source_url"] == "https://example.gov.in/source"
    assert norm["as_of_date"] == "2026-01-01"
    assert norm["effective_date"] == "2026-01-01"
    assert norm["jurisdiction"] == "India"
    assert norm["text"]


def test_raw_m4_payload_accepted():
    payload = normalize_evidence_payload(
        {"jurisdiction": "India", "evidence": [RAW_M4_EVIDENCE]}
    )
    assert len(payload["evidence"]) == 1
    assert payload["evidence"][0]["id"] == "e1"
    assert payload["evidence"][0]["text"]


# ---------------------------------------------------------------------------
# G2 — Backend-normalized evidence regression
# ---------------------------------------------------------------------------
def test_backend_normalized_evidence_still_works():
    backend = {
        "id": "BE1",
        "text": SUPPORTED_CLAIM_TEXT,
        "document_name": "The Biological Diversity Act, 2002",
        "section": "Section 3",
        "jurisdiction": "India",
        "source_url": "https://nbaindia.org/act/",
        "authority": "National Biodiversity Authority",
        "effective_date": "2003-02-05",
        "legal_domain": "ABS",
    }
    norm = normalize_evidence_item(backend)
    assert norm["id"] == "BE1"
    assert norm["document"] == "The Biological Diversity Act, 2002"  # document_name alias
    assert norm["legal_domain"] == "ABS"
    assert norm["authority"] == "National Biodiversity Authority"
    assert norm["text"] == SUPPORTED_CLAIM_TEXT

    payload = verify_claims_batch(
        [{"id": "C1", "text": SUPPORTED_CLAIM_TEXT, "jurisdiction": "India"}],
        [backend],
        model=MODEL,
    )
    assert payload["verification"][0]["best_evidence_id"] == "BE1"
    assert payload["verification"][0]["best_evidence"]["document"] == "The Biological Diversity Act, 2002"


# ---------------------------------------------------------------------------
# G3 — Claim evidence_ids survive normalization
# ---------------------------------------------------------------------------
def test_claim_evidence_ids_preserved():
    claim = {
        "claim_id": "c1",
        "text": "Claim text",
        "claim_type": "IP",
        "jurisdiction": "India",
        "evidence_ids": ["e1", "e2"],
    }
    norm = normalize_claim(claim)
    assert norm["id"] == "c1"                       # claim_id alias
    assert norm["claim_type"] == "IP"
    assert norm["evidence_ids"] == ["e1", "e2"]


def test_claim_evidence_ids_preserved_through_extract():
    payload = extract_claims(
        [{"id": "c1", "text": "Claim text", "evidence_ids": ["e1"]}]
    )
    assert payload["claims"][0]["evidence_ids"] == ["e1"]


def test_claim_evidence_ids_normalization_of_odd_inputs():
    assert normalize_claim({"id": "c", "text": "t", "evidence_ids": None})["evidence_ids"] == []
    assert normalize_claim({"id": "c", "text": "t", "evidence_ids": []})["evidence_ids"] == []
    assert normalize_claim({"id": "c", "text": "t", "evidence_ids": "e1"})["evidence_ids"] == ["e1"]
    assert normalize_claim({"id": "c", "text": "t", "evidence_ids": ["e1", "", "e1"]})["evidence_ids"] == ["e1"]
    assert "evidence_ids" in normalize_claim("bare string claim")


# ---------------------------------------------------------------------------
# G4 — Valid declared citation
# ---------------------------------------------------------------------------
def test_valid_citation_no_flag():
    result = verify_claim(
        {"id": "c1", "text": SUPPORTED_CLAIM_TEXT, "evidence_ids": ["e1"]},
        _normalized_evidence("e1"),
        model=MODEL,
    )
    assert FLAG_UNKNOWN_CITATION_REFERENCE not in result["flags"]
    assert result["valid_citation_ids"] == ["e1"]
    assert result["unknown_citation_ids"] == []
    assert result["best_evidence_id"] == "e1"


# ---------------------------------------------------------------------------
# G5 — Fabricated declared citation
# ---------------------------------------------------------------------------
def test_fabricated_citation_flagged_never_valid():
    result = verify_claim(
        {"id": "c1", "text": SUPPORTED_CLAIM_TEXT, "evidence_ids": ["fake_e999"]},
        _normalized_evidence("e1"),
        model=MODEL,
    )
    assert FLAG_UNKNOWN_CITATION_REFERENCE in result["flags"]
    assert result["declared_evidence_ids"] == ["fake_e999"]
    assert result["valid_citation_ids"] == []
    assert result["unknown_citation_ids"] == ["fake_e999"]
    # Semantic similarity must NOT make the fake id valid.
    assert result["best_evidence_id"] != "fake_e999"
    assert result["best_evidence_id"] == "e1"
    assert all(row["evidence_id"] != "fake_e999" for row in result["ranked_evidence"])


# ---------------------------------------------------------------------------
# G6 — Mixed citations
# ---------------------------------------------------------------------------
def test_mixed_citations_valid_preserved_fake_flagged():
    evidence = _normalized_evidence("e1") + [{
        "id": "e2",
        "text": "A novel process of extraction not previously disclosed may be considered for patent protection.",
        "document": "The Patents Act, 1970",
        "jurisdiction": "India",
        "authority": "Indian Patent Office",
    }]
    result = verify_claim(
        {"id": "c1", "text": SUPPORTED_CLAIM_TEXT, "evidence_ids": ["e1", "fake_e3"]},
        evidence,
        model=MODEL,
    )
    assert result["valid_citation_ids"] == ["e1"]
    assert result["unknown_citation_ids"] == ["fake_e3"]
    assert FLAG_UNKNOWN_CITATION_REFERENCE in result["flags"]


# ---------------------------------------------------------------------------
# G7/G8/G9 — Absent / empty / None evidence_ids
# ---------------------------------------------------------------------------
def test_no_evidence_ids_semantic_verification_continues():
    result = verify_claim(
        {"id": "c1", "text": SUPPORTED_CLAIM_TEXT},
        _normalized_evidence("e1"),
        model=MODEL,
    )
    assert result["status"] == STATUS_SUPPORTED
    assert result["declared_evidence_ids"] == []
    assert result["unknown_citation_ids"] == []
    assert FLAG_UNKNOWN_CITATION_REFERENCE not in result["flags"]


def test_empty_evidence_ids_no_flag():
    result = verify_claim(
        {"id": "c1", "text": SUPPORTED_CLAIM_TEXT, "evidence_ids": []},
        _normalized_evidence("e1"),
        model=MODEL,
    )
    assert FLAG_UNKNOWN_CITATION_REFERENCE not in result["flags"]
    assert result["status"] == STATUS_SUPPORTED


def test_none_evidence_ids_no_crash():
    result = verify_claim(
        {"id": "c1", "text": SUPPORTED_CLAIM_TEXT, "evidence_ids": None},
        _normalized_evidence("e1"),
        model=MODEL,
    )
    assert result["status"] == STATUS_SUPPORTED
    assert FLAG_UNKNOWN_CITATION_REFERENCE not in result["flags"]


def test_fabricated_citation_detected_in_batch_payload():
    payload = verify_claims_batch(
        [{"id": "c1", "text": SUPPORTED_CLAIM_TEXT, "evidence_ids": ["fake_e999"]}],
        _normalized_evidence("e1"),
        model=MODEL,
    )
    row = payload["verification"][0]
    assert FLAG_UNKNOWN_CITATION_REFERENCE in row["flags"]
    assert "unknown_citation" in payload["abstain_reasons"]


# ---------------------------------------------------------------------------
# G10 — Honest authority scoring
# ---------------------------------------------------------------------------
def _result_for_authority(authority: str | None):
    return {
        "status": STATUS_SUPPORTED,
        "jurisdiction_match": True,
        "best_evidence": ({"authority": authority} if authority is not None else {}),
        "flags": [],
    }


def _authority_signal(authority: str | None) -> float:
    return calculate_confidence([_result_for_authority(authority)], evidence=[{"id": "e1"}])[
        "signals"
    ]["source_authority"]


def test_recognized_authority_scores_full():
    assert _authority_signal("National Biodiversity Authority") == 100.0


def test_missing_authority_gets_zero():
    assert _authority_signal(None) == 0.0


def test_none_vs_empty_vs_placeholder_all_zero():
    assert _authority_signal("") == 0.0
    assert _authority_signal("Not provided by the legal corpus yet") == 0.0
    assert _authority_signal("Unknown") == 0.0
    assert _authority_signal("unavailable") == 0.0


def test_unrecognized_authority_is_conservative_not_zero():
    score = _authority_signal("Cartoon Legal Institute")
    assert 0.0 < score < 100.0


def test_placeholder_credited_less_than_unrecognized():
    assert _authority_signal("Not provided by the legal corpus yet") < _authority_signal("Cartoon Legal Institute")


# ---------------------------------------------------------------------------
# G11 — Confidence regression
# ---------------------------------------------------------------------------
def test_confidence_boundaries_unchanged():
    assert confidence_level(80.0) == "HIGH"
    assert confidence_level(79.9) == "MEDIUM"
    assert confidence_level(50.0) == "MEDIUM"
    assert confidence_level(49.9) == "LOW"


# ---------------------------------------------------------------------------
# G12 — Raw M4 evidence end-to-end through full M5 pipeline
# ---------------------------------------------------------------------------
def test_raw_m4_end_to_end_no_degradation():
    claim = {
        "claim_id": "c1",
        "text": SUPPORTED_CLAIM_TEXT,
        "claim_type": "patentability",
        "jurisdiction": "India",
    }
    payload = verify_claims_batch([claim], [RAW_M4_EVIDENCE], top_k=3, model=MODEL)
    row = payload["verification"][0]

    # No longer degrades into NO_EVIDENCE / empty text / abstain.
    assert row["status"] in (STATUS_SUPPORTED, STATUS_PARTIAL)
    assert "NO_EVIDENCE" not in row["flags"]
    assert row["best_evidence_id"] == "e1"
    assert row["best_evidence"]["text"] == RAW_M4_EVIDENCE["content"]
    assert row["best_evidence"]["document"] == "Example Indian Act"
    assert row["best_evidence"]["legal_domain"] == "Patent"
    assert row["best_evidence"]["authority"] == "Indian Patent Office"

    assert payload["confidence"]["score"] > 0.0
    assert payload["abstain"] is False
    assert payload["summary"]["total_claims"] == 1


def test_raw_m4_end_to_end_verified_citation_path():
    payload = verify_claims_batch(
        [{"id": "c1", "text": SUPPORTED_CLAIM_TEXT, "evidence_ids": ["e1"]}],
        [RAW_M4_EVIDENCE],
        top_k=3,
        model=MODEL,
    )
    row = payload["verification"][0]
    assert row["valid_citation_ids"] == ["e1"]
    assert row["unknown_citation_ids"] == []
    assert FLAG_UNKNOWN_CITATION_REFERENCE not in row["flags"]
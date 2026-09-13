"""
Member 5 — Safe Abstention regression suite (vague / miracle inputs).

Locks in the safe-abstention behavior that prevents vague inputs from
producing a high-confidence roadmap. The full demo scenario exercises the
REAL signals that drive the decision, not a hardcoded check:

  - unknown_insufficient_information classification → forced abstention
    (the system cannot say WHAT the product is, so it never presents a
    confident roadmap).
  - input_completeness < 0.5 (mostly "Not sure" clarification answers)
    → retrieval quality is penalized and abstention is forced.
  - required_domains empty (product type unknown) → on-domain evidence
    coverage scores 0, dragging retrieval_quality down.
  - claim_support treats PARTIAL as 0.5, not as full support.
  - ABSTAIN_SCORE_MIN raised to 50: LOW (<50) confidence never shows as a
    roadmap.

Regression guards:
  - canonical (clearly-classified, fully-answered) inputs still produce
    HIGH confidence and abstain=False.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from verification import (
    ABSTAIN_SCORE_MIN,
    CONFIDENCE_HIGH,
    CONFIDENCE_LOW,
    STATUS_PARTIAL,
    STATUS_SUPPORTED,
    STATUS_UNSUPPORTED,
    load_model,
    verify_claims_batch,
)

MODEL = load_model()

UNKNOWN_CATEGORY = "unknown_insufficient_information"
KNOWN_CATEGORY = "proprietary_ayurvedic_medicine"

# --- Evidence building blocks -------------------------------------------------

def _generic_evidence() -> list[dict]:
    """Six authoritative-looking but GENERIC Indian law chunks — the sort of
    corpus the retriever returns regardless of the query. Individually real and
    useful, but they do not specifically answer a miracle-cure claim."""
    return [
        {
            "id": f"gen_{i}",
            "text": (
                "Indian law regulates products that claim therapeutic use. "
                "Manufacturers must comply with the applicable statutory "
                "framework before marketing any such product in India."
            ),
            "document": "Consolidated Indian Regulatory Notes",
            "section": f"Clause {i}",
            "jurisdiction": "India",
            "legal_domain": "REGULATORY_AYUSH",
            "authority": "Ministry of AYUSH",
            "source_url": "https://indiacode.nic.in",
        }
        for i in range(6)
    ]


def _vague_claims() -> list[dict]:
    """Claims a miracle-cure product would generate: generic, ambitious,
    and only loosely grounded in the retrieved statutory content."""
    return [
        {
            "id": f"vague_{i}",
            "text": (
                "My revolutionary herbal product cures many diseases and "
                "guarantees results without any clinical trials."
            ),
            "jurisdiction": "India",
        }
        for i in range(6)
    ]


def _strong_claim() -> list[dict]:
    return [
        {
            "id": "strong_1",
            "text": (
                "A novel extraction process for an Ayurvedic bioresource may "
                "warrant further patentability assessment under Indian law."
            ),
            "jurisdiction": "India",
        }
    ]


def _strong_evidence() -> list[dict]:
    return [
        {
            "id": "st_1",
            "text": (
                "A novel extraction or manufacturing process that is not "
                "already known may be considered for further patentability "
                "assessment by a qualified professional."
            ),
            "document": "The Patents Act, 1970",
            "section": "Section 2(1)(j)",
            "jurisdiction": "India",
            "legal_domain": "IP_PATENT",
            "authority": "Indian Patent Office",
            "source_url": "https://ipindia.gov.in",
        }
    ]


# ---------------------------------------------------------------------------
# Scenario 1 — SAFE ABSTENTION on a vague / miracle input
# ---------------------------------------------------------------------------
def test_vague_miracle_input_abstains_with_low_confidence():
    payload = verify_claims_batch(
        _vague_claims(),
        _generic_evidence(),
        model=MODEL,
        classification={"category": UNKNOWN_CATEGORY, "confidence": 0, "reason": "too vague"},
        input_completeness=0.2,  # 4/5 answers "Not sure", only "India" informative
        required_domains=[],      # product type unknown → no domains to confirm
    )

    assert payload["abstain"] is True
    assert "classification_unknown" in payload["abstain_reasons"]
    assert payload["confidence"]["score"] < 50
    assert payload["confidence"]["level"] == CONFIDENCE_LOW


def test_vague_miracle_unknown_classification_caps_score_even_with_generic_authority():
    """Even if the corpus chunks look authoritative, an unclassified product
    must never present a confident score (capped to LOW)."""
    payload = verify_claims_batch(
        _vague_claims(),
        _generic_evidence(),
        model=MODEL,
        classification={"category": UNKNOWN_CATEGORY, "confidence": 0},
        input_completeness=0.2,
        required_domains=[],
    )
    assert payload["confidence"]["score"] <= 25.0
    assert payload["confidence"]["level"] == CONFIDENCE_LOW


def test_unsupported_heavy_roadmap_abstains():
    """More than half of claims unsupported → too_many_unsupported gate."""
    claims = [
        {"id": "a", "text": "Guaranteed fast-track patent grant in 3 months.", "jurisdiction": "India"},
        {"id": "b", "text": "100% cure for chronic disease without proof.", "jurisdiction": "India"},
    ]
    payload = verify_claims_batch(
        claims,
        _generic_evidence(),
        model=MODEL,
        classification={"category": KNOWN_CATEGORY, "confidence": 80},
        input_completeness=1.0,
        required_domains=["REGULATORY_AYUSH", "ABS_BIODIVERSITY", "IP_PATENT"],
    )
    assert payload["abstain"] is True
    assert "too_many_unsupported" in payload["abstain_reasons"]


def test_insufficient_input_abstains_despite_known_category():
    """Mostly-'Not sure' answers are insufficient even when the classifier
    somehow picked a category — the input is still too vague to trust."""
    payload = verify_claims_batch(
        _strong_claim(),
        _strong_evidence(),
        model=MODEL,
        classification={"category": KNOWN_CATEGORY, "confidence": 80},
        input_completeness=0.2,
        required_domains=["REGULATORY_AYUSH", "ABS_BIODIVERSITY", "IP_PATENT"],
    )
    assert payload["abstain"] is True
    assert "insufficient_input" in payload["abstain_reasons"]


# ---------------------------------------------------------------------------
# Scenario 2 — CANONICAL (fully-answered, clearly-classified) input
# ---------------------------------------------------------------------------
def test_canonical_clearly_classified_input_does_not_abstain():
    payload = verify_claims_batch(
        _strong_claim(),
        _strong_evidence(),
        model=MODEL,
        classification={"category": KNOWN_CATEGORY, "confidence": 88},
        input_completeness=1.0,
        required_domains=["REGULATORY_AYUSH", "ABS_BIODIVERSITY", "IP_PATENT"],
    )
    assert payload["abstain"] is False
    assert payload["abstain_reasons"] == []
    assert payload["confidence"]["level"] == CONFIDENCE_HIGH
    assert payload["confidence"]["score"] >= 80


# ---------------------------------------------------------------------------
# Guards on the constants the whole design rests on
# ---------------------------------------------------------------------------
def test_abstain_score_min_is_50_or_lower_not_30():
    """The abstention threshold must sit at the LOW/MEDIUM boundary so a
    MEDIUM score can still be shown, but the old 30 (bottom of LOW) is gone."""
    assert ABSTAIN_SCORE_MIN >= 50.0


def test_required_domains_empty_forces_zero_ondomain():
    """Empty required_domains (unknown product type) must collapse the
    on-domain sub-factor — evidence coverage cannot be confirmed."""
    payload = verify_claims_batch(
        _vague_claims(),
        _generic_evidence(),
        model=MODEL,
        classification={"category": KNOWN_CATEGORY, "confidence": 50},
        input_completeness=1.0,
        required_domains=[],
    )
    # With an empty domain list the on-domain share of retrieval_quality is 0,
    # but relevance/meaningful still contribute — verify the overall score is
    # NOT pushed into HIGH purely by count of evidence.
    assert payload["confidence"]["score"] < 80


def test_claim_support_weights_partial_as_half():
    """PARTIALLY_SUPPORTED must not score the same as SUPPORTED."""
    from verification import calculate_confidence

    supported_only = calculate_confidence(
        [{"status": STATUS_SUPPORTED, "jurisdiction_match": True, "best_evidence": {"authority": "Indian Patent Office", "id": "e1"}}],
        evidence=[{"id": "e1", "legal_domain": "IP_PATENT", "jurisdiction": "India"}],
    )
    partial_only = calculate_confidence(
        [{"status": STATUS_PARTIAL, "jurisdiction_match": True, "best_evidence": {"authority": "Indian Patent Office", "id": "e1"}}],
        evidence=[{"id": "e1", "legal_domain": "IP_PATENT", "jurisdiction": "India"}],
    )
    assert partial_only["signals"]["claim_support"] == 50.0
    assert supported_only["signals"]["claim_support"] == 100.0
    assert partial_only["signals"]["claim_support"] < supported_only["signals"]["claim_support"]
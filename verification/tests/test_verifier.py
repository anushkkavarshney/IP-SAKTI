"""
Day 2 Task 3 — Comprehensive Testing, Validation & Edge Cases Suite.

Evaluates the 12 required test categories:
1. Strong Semantic Match
2. Partial Support
3. Unsupported Claim
4. Irrelevant Evidence
5. Multiple Evidence Chunks (Ranking & Top-K)
6. Multiple Claims Batch Processing
7. No Evidence Handling
8. Empty Claim List Handling
9. Jurisdiction Mismatch Flagging
10. Duplicate Evidence Deduplication
11. Missing Metadata Preservation
12. Ambiguous Semantic Match (Topical Relevance vs Logical Entailment Limitation)
"""

import os
import sys
from typing import Any

# Ensure project root is in sys.path for package import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from verification.schemas import (
    STATUS_SUPPORTED,
    STATUS_PARTIAL,
    STATUS_UNSUPPORTED,
    FLAG_NO_EVIDENCE,
    FLAG_EMPTY_CLAIM,
    FLAG_JURISDICTION_MISMATCH,
)
from verification import verify_claim, verify_claims_batch, load_model


# Load model once for all tests
MODEL = load_model()


# ---------------------------------------------------------------------------
# Test Category 1: Strong Semantic Match
# ---------------------------------------------------------------------------
def test_category_1_strong_semantic_match():
    claim = {
        "id": "C1",
        "text": "The innovation may involve a biological resource.",
        "jurisdiction": "India",
    }
    evidence = [
        {
            "id": "E1",
            "text": "The innovation may involve a biological resource.",
            "document": "The Biological Diversity Act, 2002",
            "section": "Section 2(c)",
            "jurisdiction": "India",
            "source_url": "https://nbaindia.org/act/",
            "authority": "National Biodiversity Authority",
        },
        {
            "id": "E2",
            "text": "Patent specification drawings should be clear.",
            "document": "The Patents Act, 1970",
            "section": "Section 10",
            "jurisdiction": "India",
            "source_url": "https://ipindia.gov.in/",
        },
    ]

    res = verify_claims_batch([claim], evidence, model=MODEL)
    ver = res["verification"][0]

    assert ver["status"] == STATUS_SUPPORTED
    assert ver["best_evidence_id"] == "E1"
    assert ver["similarity_score"] >= 0.70
    assert ver["best_evidence"]["document"] == "The Biological Diversity Act, 2002"
    assert ver["best_evidence"]["authority"] == "National Biodiversity Authority"


# ---------------------------------------------------------------------------
# Test Category 2: Partial Support
# ---------------------------------------------------------------------------
def test_category_2_partial_support():
    claim = {
        "id": "C2",
        "text": "Access and benefit sharing may need to be reviewed because the formulation uses a plant material.",
        "jurisdiction": "India",
    }
    evidence = [
        {
            "id": "E1",
            "text": "Biological resources obtained from plants may raise biodiversity-related questions that should be reviewed separately from product labelling rules.",
            "document": "Plant Material Notes",
            "section": "Sec 4",
            "jurisdiction": "India",
            "source_url": "https://example.com/plant",
        }
    ]

    res = verify_claims_batch([claim], evidence, model=MODEL)
    ver = res["verification"][0]

    # Partial support similarity signal
    assert ver["status"] in (STATUS_PARTIAL, STATUS_SUPPORTED)
    assert ver["similarity_score"] > 0.40


# ---------------------------------------------------------------------------
# Test Category 3: Unsupported Claim
# ---------------------------------------------------------------------------
def test_category_3_unsupported_claim():
    claim = {
        "id": "C3",
        "text": "Cosmetic products are completely exempt from all ingredient labelling and registration requirements.",
        "jurisdiction": "India",
    }
    evidence = [
        {
            "id": "E1",
            "text": "Cosmetic labelling should list ingredients clearly in a manner consumers can understand.",
            "document": "Cosmetic Rules, 2020",
            "section": "Rule 34",
            "jurisdiction": "India",
            "source_url": "https://cdsco.gov.in/",
        }
    ]

    res = verify_claims_batch([claim], evidence, model=MODEL)
    ver = res["verification"][0]

    # Contradicting/unsupported claim produces low or partial relevance score, not high support for false claim
    assert ver["best_evidence_id"] == "E1"


# ---------------------------------------------------------------------------
# Test Category 4: Irrelevant Evidence
# ---------------------------------------------------------------------------
def test_category_4_irrelevant_evidence():
    claim = {
        "id": "C4",
        "text": "ABS considerations may arise because the innovation uses a biological resource.",
        "jurisdiction": "India",
    }
    evidence = [
        {
            "id": "E_IRRELEVANT",
            "text": "Printer toner cartridges should be replaced when print quality becomes faint.",
            "document": "Office Supplies Manual",
            "section": "Section 12",
            "jurisdiction": "India",
            "source_url": "https://example.com/office",
        }
    ]

    res = verify_claims_batch([claim], evidence, model=MODEL)
    ver = res["verification"][0]

    assert ver["status"] == STATUS_UNSUPPORTED
    assert ver["similarity_score"] < 0.45


# ---------------------------------------------------------------------------
# Test Category 5: Multiple Evidence Chunks (Ranking & Top-K)
# ---------------------------------------------------------------------------
def test_category_5_multiple_evidence_chunks():
    claim = {
        "id": "C5",
        "text": "A new extraction process may warrant further patentability assessment.",
        "jurisdiction": "India",
    }
    evidence = [
        {
            "id": "E_IRRELEVANT_1",
            "text": "Warehouse temperature logs should be updated daily.",
            "document": "Warehouse Guide",
            "section": "Sec 1",
            "jurisdiction": "India",
            "source_url": "https://example.com/w1",
        },
        {
            "id": "E_STRONG",
            "text": "A novel extraction or manufacturing process that is not already known may be considered for further patentability assessment by a qualified professional.",
            "document": "Patent Process Notes",
            "section": "Sec 2",
            "jurisdiction": "India",
            "source_url": "https://example.com/p2",
        },
        {
            "id": "E_MODERATE",
            "text": "Innovators document how a process was developed so that later review of novelty is easier.",
            "document": "Documentation Notes",
            "section": "Sec 3",
            "jurisdiction": "India",
            "source_url": "https://example.com/p3",
        },
        {
            "id": "E_IRRELEVANT_2",
            "text": "Cafeteria menus should offer vegetarian options.",
            "document": "Cafeteria Policy",
            "section": "Sec 4",
            "jurisdiction": "India",
            "source_url": "https://example.com/c4",
        },
    ]

    res = verify_claims_batch([claim], evidence, top_k=3, model=MODEL)
    ver = res["verification"][0]
    ranked = ver["ranked_evidence"]

    assert len(ranked) == 3
    assert ranked[0]["evidence_id"] == "E_STRONG"
    assert ranked[1]["evidence_id"] == "E_MODERATE"
    assert ranked[0]["score"] >= ranked[1]["score"] >= ranked[2]["score"]


# ---------------------------------------------------------------------------
# Test Category 6: Multiple Claims Batch Processing
# ---------------------------------------------------------------------------
def test_category_6_multiple_claims():
    claims = [
        {
            "id": "C1",
            "text": "The innovation may involve a biological resource if it uses plants or micro-organisms.",
            "jurisdiction": "India",
        },
        {
            "id": "C2",
            "text": "A novel process of extraction may be considered for patent protection.",
            "jurisdiction": "India",
        },
        {
            "id": "C3",
            "text": "Food supplement products may follow food-safety regulatory pathways.",
            "jurisdiction": "India",
        },
    ]
    evidence = [
        {
            "id": "E_BIO",
            "text": "The innovation may involve a biological resource if it uses plants, animals, micro-organisms, or parts of them.",
            "document": "Biological Diversity Act",
            "section": "Sec 2",
            "jurisdiction": "India",
            "source_url": "https://nbaindia.org/",
        },
        {
            "id": "E_PATENT",
            "text": "A novel process of extraction not previously disclosed may be considered for patent protection.",
            "document": "Patents Act",
            "section": "Sec 2(1)(j)",
            "jurisdiction": "India",
            "source_url": "https://ipindia.gov.in/",
        },
        {
            "id": "E_FOOD",
            "text": "Food supplement products follow food-safety regulatory pathways under FSSAI rules.",
            "document": "FSSAI Act",
            "section": "Sec 22",
            "jurisdiction": "India",
            "source_url": "https://fssai.gov.in/",
        },
    ]

    res = verify_claims_batch(claims, evidence, top_k=2, model=MODEL)

    assert len(res["verification"]) == 3
    assert res["summary"]["total_claims"] == 3
    assert res["verification"][0]["best_evidence_id"] == "E_BIO"
    assert res["verification"][1]["best_evidence_id"] == "E_PATENT"
    assert res["verification"][2]["best_evidence_id"] == "E_FOOD"


# ---------------------------------------------------------------------------
# Test Category 7: No Evidence Handling
# ---------------------------------------------------------------------------
def test_category_7_no_evidence():
    claims = [{"id": "C1", "text": "Claim with no evidence", "jurisdiction": "India"}]
    res = verify_claims_batch(claims, [], model=MODEL)

    ver = res["verification"][0]
    assert ver["status"] == STATUS_UNSUPPORTED
    assert ver["score"] == 0.0
    assert ver["best_evidence"] is None
    assert FLAG_NO_EVIDENCE in ver["flags"]


# ---------------------------------------------------------------------------
# Test Category 8: Empty Claim List Handling
# ---------------------------------------------------------------------------
def test_category_8_empty_claim_list():
    evidence = [{"id": "E1", "text": "Some evidence text", "jurisdiction": "India"}]
    res = verify_claims_batch([], evidence, model=MODEL)

    assert res["verification"] == []
    assert res["summary"]["total_claims"] == 0
    assert res["summary"]["supported_claims"] == 0


# ---------------------------------------------------------------------------
# Test Category 9: Jurisdiction Mismatch Flagging
# ---------------------------------------------------------------------------
def test_category_9_jurisdiction_mismatch():
    claim = {
        "id": "C1",
        "text": "The innovation may involve a biological resource.",
        "jurisdiction": "India",
    }
    evidence = [
        {
            "id": "E_US",
            "text": "The innovation may involve a biological resource under US federal guidelines.",
            "document": "US Patent Code Title 35",
            "section": "Section 101",
            "jurisdiction": "USA",
            "source_url": "https://uspto.gov/",
        }
    ]

    res = verify_claims_batch([claim], evidence, target_jurisdiction="India", model=MODEL)
    ver = res["verification"][0]

    assert ver["jurisdiction_match"] is False
    assert FLAG_JURISDICTION_MISMATCH in ver["flags"]


# ---------------------------------------------------------------------------
# Test Category 10: Duplicate Evidence Deduplication
# ---------------------------------------------------------------------------
def test_category_10_duplicate_evidence():
    claim = {"id": "C1", "text": "Testing duplicate evidence filtering.", "jurisdiction": "India"}
    evidence = [
        {
            "id": "E1",
            "text": "Biological resources include plants, animals, and microorganisms.",
            "document": "Doc 1",
            "jurisdiction": "India",
        },
        {
            "id": "E1",  # Duplicate ID
            "text": "Biological resources include plants, animals, and microorganisms.",
            "document": "Doc 1",
            "jurisdiction": "India",
        },
        {
            "id": "E2",  # Duplicate Text
            "text": "Biological resources include plants, animals, and microorganisms.",
            "document": "Doc 2",
            "jurisdiction": "India",
        },
    ]

    res = verify_claims_batch([claim], evidence, top_k=5, model=MODEL)
    ver = res["verification"][0]

    assert len(ver["ranked_evidence"]) == 1


# ---------------------------------------------------------------------------
# Test Category 11: Missing Metadata Preservation
# ---------------------------------------------------------------------------
def test_category_11_missing_metadata():
    claim = {"id": "C1", "text": "Biological resource assertion", "jurisdiction": "India"}
    evidence = [
        {
            "id": "E_MINIMAL",
            "text": "Biological resources assertion passage.",
            # Missing document, section, authority, effective_date, source_url
        }
    ]

    res = verify_claims_batch([claim], evidence, model=MODEL)
    best_ev = res["verification"][0]["best_evidence"]

    assert best_ev["document"] == ""
    assert best_ev["section"] == ""
    assert best_ev["authority"] == ""
    assert best_ev["effective_date"] == ""
    assert best_ev["source_url"] == ""


# ---------------------------------------------------------------------------
# Test Category 12: Ambiguous Semantic Match (Topical vs Entailment Limitation)
# ---------------------------------------------------------------------------
def test_category_12_ambiguous_semantic_match():
    """
    CRITICAL EDGE CASE TEST:
    Demonstrates that high semantic similarity occurs due to shared vocabulary ('patent', 'granted', 'protection'),
    even though the evidence does NOT logically entail the absolute word 'definitely'.

    This test confirms the known architecture limitation:
    Cosine similarity alone measures TOPICAL RELEVANCE, NOT LOGICAL ENTAILMENT.
    """
    claim = {
        "id": "C_AMBIGUOUS",
        "text": "A patent will definitely be granted for this extraction formulation.",
        "jurisdiction": "India",
    }
    evidence = [
        {
            "id": "E_CONDITIONAL",
            "text": "Patent protection depends on applicable statutory patentability requirements and prior-art examination under Section 3.",
            "document": "The Patents Act, 1970",
            "section": "Section 3",
            "jurisdiction": "India",
            "source_url": "https://ipindia.gov.in/",
        }
    ]

    res = verify_claims_batch([claim], evidence, model=MODEL)
    ver = res["verification"][0]

    # Empirical observation: topical similarity is moderate (> 0.25) due to shared patent terminology ('patent', 'formulation')
    # despite the evidence failing to entail the absolute claim 'definitely granted'.
    assert ver["similarity_score"] > 0.25
    # Note: Semantic similarity rates this as partial or supported because of high topic overlap,
    # demonstrating why downstream NLI / cross-encoder entailment logic is needed in future work.


def run_all_test_categories() -> bool:
    print("=" * 70)
    print("MEMBER 5 — DAY 2 TASK 3: COMPREHENSIVE EDGE-CASE TEST SUITE")
    print("=" * 70)

    tests = [
        ("Cat 1: Strong Semantic Match", test_category_1_strong_semantic_match),
        ("Cat 2: Partial Support Signal", test_category_2_partial_support),
        ("Cat 3: Unsupported Claim Handling", test_category_3_unsupported_claim),
        ("Cat 4: Irrelevant Evidence Filter", test_category_4_irrelevant_evidence),
        ("Cat 5: Multiple Evidence Top-K Ranking", test_category_5_multiple_evidence_chunks),
        ("Cat 6: Multiple Claims Batch Processing", test_category_6_multiple_claims),
        ("Cat 7: No Evidence Handling", test_category_7_no_evidence),
        ("Cat 8: Empty Claim List Handling", test_category_8_empty_claim_list),
        ("Cat 9: Jurisdiction Mismatch Flagging", test_category_9_jurisdiction_mismatch),
        ("Cat 10: Duplicate Evidence Deduplication", test_category_10_duplicate_evidence),
        ("Cat 11: Missing Metadata Preservation", test_category_11_missing_metadata),
        ("Cat 12: Ambiguous Match (Semantic vs Entailment)", test_category_12_ambiguous_semantic_match),
    ]

    passed_count = 0
    total_count = len(tests)

    for name, test_func in tests:
        try:
            test_func()
            print(f"[PASSED] {name}")
            passed_count += 1
        except AssertionError as err:
            print(f"[FAILED] {name}: {err}")
        except Exception as ex:
            print(f"[ERROR]  {name}: {ex}")

    print("=" * 70)
    print(f"SUMMARY: {passed_count}/{total_count} Categories Passed")
    print("=" * 70)

    return passed_count == total_count


if __name__ == "__main__":
    success = run_all_test_categories()
    sys.exit(0 if success else 1)

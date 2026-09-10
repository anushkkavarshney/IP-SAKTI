"""
Day 2 Task 2 — Batch Claim Verification Engine Test Suite.

Verifies:
1. Single claim + multiple evidence items
2. Multiple claims + multiple evidence items
3. Empty claims handling
4. Empty evidence handling
5. Irrelevant evidence (low similarity)
6. India claim + India evidence matching
7. India claim + non-India evidence jurisdiction mismatch flag
8. Duplicate evidence deduplication
9. Preservation of missing metadata (no fabricated fields)
10. Configurable Top-K parameter support
"""

import json
from typing import Any

from verification import verify_claims_batch
from verification.schemas import (
    STATUS_SUPPORTED,
    STATUS_PARTIAL,
    STATUS_UNSUPPORTED,
    FLAG_NO_EVIDENCE,
    FLAG_EMPTY_CLAIM,
    FLAG_JURISDICTION_MISMATCH,
)


def run_batch_tests() -> bool:
    print("=" * 60)
    print("MEMBER 5 — DAY 2 TASK 2: BATCH VERIFICATION TEST SUITE")
    print("=" * 60)
    all_passed = True

    # -------------------------------------------------------------
    # Scenario 1: Single claim + multiple evidence items
    # -------------------------------------------------------------
    print("\n--- Test 1: Single claim + multiple evidence items ---")
    claims_1 = [
        {
            "id": "C1",
            "text": "The innovation may involve a biological resource.",
            "jurisdiction": "India",
        }
    ]
    evidence_1 = [
        {
            "id": "E1",
            "text": "The innovation may involve a biological resource if it uses plants, animals, microorganisms, or parts of them.",
            "document": "The Biological Diversity Act, 2002",
            "section": "Section 2(c)",
            "jurisdiction": "India",
            "source_url": "https://nbaindia.org/act/",
        },
        {
            "id": "E2",
            "text": "Patent claims must define the scope of protection clearly.",
            "document": "The Patents Act, 1970",
            "section": "Section 10",
            "jurisdiction": "India",
            "source_url": "https://ipindia.gov.in/",
        },
    ]

    res_1 = verify_claims_batch(claims_1, evidence_1, top_k=2)
    ver_1 = res_1["verification"][0]
    pass_1 = ver_1["status"] == STATUS_SUPPORTED and ver_1["best_evidence_id"] == "E1"
    print(f"Status: {ver_1['status']} (Expected: {STATUS_SUPPORTED})")
    print(f"Best Evidence ID: {ver_1['best_evidence_id']} (Expected: E1)")
    print(f"Top-K count: {len(ver_1['ranked_evidence'])} (Expected: 2)")
    print(f"Result: {'PASSED' if pass_1 else 'FAILED'}")
    if not pass_1:
        all_passed = False

    # -------------------------------------------------------------
    # Scenario 2: Multiple claims + multiple evidence items
    # -------------------------------------------------------------
    print("\n--- Test 2: Multiple claims + multiple evidence items ---")
    claims_2 = [
        {
            "id": "C1",
            "text": "The formulation uses Ashwagandha root extract as a biological resource.",
            "jurisdiction": "India",
        },
        {
            "id": "C2",
            "text": "A new solvent extraction process may warrant patentability review.",
            "jurisdiction": "India",
        },
    ]
    evidence_2 = [
        {
            "id": "E1",
            "text": "Extraction of plant material from biological species requires ABS compliance.",
            "document": "The Biological Diversity Act, 2002",
            "section": "Section 3",
            "jurisdiction": "India",
            "source_url": "https://nbaindia.org/",
        },
        {
            "id": "E2",
            "text": "A novel process of extraction not previously disclosed may be considered for patent protection.",
            "document": "The Patents Act, 1970",
            "section": "Section 2(1)(j)",
            "jurisdiction": "India",
            "source_url": "https://ipindia.gov.in/",
        },
    ]

    res_2 = verify_claims_batch(claims_2, evidence_2, top_k=2)
    pass_2 = (
        len(res_2["verification"]) == 2
        and res_2["verification"][0]["best_evidence_id"] == "E1"
        and res_2["verification"][1]["best_evidence_id"] == "E2"
    )
    print(f"Claim 1 Best Evidence: {res_2['verification'][0]['best_evidence_id']} (Expected: E1)")
    print(f"Claim 2 Best Evidence: {res_2['verification'][1]['best_evidence_id']} (Expected: E2)")
    print(f"Result: {'PASSED' if pass_2 else 'FAILED'}")
    if not pass_2:
        all_passed = False

    # -------------------------------------------------------------
    # Scenario 3: Empty claims handling
    # -------------------------------------------------------------
    print("\n--- Test 3: Empty claims list handling ---")
    res_3 = verify_claims_batch([], evidence_2)
    pass_3 = res_3["verification"] == [] and res_3["summary"]["total_claims"] == 0
    print(f"Verification items: {len(res_3['verification'])} (Expected: 0)")
    print(f"Result: {'PASSED' if pass_3 else 'FAILED'}")
    if not pass_3:
        all_passed = False

    # -------------------------------------------------------------
    # Scenario 4: Empty evidence handling
    # -------------------------------------------------------------
    print("\n--- Test 4: Empty evidence list handling ---")
    res_4 = verify_claims_batch(claims_1, [])
    ver_4 = res_4["verification"][0]
    pass_4 = ver_4["status"] == STATUS_UNSUPPORTED and FLAG_NO_EVIDENCE in ver_4["flags"]
    print(f"Status: {ver_4['status']} (Expected: {STATUS_UNSUPPORTED})")
    print(f"Flags: {ver_4['flags']} (Expected: contains '{FLAG_NO_EVIDENCE}')")
    print(f"Result: {'PASSED' if pass_4 else 'FAILED'}")
    if not pass_4:
        all_passed = False

    # -------------------------------------------------------------
    # Scenario 5: Irrelevant evidence (low similarity)
    # -------------------------------------------------------------
    print("\n--- Test 5: Irrelevant evidence (low similarity) ---")
    evidence_5 = [
        {
            "id": "E_IRRELEVANT",
            "text": "Office air conditioning filters should be cleaned monthly during summer.",
            "document": "Building Maintenance Guide",
            "section": "Clause 4.1",
            "jurisdiction": "India",
            "source_url": "https://example.com/building",
        }
    ]
    res_5 = verify_claims_batch(claims_1, evidence_5)
    ver_5 = res_5["verification"][0]
    pass_5 = ver_5["status"] == STATUS_UNSUPPORTED and ver_5["score"] < 0.45
    print(f"Status: {ver_5['status']} (Expected: {STATUS_UNSUPPORTED})")
    print(f"Similarity Score: {ver_5['score']:.4f} (Expected: < 0.45)")
    print(f"Result: {'PASSED' if pass_5 else 'FAILED'}")
    if not pass_5:
        all_passed = False

    # -------------------------------------------------------------
    # Scenario 6: India claim + India evidence matching
    # -------------------------------------------------------------
    print("\n--- Test 6: India claim + India evidence matching ---")
    res_6 = verify_claims_batch(claims_1, evidence_1, target_jurisdiction="India")
    ver_6 = res_6["verification"][0]
    pass_6 = ver_6["jurisdiction_match"] is True and FLAG_JURISDICTION_MISMATCH not in ver_6["flags"]
    print(f"Jurisdiction Match: {ver_6['jurisdiction_match']} (Expected: True)")
    print(f"Flags: {ver_6['flags']} (Expected: empty list)")
    print(f"Result: {'PASSED' if pass_6 else 'FAILED'}")
    if not pass_6:
        all_passed = False

    # -------------------------------------------------------------
    # Scenario 7: India claim + non-India evidence (jurisdiction mismatch flag)
    # -------------------------------------------------------------
    print("\n--- Test 7: India claim + non-India evidence (jurisdiction mismatch flag) ---")
    evidence_7 = [
        {
            "id": "E_US",
            "text": "The innovation may involve a biological resource if it uses plants, animals, or microorganisms.",
            "document": "US Patent Code Title 35",
            "section": "Section 101",
            "jurisdiction": "USA",
            "source_url": "https://uspto.gov/",
        }
    ]
    res_7 = verify_claims_batch(claims_1, evidence_7, target_jurisdiction="India")
    ver_7 = res_7["verification"][0]
    pass_7 = ver_7["jurisdiction_match"] is False and FLAG_JURISDICTION_MISMATCH in ver_7["flags"]
    print(f"Jurisdiction Match: {ver_7['jurisdiction_match']} (Expected: False)")
    print(f"Flags: {ver_7['flags']} (Expected: contains '{FLAG_JURISDICTION_MISMATCH}')")
    print(f"Result: {'PASSED' if pass_7 else 'FAILED'}")
    if not pass_7:
        all_passed = False

    # -------------------------------------------------------------
    # Scenario 8: Duplicate evidence deduplication
    # -------------------------------------------------------------
    print("\n--- Test 8: Duplicate evidence deduplication ---")
    evidence_8 = [
        evidence_1[0],
        evidence_1[0],  # Exact duplicate object
        {
            "id": "E1_DUP",
            "text": evidence_1[0]["text"],  # Duplicate text content
            "document": "Duplicate Doc",
            "section": "Sec 1",
            "jurisdiction": "India",
            "source_url": "https://example.com/dup",
        },
    ]
    res_8 = verify_claims_batch(claims_1, evidence_8, top_k=5)
    ver_8 = res_8["verification"][0]
    pass_8 = len(ver_8["ranked_evidence"]) == 1
    print(f"Ranked Evidence Count: {len(ver_8['ranked_evidence'])} (Expected: 1 after deduplication)")
    print(f"Result: {'PASSED' if pass_8 else 'FAILED'}")
    if not pass_8:
        all_passed = False

    # -------------------------------------------------------------
    # Scenario 9: Missing metadata preservation
    # -------------------------------------------------------------
    print("\n--- Test 9: Missing metadata preservation (no fabricated fields) ---")
    evidence_9 = [
        {
            "id": "E_MINIMAL",
            "text": "The innovation may involve a biological resource.",
            # Omit document, section, authority, source_url
        }
    ]
    res_9 = verify_claims_batch(claims_1, evidence_9)
    best_ev_9 = res_9["verification"][0]["best_evidence"]
    pass_9 = (
        best_ev_9.get("authority") == ""
        and best_ev_9.get("section") == ""
        and best_ev_9.get("effective_date") == ""
    )
    print(f"Authority: '{best_ev_9.get('authority')}' (Expected: '')")
    print(f"Section: '{best_ev_9.get('section')}' (Expected: '')")
    print(f"Result: {'PASSED' if pass_9 else 'FAILED'}")
    if not pass_9:
        all_passed = False

    # -------------------------------------------------------------
    # Scenario 10: Configurable Top-K parameter
    # -------------------------------------------------------------
    print("\n--- Test 10: Configurable Top-K parameter ---")
    evidence_10 = [
        {
            "id": f"E_{i}",
            "text": f"Biological resources statement variant {i} for innovation testing.",
            "document": f"Doc {i}",
            "section": f"Section {i}",
            "jurisdiction": "India",
            "source_url": f"https://example.com/{i}",
        }
        for i in range(1, 6)
    ]
    res_10_k2 = verify_claims_batch(claims_1, evidence_10, top_k=2)
    res_10_k4 = verify_claims_batch(claims_1, evidence_10, top_k=4)
    count_k2 = len(res_10_k2["verification"][0]["ranked_evidence"])
    count_k4 = len(res_10_k4["verification"][0]["ranked_evidence"])
    pass_10 = count_k2 == 2 and count_k4 == 4
    print(f"Top-K=2 returned items: {count_k2} (Expected: 2)")
    print(f"Top-K=4 returned items: {count_k4} (Expected: 4)")
    print(f"Result: {'PASSED' if pass_10 else 'FAILED'}")
    if not pass_10:
        all_passed = False

    # -------------------------------------------------------------
    # Overall Test Summary
    # -------------------------------------------------------------
    print("\n" + "=" * 60)
    print("BATCH TEST SUITE SUMMARY")
    print("=" * 60)
    print(f"All 10 Scenarios Passed: {'YES' if all_passed else 'NO'}")
    print("Note: This test suite evaluates batch verification functionality.")
    print("Similarity scores are semantic relevance signals, not legal proof.")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    import sys
    success = run_batch_tests()
    sys.exit(0 if success else 1)

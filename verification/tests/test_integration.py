"""
Day 2 Task 4 — Importability & Integration Test.

Verifies that Member 5's public entry point `verify_claims` can be imported
and executed seamlessly as a Python package from external modules.
"""

import os
import sys

# Ensure project root is in sys.path for package import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from verification import verify_claims, verify_claims_batch
from verification.schemas import (
    STATUS_SUPPORTED,
    STATUS_UNSUPPORTED,
    DEFAULT_JURISDICTION,
    SAFETY_NOTE,
)


def test_public_package_imports():
    """Verify that verify_claims entry point is importable and functional."""
    claims = [
        {
            "id": "C_TEST",
            "text": "The innovation may involve a biological resource.",
            "jurisdiction": DEFAULT_JURISDICTION,
        }
    ]
    evidence = [
        {
            "id": "E_TEST",
            "text": "The innovation may involve a biological resource if it uses plants, animals, microorganisms, or parts of them.",
            "document": "The Biological Diversity Act, 2002",
            "section": "Section 2(c)",
            "jurisdiction": DEFAULT_JURISDICTION,
            "source_url": "https://nbaindia.org/act/",
        }
    ]

    # Test verify_claims alias
    res1 = verify_claims(claims, evidence, top_k=1)
    assert "verification" in res1
    assert "summary" in res1
    assert res1["support_type"] == "preliminary_semantic_support"
    assert res1["note"] == SAFETY_NOTE
    assert res1["verification"][0]["status"] == STATUS_SUPPORTED
    assert res1["verification"][0]["best_evidence_id"] == "E_TEST"

    # Test verify_claims_batch function
    res2 = verify_claims_batch(claims, evidence, top_k=1)
    assert res1 == res2


def test_deterministic_output():
    """Verify that identical inputs produce identical ranking and scores."""
    claims = [{"id": "C1", "text": "A new extraction process may warrant patentability assessment."}]
    evidence = [
        {
            "id": "E1",
            "text": "A novel extraction or manufacturing process that is not already known may be considered for further patentability assessment.",
            "document": "Patent Process Notes",
        },
        {
            "id": "E2",
            "text": "Warehouse temperature logs should be updated daily.",
            "document": "Warehouse Guide",
        },
    ]

    run1 = verify_claims(claims, evidence)
    run2 = verify_claims(claims, evidence)

    assert run1 == run2
    assert run1["verification"][0]["score"] == run2["verification"][0]["score"]
    assert run1["verification"][0]["best_evidence_id"] == run2["verification"][0]["best_evidence_id"]


if __name__ == "__main__":
    test_public_package_imports()
    test_deterministic_output()
    print("Integration & Importability Tests Passed Successfully!")

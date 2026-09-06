"""
IP-SAKTI Navigator — Member 5 — Day 1 claim verifier.

Day 1 pipeline:
    claim
      → embedding
      → cosine similarity vs each evidence embedding
      → rank evidence
      → best evidence
      → preliminary semantic support status

This is a first-stage RELEVANCE signal only.
It does NOT prove that a claim is legally true, valid, or verified.
Thresholds below are starting points for a synthetic demo, not validated legal cutoffs.

Compatible with later Member 4 evidence that may use `source` or `source_url`.
"""

from __future__ import annotations

import json
from typing import Any

from sentence_transformers import SentenceTransformer, util

from test_cases import TEST_CASES

# Lightweight MVP model: fast, small, good enough for semantic matching.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Starting thresholds for THIS synthetic dataset. Tune later with real evaluation data.
# Do not treat these numbers as scientifically or legally validated.
SUPPORTED_MIN = 0.70
PARTIALLY_SUPPORTED_MIN = 0.45

STATUS_SUPPORTED = "SUPPORTED"
STATUS_PARTIAL = "PARTIALLY_SUPPORTED"
STATUS_UNSUPPORTED = "UNSUPPORTED"

_model: SentenceTransformer | None = None


def load_model() -> SentenceTransformer:
    """Load the Sentence Transformer once and reuse it."""
    global _model
    if _model is None:
        print(f"Loading model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_text(text: str, model: SentenceTransformer | None = None):
    """Turn one string into a numeric embedding vector."""
    model = model or load_model()
    return model.encode(text, convert_to_tensor=True)


def embed_texts(texts: list[str], model: SentenceTransformer | None = None):
    """Turn many strings into embedding vectors."""
    model = model or load_model()
    return model.encode(texts, convert_to_tensor=True)


def calculate_similarity(claim_embedding, evidence_embedding) -> float:
    """
    Cosine similarity: 1.0 means almost the same meaning,
    values near 0 mean little semantic overlap.
    This is NOT a legal-proof score.
    """
    score = util.cos_sim(claim_embedding, evidence_embedding)
    return float(score.item())


def classify_similarity(score: float) -> str:
    """Map a similarity score to a PRELIMINARY semantic support label."""
    if score >= SUPPORTED_MIN:
        return STATUS_SUPPORTED
    if score >= PARTIALLY_SUPPORTED_MIN:
        return STATUS_PARTIAL
    return STATUS_UNSUPPORTED


def _evidence_text(item: dict[str, Any]) -> str:
    return (item.get("text") or "").strip()


def rank_evidence(claim: str, evidence: list[dict[str, Any]], model: SentenceTransformer | None = None) -> list[dict[str, Any]]:
    """Compare the claim with every evidence passage and sort highest similarity first."""
    model = model or load_model()
    claim_emb = embed_text(claim, model=model)
    ranked: list[dict[str, Any]] = []

    for item in evidence:
        text = _evidence_text(item)
        if not text:
            score = 0.0
        else:
            score = calculate_similarity(claim_emb, embed_text(text, model=model))
        ranked.append({"score": round(score, 4), "evidence": item})

    ranked.sort(key=lambda row: row["score"], reverse=True)
    return ranked


def verify_claim(claim: str, evidence: list[dict[str, Any]], model: SentenceTransformer | None = None) -> dict[str, Any]:
    """
    Return structured JSON for one claim + evidence list.

    `status` means preliminary semantic support, not legal verification.
    """
    if not claim.strip():
        return {
            "claim": claim,
            "status": STATUS_UNSUPPORTED,
            "similarity_score": 0.0,
            "support_type": "preliminary_semantic_support",
            "note": "Empty claim. Semantic matching was not performed.",
            "best_evidence": None,
            "ranked_evidence": [],
        }

    if not evidence:
        return {
            "claim": claim,
            "status": STATUS_UNSUPPORTED,
            "similarity_score": 0.0,
            "support_type": "preliminary_semantic_support",
            "note": "No evidence was provided. Semantic matching was not performed.",
            "best_evidence": None,
            "ranked_evidence": [],
        }

    ranked = rank_evidence(claim, evidence, model=model)
    best = ranked[0]
    best_score = best["score"]
    status = classify_similarity(best_score)

    return {
        "claim": claim,
        "status": status,
        "similarity_score": best_score,
        "support_type": "preliminary_semantic_support",
        "note": (
            "Similarity is a first-stage relevance signal only. "
            "It does not establish legal validity or legal proof."
        ),
        "best_evidence": best["evidence"],
        "ranked_evidence": [
            {
                "score": row["score"],
                "document": row["evidence"].get("document", ""),
                "section": row["evidence"].get("section", ""),
                "jurisdiction": row["evidence"].get("jurisdiction", ""),
                "source": row["evidence"].get("source")
                or row["evidence"].get("source_url", ""),
            }
            for row in ranked
        ],
    }


def _print_result(index: int, total: int, case: dict[str, Any], result: dict[str, Any], passed: bool) -> None:
    best = result.get("best_evidence") or {}
    best_text = (best.get("text") or "None")[:180]
    print("=" * 40)
    print("CLAIM VERIFICATION - DAY 1")
    print("=" * 40)
    print(f"Test {index}/{total}: {case.get('id', '')}")
    print()
    print(f"Claim: {result['claim']}")
    print()
    print(f"Best Evidence: {best_text}")
    print()
    print(f"Similarity Score: {result['similarity_score']:.2f}")
    print()
    print(f"Preliminary Status: {result['status']}")
    print(f"Expected Status: {case['expected'].upper()}")
    print(f"Match: {'PASSED' if passed else 'FAILED'}")
    print()
    print("Ranked evidence:")
    for row in result.get("ranked_evidence", []):
        print(f"  {row['score']:.2f}  {row['document']}")
    print("=" * 40)
    print()


def run_tests() -> dict[str, Any]:
    """Run synthetic test cases. Pass/fail is NOT legal accuracy."""
    model = load_model()
    total = len(TEST_CASES)
    passed = 0
    details = []

    print()
    print("=" * 40)
    print("CLAIM VERIFICATION - DAY 1")
    print("=" * 40)
    print("Evidence in these tests is SYNTHETIC DEMO TEXT.")
    print("Pass/fail only checks semantic labels on this demo set.")
    print("It is not legal accuracy.")
    print()

    for i, case in enumerate(TEST_CASES, start=1):
        result = verify_claim(case["claim"], case["evidence"], model=model)
        predicted = result["status"].lower()
        expected = case["expected"].lower()
        is_pass = predicted == expected
        if is_pass:
            passed += 1
        details.append(
            {
                "id": case.get("id"),
                "expected": expected,
                "predicted": predicted,
                "score": result["similarity_score"],
                "passed": is_pass,
            }
        )
        _print_result(i, total, case, result, is_pass)

    failed = total - passed
    summary = {
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "evaluation_note": (
            "This summary evaluates synthetic semantic test cases only. "
            "It does not represent legal accuracy."
        ),
        "details": details,
    }

    print("TEST SUMMARY")
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()
    print(summary["evaluation_note"])
    print()
    print("JSON summary:")
    print(json.dumps({k: summary[k] for k in ("total_tests", "passed", "failed", "evaluation_note")}, indent=2))
    return summary


if __name__ == "__main__":
    run_tests()

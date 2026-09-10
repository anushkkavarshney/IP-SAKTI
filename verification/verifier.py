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

from .schemas import (
    FLAG_EMPTY_CLAIM,
    FLAG_NO_EVIDENCE,
    FLAG_JURISDICTION_MISMATCH,
    SAFETY_NOTE,
    build_claim_result,
    empty_claim_result,
    normalize_claim,
    normalize_claims_payload,
    normalize_evidence_payload,
    wrap_verification_payload,
)
from .test_cases import TEST_CASES

# Lightweight MVP model: fast, small, good enough for semantic matching.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Starting thresholds for THIS synthetic dataset. Tune later with real evaluation data.
# Do not treat these numbers as scientifically or legally validated.
SUPPORTED_MIN = 0.70
PARTIALLY_SUPPORTED_MIN = 0.45
DEFAULT_TOP_K = 3

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
    normalized = normalize_evidence_payload(evidence)["evidence"]
    ranked: list[dict[str, Any]] = []

    for item in normalized:
        text = _evidence_text(item)
        if not text:
            score = 0.0
        else:
            score = calculate_similarity(claim_emb, embed_text(text, model=model))
        ranked.append({"score": round(score, 4), "evidence": item})

    ranked.sort(key=lambda row: row["score"], reverse=True)
    return ranked


def deduplicate_evidence(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Remove duplicate evidence items by ID or identical text while preserving metadata.
    Keep the first occurrence of each item.
    """
    seen_ids: set[str] = set()
    seen_texts: set[str] = set()
    deduped: list[dict[str, Any]] = []

    for item in evidence:
        item_id = str(item.get("id") or item.get("evidence_id") or "").strip()
        text = str(item.get("text") or "").strip().casefold()

        if item_id and item_id in seen_ids:
            continue
        if text and text in seen_texts:
            continue

        if item_id:
            seen_ids.add(item_id)
        if text:
            seen_texts.add(text)
        deduped.append(item)

    return deduped


def verify_claim(
    claim: str | dict[str, Any],
    evidence: list[dict[str, Any]],
    model: SentenceTransformer | None = None,
    top_k: int | None = None,
) -> dict[str, Any]:
    """
    Return structured JSON for one claim + evidence list.

    `status` means preliminary semantic support, not legal verification.
    Accepts a Day 1 claim string or an M3 claim object.
    """
    normalized_claim = normalize_claim(claim)

    if not normalized_claim["text"]:
        return empty_claim_result(
            normalized_claim,
            FLAG_EMPTY_CLAIM,
            "Empty claim. Semantic matching was not performed.",
        )

    if not evidence:
        return empty_claim_result(
            normalized_claim,
            FLAG_NO_EVIDENCE,
            "No evidence was provided. Semantic matching was not performed.",
        )

    ranked = rank_evidence(normalized_claim["text"], evidence, model=model)
    if top_k is not None and top_k > 0:
        ranked = ranked[:top_k]

    best_score = ranked[0]["score"] if ranked else 0.0
    status = classify_similarity(best_score)
    return build_claim_result(normalized_claim, status, best_score, ranked, note=SAFETY_NOTE)


def verify_claims_batch(
    claims: dict[str, Any] | list,
    evidence: dict[str, Any] | list,
    *,
    top_k: int = 3,
    target_jurisdiction: str = "India",
    model: SentenceTransformer | None = None,
) -> dict[str, Any]:
    """
    Day 2 Task 2 — Batch Claim Verification Engine.

    Accepts multiple claims (M3 claims payload or list) and multiple legal evidence items
    (M4 evidence payload or list). Computes similarity vectors, ranks top-K evidence items per claim,
    evaluates jurisdiction alignment, and returns structured verification results.

    `status` signifies preliminary semantic support signal only, NOT legal proof or validation.
    """
    model = model or load_model()

    normalized_claims_payload = normalize_claims_payload(claims)
    normalized_evidence_payload = normalize_evidence_payload(evidence)

    claims_list = normalized_claims_payload["claims"]
    raw_evidence_list = normalized_evidence_payload["evidence"]

    # Edge Case 1: No claims provided
    if not claims_list:
        return wrap_verification_payload([])

    # Edge Case 5: Deduplicate evidence items before embedding
    deduped_evidence = deduplicate_evidence(raw_evidence_list)

    # Edge Case 2: No evidence provided
    if not deduped_evidence:
        verification_results = [
            empty_claim_result(
                claim,
                FLAG_NO_EVIDENCE,
                "No evidence was provided. Semantic matching was not performed.",
            )
            for claim in claims_list
        ]
        return wrap_verification_payload(verification_results)

    # Performance optimization: pre-compute evidence embeddings for the batch
    evidence_texts = [_evidence_text(item) for item in deduped_evidence]
    valid_indices = [i for i, text in enumerate(evidence_texts) if text]

    if not valid_indices:
        verification_results = [
            empty_claim_result(
                claim,
                FLAG_NO_EVIDENCE,
                "All provided evidence passages were empty. Semantic matching was not performed.",
            )
            for claim in claims_list
        ]
        return wrap_verification_payload(verification_results)

    valid_evidence_items = [deduped_evidence[i] for i in valid_indices]
    valid_texts = [evidence_texts[i] for i in valid_indices]
    evidence_embeddings = embed_texts(valid_texts, model=model)

    verification_results: list[dict[str, Any]] = []

    for claim in claims_list:
        claim_text = claim["text"]

        # Edge Case 3: Empty claim text
        if not claim_text:
            verification_results.append(
                empty_claim_result(
                    claim,
                    FLAG_EMPTY_CLAIM,
                    "Empty claim text. Semantic matching was not performed.",
                )
            )
            continue

        claim_emb = embed_text(claim_text, model=model)

        # Batch similarity calculation against evidence matrix
        scores = util.cos_sim(claim_emb, evidence_embeddings)[0]

        ranked: list[dict[str, Any]] = []
        for idx, item in enumerate(valid_evidence_items):
            score_val = float(scores[idx].item())
            ranked.append({"score": round(score_val, 4), "evidence": item})

        # Deterministic sorting: highest score first, then evidence_id tie-breaker
        ranked.sort(key=lambda row: (row["score"], row["evidence"].get("id", "")), reverse=True)

        # Configurable Top-K slicing
        if top_k > 0:
            ranked = ranked[:top_k]

        best_score = ranked[0]["score"] if ranked else 0.0
        status = classify_similarity(best_score)

        claim_res = build_claim_result(claim, status, best_score, ranked, note=SAFETY_NOTE)

        # Check target jurisdiction match (Edge Case 6: non-target jurisdiction evidence flag)
        claim_jurisdiction = claim.get("jurisdiction", target_jurisdiction)
        best_evidence_jurisdiction = (
            ranked[0]["evidence"].get("jurisdiction", "") if ranked else ""
        )

        if best_evidence_jurisdiction and claim_jurisdiction:
            if claim_jurisdiction.casefold() != best_evidence_jurisdiction.casefold():
                if FLAG_JURISDICTION_MISMATCH not in claim_res.get("flags", []):
                    claim_res["flags"].append(FLAG_JURISDICTION_MISMATCH)

        verification_results.append(claim_res)

    return wrap_verification_payload(verification_results)


# Clean public entry point alias
verify_claims = verify_claims_batch


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


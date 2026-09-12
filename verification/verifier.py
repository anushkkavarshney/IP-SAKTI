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
    FLAG_LONG_CLAIM,
    FLAG_MODEL_ERROR,
    FLAG_NO_EVIDENCE,
    FLAG_JURISDICTION_MISMATCH,
    FLAG_UNKNOWN_CITATION,
    SAFETY_NOTE,
    build_claim_result,
    deduplicate_claims,
    empty_claim_result,
    extract_claims,
    is_long_claim,
    normalize_claim,
    normalize_claims_payload,
    normalize_evidence_payload,
    unknown_citation_flag_for,
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
    """Load the Sentence Transformer once and reuse it (once-per-process)."""
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
    """Turn many strings into embedding vectors (batched)."""
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


def _model_error_result(claim: dict[str, Any], exc: BaseException) -> dict[str, Any]:
    return empty_claim_result(
        claim,
        FLAG_MODEL_ERROR,
        f"Embedding/model error prevented verification: {type(exc).__name__}.",
    )


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


def _post_process_claim_result(
    claim_res: dict[str, Any],
    claim: dict[str, Any],
    best_evidence: dict[str, Any] | None,
) -> dict[str, Any]:
    """Apply M5 flag enrichment shared by single/batch verification:
    UNKNOWN_CITATION on the best evidence and LONG_CLAIM marking."""
    existing = claim_res.get("flags") or []

    if best_evidence:
        authority = (best_evidence.get("authority") or "").strip()
        unknown = unknown_citation_flag_for(authority)
        if unknown and unknown not in existing:
            existing.append(unknown)

    if claim.get("text") and is_long_claim(claim["text"]) and FLAG_LONG_CLAIM not in existing:
        existing.append(FLAG_LONG_CLAIM)

    claim_res["flags"] = existing
    return claim_res


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

    try:
        ranked = rank_evidence(normalized_claim["text"], evidence, model=model)
    except Exception as exc:  # pragma: no cover - defensive
        return _model_error_result(normalized_claim, exc)

    if top_k is not None and top_k > 0:
        ranked = ranked[:top_k]

    best_score = ranked[0]["score"] if ranked else 0.0
    best_evidence = ranked[0]["evidence"] if ranked else None
    status = classify_similarity(best_score)
    claim_res = build_claim_result(normalized_claim, status, best_score, ranked, note=SAFETY_NOTE)
    return _post_process_claim_result(claim_res, normalized_claim, best_evidence)


def verify_claims_batch(
    claims: dict[str, Any] | list,
    evidence: dict[str, Any] | list,
    *,
    top_k: int = 3,
    target_jurisdiction: str = "India",
    model: SentenceTransformer | None = None,
    include_confidence: bool = True,
) -> dict[str, Any]:
    """
    Batch Claim Verification Engine.

    Accepts multiple claims (M3 claims payload or list) and multiple legal evidence items
    (M4 evidence payload or list). Computes similarity vectors, ranks top-K evidence items
    per claim, evaluates jurisdiction alignment, applies safe abstention + confidence,
    and returns structured verification results.

    `status` signifies preliminary semantic support signal only, NOT legal proof or validation.
    """
    from .confidence import calculate_abstention, calculate_confidence

    model = model or load_model()

    normalized_claims_payload = normalize_claims_payload(claims)
    normalized_evidence_payload = normalize_evidence_payload(evidence)

    claims_list = normalized_claims_payload["claims"]
    raw_evidence_list = normalized_evidence_payload["evidence"]

    # Edge Case: No claims provided
    if not claims_list:
        payload = _finalize_payload([], include_confidence=include_confidence, evidence=raw_evidence_list)
        return payload

    # TASK 11 — deduplicate claims before processing (empty claims are kept
    # so the per-claim loop can flag them with FLAG_EMPTY_CLAIM)
    claims_list = deduplicate_claims(claims_list)

    # Edge Case: Deduplicate evidence items before embedding
    deduped_evidence = deduplicate_evidence(raw_evidence_list)

    # Edge Case: No evidence provided
    if not deduped_evidence:
        verification_results = [
            empty_claim_result(
                claim,
                FLAG_NO_EVIDENCE,
                "No evidence was provided. Semantic matching was not performed.",
            )
            for claim in claims_list
        ]
        return _finalize_payload(verification_results, include_confidence=include_confidence, evidence=raw_evidence_list)

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
        return _finalize_payload(verification_results, include_confidence=include_confidence, evidence=raw_evidence_list)

    try:
        valid_evidence_items = [deduped_evidence[i] for i in valid_indices]
        valid_texts = [evidence_texts[i] for i in valid_indices]
        evidence_embeddings = embed_texts(valid_texts, model=model)
    except Exception as exc:  # pragma: no cover - defensive
        verification_results = [
            _model_error_result(claim, exc) for claim in claims_list
        ]
        return _finalize_payload(verification_results, include_confidence=include_confidence, evidence=raw_evidence_list)

    verification_results: list[dict[str, Any]] = []

    for claim in claims_list:
        claim_text = claim["text"]

        # Edge Case: Empty claim text
        if not claim_text:
            verification_results.append(
                empty_claim_result(
                    claim,
                    FLAG_EMPTY_CLAIM,
                    "Empty claim text. Semantic matching was not performed.",
                )
            )
            continue

        try:
            claim_emb = embed_text(claim_text, model=model)

            scores = util.cos_sim(claim_emb, evidence_embeddings)[0]

            ranked: list[dict[str, Any]] = []
            for idx, item in enumerate(valid_evidence_items):
                score_val = float(scores[idx].item())
                ranked.append({"score": round(score_val, 4), "evidence": item})

            ranked.sort(key=lambda row: (row["score"], row["evidence"].get("id", "")), reverse=True)

            if top_k > 0:
                ranked = ranked[:top_k]

            best_score = ranked[0]["score"] if ranked else 0.0
            best_evidence = ranked[0]["evidence"] if ranked else None
            status = classify_similarity(best_score)

            claim_res = build_claim_result(claim, status, best_score, ranked, note=SAFETY_NOTE)

            claim_jurisdiction = claim.get("jurisdiction", target_jurisdiction)
            best_evidence_jurisdiction = best_evidence.get("jurisdiction", "") if best_evidence else ""

            if best_evidence_jurisdiction and claim_jurisdiction:
                if claim_jurisdiction.casefold() != best_evidence_jurisdiction.casefold():
                    if FLAG_JURISDICTION_MISMATCH not in claim_res.get("flags", []):
                        claim_res["flags"].append(FLAG_JURISDICTION_MISMATCH)

            claim_res = _post_process_claim_result(claim_res, claim, best_evidence)
            verification_results.append(claim_res)
        except Exception as exc:  # pragma: no cover - defensive
            verification_results.append(_model_error_result(claim, exc))

    return _finalize_payload(verification_results, include_confidence=include_confidence, evidence=raw_evidence_list)


def _finalize_payload(
    verification_results: list[dict[str, Any]],
    *,
    include_confidence: bool,
    evidence: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    """Wrap verification results and attach M5 confidence + abstention."""
    from .confidence import calculate_abstention, calculate_confidence

    payload = wrap_verification_payload(verification_results)
    if include_confidence:
        confidence = calculate_confidence(verification_results, evidence=evidence)
        abstention = calculate_abstention(
            verification_results, evidence=evidence, confidence=confidence
        )
        payload["confidence"] = confidence
        payload["abstain"] = abstention["abstain"]
        payload["abstain_reason"] = abstention["abstain_reason"]
        payload["abstain_reasons"] = abstention["reasons"]
    return payload


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


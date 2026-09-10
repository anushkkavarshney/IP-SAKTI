"""
PipelineService -- Member 2's orchestration layer.

This calls (in order): classification_stub -> decision_router ->
rag_adapter (Member 4) -> verification_adapter (Member 5) -> confidence
scoring -> abstention -> final report assembly.

There is deliberately NO real LLM-generation step wired in yet: Member 3's
llm_pipeline/generator.py currently calls Member 4's retriever with the
wrong signature (see rag_adapter.py's module docstring) and there is no
claim-extraction module in the repo. Rather than fabricate an LLM call
that doesn't work, or invent claim-extraction logic that belongs to
Member 3, this pipeline builds a small number of cautious, templated
claims (using the "may / potentially / requires further assessment"
language Roadmap.md Section 9 requires) and sends THOSE through the real
RAG + verification pipeline. Every fact in the final report is either:
  (a) directly backed by retrieved evidence, or
  (b) explicitly marked as not yet evidence-backed.
Nothing is invented. When Member 3's real generator is fixed and wired
up, only `build_claims()` below needs to change.
"""

from typing import Dict, List

from . import classification_stub, decision_router, rag_adapter, verification_adapter

CONFIDENCE_WEIGHTS = {
    "retrieval_quality": 0.30,
    "source_authority": 0.25,
    "claim_support": 0.25,
    "jurisdiction_match": 0.20,
}


def clarify(description: str) -> List[Dict]:
    return classification_stub.get_clarification_questions()


def _build_claims(routing: Dict, classification: Dict) -> List[Dict]:
    claims = []
    claims.append(
        {
            "id": "claim_classification",
            "text": (
                f"This innovation, classified as {classification['category']}, "
                f"likely falls under the {routing['regulatory_path']} regulatory pathway in India."
            ),
        }
    )
    if routing["ip_required"]:
        claims.append(
            {
                "id": "claim_ip",
                "text": (
                    "The described innovation may involve a novel formulation or process "
                    "that could warrant further patentability assessment."
                ),
            }
        )
    if routing["abs_check"]:
        claims.append(
            {
                "id": "claim_abs",
                "text": (
                    "The innovation appears to use a biological resource, which may require "
                    "Access and Benefit Sharing (ABS) review under Indian biodiversity law."
                ),
            }
        )
    return claims


def _evidence_for(claim_text: str, top_k: int = 3) -> List[Dict]:
    return rag_adapter.fetch_evidence(claim_text, jurisdiction="India", top_k=top_k)


def _result_for_claim(claim_id: str, verification_results: List[Dict]) -> Dict:
    for row in verification_results:
        if row.get("claim_id") == claim_id:
            return row
    return {"status": "UNSUPPORTED", "best_evidence": None, "score": 0.0, "flags": ["NO_EVIDENCE"]}


def _to_evidence_chunk(evidence_item: Dict) -> Dict:
    """verification/schemas.py keeps our normalized fields intact on
    best_evidence, so we can map straight back to the frontend shape."""
    return {
        "id": evidence_item.get("id"),
        "jurisdiction": evidence_item.get("jurisdiction", "India"),
        "legal_domain": evidence_item.get("legal_domain") or rag_adapter.NOT_PROVIDED,
        "document_name": evidence_item.get("document_name") or evidence_item.get("document") or rag_adapter.NOT_PROVIDED,
        "section": evidence_item.get("section") or rag_adapter.NOT_PROVIDED,
        "authority": evidence_item.get("authority") or rag_adapter.NOT_PROVIDED,
        "effective_date": evidence_item.get("effective_date"),
        "source_url": evidence_item.get("source_url") or evidence_item.get("source") or rag_adapter.NOT_PROVIDED,
        "text": evidence_item.get("text", ""),
    }

STATUS_MAP = {
    "SUPPORTED": "supported",
    "PARTIALLY_SUPPORTED": "partially_supported",
    "UNSUPPORTED": "unsupported",
}


def _build_items(claims: List[Dict], verification_results: List[Dict]) -> List[Dict]:
    """Builds the per-claim detail list the frontend's ClaimVerificationTable
    needs (verification.items). Previously this was left as None, which
    crashed the frontend on `.map()` since the destructuring default
    `items = []` only applies to `undefined`, not JSON `null`."""
    items = []
    for claim in claims:
        row = _result_for_claim(claim["id"], verification_results)
        best_evidence = row.get("best_evidence")
        items.append(
            {
                "claim_id": claim["id"],
                "claim": claim["text"],
                "best_evidence_id": best_evidence.get("id") if best_evidence else None,
                "status": STATUS_MAP.get(row.get("status", "UNSUPPORTED"), "unsupported"),
                "score": row.get("score", 0.0),
                "explanation": row.get("note"),
                "evidence_snippet": (best_evidence.get("text") if best_evidence else None),
                "source_document": (
                    best_evidence.get("document_name") or best_evidence.get("document")
                    if best_evidence
                    else None
                ),
                "source_section": best_evidence.get("section") if best_evidence else None,
            }
        )
    return items


def _confidence(all_evidence: List[Dict], verification_results: List[Dict]) -> Dict:
    total = len(verification_results) or 1
    supported_or_partial = sum(
        1 for r in verification_results if r.get("status") in ("SUPPORTED", "PARTIALLY_SUPPORTED")
    )
    retrieval_quality = min(len(all_evidence) / 6.0, 1.0)  # rough: 6+ chunks = full score
    source_authority = 0.0  # honest: Member 4's corpus doesn't populate authority yet
    claim_support = supported_or_partial / total
    jurisdiction_match = sum(1 for r in verification_results if r.get("jurisdiction_match")) / total

    signals = {
        "retrieval_quality": round(retrieval_quality, 2),
        "source_authority": round(source_authority, 2),
        "claim_support": round(claim_support, 2),
        "jurisdiction_match": round(jurisdiction_match, 2),
    }
    score = sum(signals[k] * CONFIDENCE_WEIGHTS[k] for k in CONFIDENCE_WEIGHTS)
    level = "HIGH" if score >= 0.7 else "MEDIUM" if score >= 0.4 else "LOW"
    # return {"score": round(score, 2), "level": level, "signals": signals}
    note = None
    if signals["source_authority"] == 0.0 and level == "HIGH":
        level = "MEDIUM"
        note = (
            "Capped from HIGH: source authority is not yet verifiable "
            "(the legal corpus doesn't provide an authority field yet)."
        )

    return {"score": round(score, 2), "level": level, "signals": signals, "note": note}


def analyze(innovation_description: str, clarifications: Dict[str, str], jurisdiction: str = "India") -> Dict:
    category, reason, class_confidence = classification_stub.classify(innovation_description, clarifications)
    classification = {"category": category, "reason": reason, "confidence": class_confidence}

    routing = decision_router.route(category, clarifications)
    claims = _build_claims(routing, classification)

    all_evidence: List[Dict] = []
    for claim in claims:
        all_evidence.extend(_evidence_for(claim["text"]))
    # de-dupe by id while preserving order
    seen = set()
    deduped_evidence = []
    for item in all_evidence:
        if item["id"] not in seen:
            seen.add(item["id"])
            deduped_evidence.append(item)

    if deduped_evidence:
        verification_payload = verification_adapter.verify(claims, deduped_evidence, jurisdiction=jurisdiction)
        verification_results = verification_payload.get("verification", [])
        summary = verification_payload.get("summary", {})
    else:
        verification_results = []
        summary = {"total_claims": len(claims), "supported_claims": 0, "partially_supported_claims": 0, "unsupported_claims": []}

    class_row = _result_for_claim("claim_classification", verification_results)
    regulatory = {
        "jurisdiction": "India",
        "pathway": routing["regulatory_path"],
        "steps": [],  # [OPTIONAL ENHANCEMENT]: populate once Member 3/4 provide pathway-specific evidence
        "evidence": [_to_evidence_chunk(class_row["best_evidence"])] if class_row.get("best_evidence") else [],
    }

    ip_row = _result_for_claim("claim_ip", verification_results)
    ip = {
        "analysis": (
            claims[1]["text"] if routing["ip_required"] and len(claims) > 1 else
            "No novel-process indicator was identified from the clarification answers; IP analysis not triggered."
        ),
        "flags": ["novel_process_indicated"] if routing["ip_required"] else [],
        "evidence": [_to_evidence_chunk(ip_row["best_evidence"])] if ip_row.get("best_evidence") else [],
    }

    abs_row = _result_for_claim("claim_abs", verification_results)
    abs_result = {
        "applicable": routing["abs_check"],
        "analysis": (
            next((c["text"] for c in claims if c["id"] == "claim_abs"), "")
            if routing["abs_check"]
            else "No biological resource was indicated; ABS review not triggered."
        ),
        "evidence": [_to_evidence_chunk(abs_row["best_evidence"])] if abs_row.get("best_evidence") else [],
    }

    confidence = _confidence(deduped_evidence, verification_results)

    abstain = len(deduped_evidence) == 0 or confidence["score"] < 0.3
    abstain_reason = None
    if abstain:
        abstain_reason = (
            "Insufficient authoritative legal evidence was retrieved to support a confident roadmap. "
            "This is a preliminary, rule-based analysis -- please consult a qualified professional."
        )

    return {
        "classification": classification,
        "ip": ip,
        "abs": abs_result,
        "regulatory": regulatory,
        "verification": {
            "total_claims": summary.get("total_claims", len(claims)),
            "supported_claims": summary.get("supported_claims", 0),
            "partially_supported_claims": summary.get("partially_supported_claims", 0),
            "unsupported_claims": [u.get("claim", "") for u in summary.get("unsupported_claims", [])],
            "items": _build_items(claims, verification_results), 
        },
        "confidence": confidence,
        "abstain": abstain,
        "abstain_reason": abstain_reason,
    }

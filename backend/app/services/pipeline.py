"""
PipelineService -- Member 2's orchestration layer.
Updated to call Member 3's real classification/routing/generation instead
of the classification_stub/decision_router/templated-claims stopgap.
"""

from typing import Dict, List

from . import rag_adapter, verification_adapter
from llm_pipeline.classification import classify_formulation
from llm_pipeline.routing import route as m3_route
from llm_pipeline.generator import generate_roadmap

CLARIFICATION_KEY_MAP = {
    "intended_use": "q1",
    "classical_heritage": "q2",
    "novel_process": "q3",
    "biological_resource": "q4",
}


def _clarifications_to_answers(clarifications):
    return [
        {"id": CLARIFICATION_KEY_MAP.get(k, k), "answer": v}
        for k, v in clarifications.items()
    ]


CONFIDENCE_WEIGHTS = {
    "retrieval_quality": 0.30,
    "source_authority": 0.25,
    "claim_support": 0.25,
    "jurisdiction_match": 0.20,
}


def clarify(description: str) -> List[Dict]:
    from . import classification_stub as _stub_for_questions_only
    return _stub_for_questions_only.get_clarification_questions()


def _result_for_claim(claim_id: str, verification_results: List[Dict]) -> Dict:
    for row in verification_results:
        if row.get("claim_id") == claim_id:
            return row
    return {"status": "UNSUPPORTED", "best_evidence": None, "score": 0.0, "flags": ["NO_EVIDENCE"]}


def _to_evidence_chunk(evidence_item: Dict) -> Dict:
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
    retrieval_quality = min(len(all_evidence) / 6.0, 1.0)
    source_authority = 0.0
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
    note = None
    if signals["source_authority"] == 0.0 and level == "HIGH":
        level = "MEDIUM"
        note = (
            "Capped from HIGH: source authority is not yet verifiable "
            "(the legal corpus doesn't provide an authority field yet)."
        )

    return {"score": round(score, 2), "level": level, "signals": signals, "note": note}


def _evidence_chunks_for_ids(evidence_by_id: Dict[str, Dict], ids: List[str]) -> List[Dict]:
    return [_to_evidence_chunk(evidence_by_id[i]) for i in ids if i in evidence_by_id]


def analyze(innovation_description: str, clarifications: Dict[str, str], jurisdiction: str = "India") -> Dict:
    clarification_answers = _clarifications_to_answers(clarifications)
    classification = classify_formulation(innovation_description, clarification_answers)
    routing = m3_route(classification, clarification_answers)

    generated = generate_roadmap(
        innovation_description, clarification_answers, classification, routing, jurisdiction=jurisdiction
    )

    claims = generated["claims"]
    all_evidence = generated["evidence"]
    evidence_by_id = {e["id"]: e for e in all_evidence}

    if claims and all_evidence:
        verification_payload = verification_adapter.verify(claims, all_evidence, jurisdiction=jurisdiction)
        verification_results = verification_payload.get("verification", [])
        summary = verification_payload.get("summary", {})
    else:
        verification_results = []
        summary = {
            "total_claims": len(claims),
            "supported_claims": 0,
            "partially_supported_claims": 0,
            "unsupported_claims": [],
        }

    regulatory = {
        "jurisdiction": "India",
        "pathway": generated["regulatory"].get("pathway") or routing["regulatory_path"],
        "steps": generated["regulatory"].get("steps", []),
        "evidence": _evidence_chunks_for_ids(evidence_by_id, generated["regulatory"].get("evidence_ids", [])),
    }

    ip = {
        "analysis": generated["ip"].get("analysis", ""),
        "flags": generated["ip"].get("flags", []),
        "evidence": _evidence_chunks_for_ids(evidence_by_id, generated["ip"].get("evidence_ids", [])),
    }

    abs_result = {
        "applicable": generated["abs"].get("applicable", routing["abs_check"]),
        "analysis": generated["abs"].get("analysis", ""),
        "evidence": _evidence_chunks_for_ids(evidence_by_id, generated["abs"].get("evidence_ids", [])),
    }

    confidence = _confidence(all_evidence, verification_results)

    abstain = generated.get("abstain", False) or len(all_evidence) == 0 or confidence["score"] < 0.3
    abstain_reason = generated.get("abstain_reason")
    if abstain and not abstain_reason:
        abstain_reason = (
            "Insufficient authoritative legal evidence was retrieved to support a confident roadmap. "
            "This is a preliminary, AI-generated analysis -- please consult a qualified professional."
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
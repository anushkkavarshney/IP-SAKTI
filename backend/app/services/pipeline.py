"""
PipelineService -- Member 2's orchestration layer.

Calls Member 3's real classification/routing/clarification/generation
(llm_pipeline), which internally calls Member 4's RAG, then Member 5's
verification (via verification_adapter), then assembles the response in
the exact shape the frontend expects.

FIXES APPLIED HERE (2026-09-12, after auditing commit b52e525 "llm connect
with backend", which wired M3's real code in for the first time and
exposed several contract mismatches that a plain "it imports fine" check
wouldn't catch):

1. Defensive import of llm_pipeline: llm_client.py does `from groq import
   Groq` at module level. If `groq` isn't installed, importing this file
   used to crash the ENTIRE FastAPI app at startup (not just /analyze).
   Now a missing/broken LLM dependency degrades to a clean, honest
   abstain response instead.

2. /clarify now serves Member 3's REAL clarification question set
   (llm_pipeline/clarification.py) instead of backend's old temporary
   stub. This matters functionally, not just cosmetically: the old stub's
   option values ("yes_biological", "yes_novel_process") never matched
   what llm_pipeline/routing.py checks for (exact "yes"/"no" or specific
   option text) -- meaning ABS/IP routing silently never fired correctly
   for real users. Using M3's own question ids (q1..q5) as field_key, and
   the option text itself as both value and label, means whatever the
   user picks round-trips back through /analyze exactly as routing.py and
   classify_formulation() expect. No separate translation table needed.

3. classify_formulation() returns category as snake_case
   ("phytopharmaceutical") and confidence as an int 0-100. The shared
   frontend contract expects Title Case ("Phytopharmaceutical") and a
   0.0-1.0 float. Mapped/rescaled here.

4. The LLM's "regulatory.steps" are plain strings; the frontend contract
   requires structured RegulatoryStep objects (step_number, title,
   authority, description). Wrapped here instead of crashing Pydantic
   validation on the first real (non-empty) response.

NOT fixed here (raised as an Integration Change Request to Member 3
instead, since the data is lost inside their file before backend ever
sees it): llm_pipeline/generator.py's own _normalize_evidence() still
hardcodes evidence "authority"/"source_url" to NOT_PROVIDED, even though
Member 4's corpus and retriever.py now return the real values.
"""

from typing import Dict, List

from . import verification_adapter

NOT_PROVIDED = "Not provided by the legal corpus yet"

# --- Defensive import of Member 3's LLM pipeline ---------------------------
_LLM_IMPORT_ERROR = None
try:
    from llm_pipeline.classification import classify_formulation
    from llm_pipeline.routing import route as m3_route
    from llm_pipeline.generator import generate_roadmap
    from llm_pipeline.clarification import get_clarification_questions as m3_get_questions
except Exception as exc:  # pragma: no cover -- defensive; env may lack `groq` / API key
    classify_formulation = None
    m3_route = None
    generate_roadmap = None
    m3_get_questions = None
    _LLM_IMPORT_ERROR = exc


CATEGORY_DISPLAY_MAP = {
    "classical_ayurvedic_medicine": "Classical Ayurvedic Medicine",
    "proprietary_ayurvedic_medicine": "Proprietary Ayurvedic Medicine",
    "phytopharmaceutical": "Phytopharmaceutical",
    "nutraceutical": "Nutraceutical",
    "cosmetic": "Cosmetic",
    "unknown_insufficient_information": "Unknown / Insufficient Information",
}

CONFIDENCE_WEIGHTS = {
    "retrieval_quality": 0.30,
    "source_authority": 0.25,
    "claim_support": 0.25,
    "jurisdiction_match": 0.20,
}


def _fallback_questions() -> List[Dict]:
    """Only used if Member 3's clarification module can't be imported
    (see _LLM_IMPORT_ERROR) -- keeps /clarify alive instead of 500ing."""
    from . import classification_stub
    return classification_stub.get_clarification_questions()


def clarify(description: str) -> List[Dict]:
    if m3_get_questions is None:
        return _fallback_questions()

    questions = m3_get_questions(description)
    wire_questions = []
    for q in questions:
        options = q.get("options") or []
        wire_questions.append(
            {
                "id": q["id"],
                "field_key": q["id"],  # q1..q5 -- matches routing.py / classify_formulation
                "question": q["question"],
                "description": q.get("purpose", ""),
                "options": [{"value": opt, "label": opt} for opt in options],
                "allow_text": q.get("input_type") == "text",
            }
        )
    return wire_questions


def _clarifications_to_answers(clarifications: Dict[str, str]) -> List[Dict]:
    """Direct passthrough: clarify() above uses M3's own question ids
    (q1..q5) as field_key, so the dict the frontend submits is already
    keyed exactly how classify_formulation()/route() expect it."""
    return [{"id": k, "answer": v} for k, v in clarifications.items()]


def _result_for_claim(claim_id: str, verification_results: List[Dict]) -> Dict:
    for row in verification_results:
        if row.get("claim_id") == claim_id:
            return row
    return {"status": "UNSUPPORTED", "best_evidence": None, "score": 0.0, "flags": ["NO_EVIDENCE"]}


def _to_evidence_chunk(evidence_item: Dict) -> Dict:
    return {
        "id": evidence_item.get("id"),
        "jurisdiction": evidence_item.get("jurisdiction", "India"),
        "legal_domain": evidence_item.get("legal_domain") or NOT_PROVIDED,
        "document_name": evidence_item.get("document_name") or evidence_item.get("document") or NOT_PROVIDED,
        "section": evidence_item.get("section") or NOT_PROVIDED,
        "authority": evidence_item.get("authority") or NOT_PROVIDED,
        "effective_date": evidence_item.get("effective_date"),
        "source_url": evidence_item.get("source_url") or evidence_item.get("source") or NOT_PROVIDED,
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
    """
    Scale fix (2026-09-12): the frontend's ConfidenceCard.tsx renders
    "{score}/100" and computes each signal's contribution as
    signal * weight directly (e.g. retrieval_quality=90 * 0.30 = 27) --
    i.e. it expects score AND every signal on a 0-100 scale, not 0.0-1.0.
    Everything below is now computed on that 0-100 scale to match.
    """
    total = len(verification_results) or 1
    supported_or_partial = sum(
        1 for r in verification_results if r.get("status") in ("SUPPORTED", "PARTIALLY_SUPPORTED")
    )
    retrieval_quality = min(len(all_evidence) / 6.0, 1.0) * 100
    source_authority = 0.0
    claim_support = (supported_or_partial / total) * 100
    jurisdiction_match = (sum(1 for r in verification_results if r.get("jurisdiction_match")) / total) * 100

    signals = {
        "retrieval_quality": round(retrieval_quality, 1),
        "source_authority": round(source_authority, 1),
        "claim_support": round(claim_support, 1),
        "jurisdiction_match": round(jurisdiction_match, 1),
    }
    score = sum(signals[k] * CONFIDENCE_WEIGHTS[k] for k in CONFIDENCE_WEIGHTS)
    level = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    note = None
    if signals["source_authority"] == 0.0 and level == "HIGH":
        level = "MEDIUM"
        note = (
            "Capped from HIGH: source authority is not yet verifiable "
            "(the legal corpus doesn't provide an authority field yet)."
        )

    return {"score": round(score, 1), "level": level, "signals": signals, "note": note}
def _evidence_chunks_for_ids(evidence_by_id: Dict[str, Dict], ids: List[str]) -> List[Dict]:
    return [_to_evidence_chunk(evidence_by_id[i]) for i in ids if i in evidence_by_id]


def _build_regulatory_steps(steps: List[str]) -> List[Dict]:
    """Wraps the LLM's plain-string steps into the structured RegulatoryStep
    shape the frontend contract requires. We don't have a per-step
    authority from the LLM, so that's marked honestly rather than
    invented."""
    return [
        {
            "step_number": i + 1,
            "title": f"Step {i + 1}",
            "authority": NOT_PROVIDED,
            "description": step_text,
        }
        for i, step_text in enumerate(steps)
    ]


def _llm_unavailable_report(jurisdiction: str) -> Dict:
    return {
        "classification": {
            "category": "Unknown / Insufficient Information",
            "reason": f"Classification/generation service unavailable: {_LLM_IMPORT_ERROR}",
            "confidence": 0.0,
        },
        "ip": {"analysis": "", "flags": [], "evidence": []},
        "abs": {"applicable": False, "analysis": "", "evidence": []},
        "regulatory": {"jurisdiction": jurisdiction, "pathway": "", "steps": [], "evidence": []},
        "verification": {
            "total_claims": 0,
            "supported_claims": 0,
            "partially_supported_claims": 0,
            "unsupported_claims": [],
            "items": [],
        },
        "confidence": {
            "score": 0.0,
            "level": "LOW",
            "signals": {
                "retrieval_quality": 0.0,
                "source_authority": 0.0,
                "claim_support": 0.0,
                "jurisdiction_match": 0.0,
            },
            "note": None,
        },
        "abstain": True,
        "abstain_reason": (
            "The classification/generation service is currently unavailable "
            "(missing dependency or API key). Please try again once it's configured."
        ),
    }


def analyze(innovation_description: str, clarifications: Dict[str, str], jurisdiction: str = "India") -> Dict:
    if classify_formulation is None:
        return _llm_unavailable_report(jurisdiction)

    clarification_answers = _clarifications_to_answers(clarifications)
    raw_classification = classify_formulation(innovation_description, clarification_answers)
    routing = m3_route(raw_classification, clarification_answers)

    generated = generate_roadmap(
        innovation_description, clarification_answers, raw_classification, routing, jurisdiction=jurisdiction
    )

    classification = {
        "category": CATEGORY_DISPLAY_MAP.get(
            raw_classification.get("category"), "Unknown / Insufficient Information"
        ),
        "reason": raw_classification.get("reason", ""),
        "confidence": round(raw_classification.get("confidence", 0) / 100.0, 2),
    }

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
        "steps": _build_regulatory_steps(generated["regulatory"].get("steps", [])),
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

    # Guardrail wiring fix (2026-09-12): generate_roadmap() already computes
    # cautious_language_check (forbidden absolute/guarantee-language scan,
    # Roadmap Section 9/42) via llm_pipeline/guardrails.py -- correctly --
    # but this result was previously never read here, so a violation was
    # detected and then silently discarded. guardrails.py's own docstring
    # says "this is a guardrail, not a blocker: callers should log/flag
    # violations" -- so we treat a failed check as a forced abstention
    # rather than showing potentially non-compliant language to the user.
    cautious_check = generated.get("cautious_language_check")
    guardrail_violation = bool(cautious_check) and not cautious_check.get("passed", True)

    abstain = (
        generated.get("abstain", False)
        or len(all_evidence) == 0
        or confidence["score"] < 30
        or guardrail_violation
    )
    abstain_reason = generated.get("abstain_reason")
    if guardrail_violation and not abstain_reason:
        abstain_reason = (
            "The generated analysis used language that reads as a binding guarantee "
            "rather than cautious decision support, so it's being withheld pending review. "
            f"({cautious_check.get('note', '')})"
        )
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
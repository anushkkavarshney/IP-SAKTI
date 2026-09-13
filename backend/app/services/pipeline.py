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

5. (2026-09-12, later) Member 5 added verification/confidence.py -- a real
   confidence + abstention engine with authority-list scoring and
   citation-integrity checks, computed INSIDE verify_claims() now. This
   supersedes backend's old homebrew _confidence()/abstain calculation,
   which was only ever a stand-in for something that didn't exist yet.
   analyze() now reads confidence/abstain straight from
   verification_adapter.verify()'s payload instead of computing its own.

NOT fixed here (raised as an Integration Change Request to Member 3
instead, since the data is lost inside their file before backend ever
sees it): llm_pipeline/generator.py's own _normalize_evidence() still
hardcodes evidence "authority"/"source_url" to NOT_PROVIDED, even though
Member 4's corpus and retriever.py now return the real values.
[NOTE: you already fixed this one yourself -- update this docstring line
if it's no longer accurate in your copy.]
"""

import logging
from typing import Dict, List

from . import verification_adapter

logger = logging.getLogger("ip_sakti_backend")

NOT_PROVIDED = "Not provided by the legal corpus yet"

# Answers that carry no usable information for classification/routing — they
# mean "I don't know" and must NOT be counted toward input completeness.
_VAGUE_ANSWER_TOKENS = {
    "not sure",
    "unsure",
    "i don't know",
    "i do not know",
    "dont know",
    "don't know",
    "n/a",
    "na",
    "none",
    "tbd",
}


# Map each classification category to the legal_domain strings the RELEVANT
# retrieved evidence must carry (corpus categories, verified against
# rag_engine/processed_data/corpus.json: ABS_BIODIVERSITY, IP_PATENT,
# REGULATORY_AYUSH, REGULATORY_COSMETICS, REGULATORY_NUTRACEUTICAL).
# unknown_insufficient_information maps to [] — with no known product type we
# cannot confirm any domain coverage, so on-domain evidence matching scores 0.
_CATEGORY_TO_REQUIRED_DOMAINS: Dict[str, List[str]] = {
    "classical_ayurvedic_medicine": ["REGULATORY_AYUSH", "ABS_BIODIVERSITY"],
    "proprietary_ayurvedic_medicine": [
        "REGULATORY_AYUSH",
        "ABS_BIODIVERSITY",
        "IP_PATENT",
    ],
    "phytopharmaceutical": ["IP_PATENT", "ABS_BIODIVERSITY", "REGULATORY_AYUSH"],
    "nutraceutical": ["REGULATORY_NUTRACEUTICAL"],
    "cosmetic": ["REGULATORY_COSMETICS"],
    "unknown_insufficient_information": [],
}

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
    # Never silently swallow a startup-class failure: surface the real cause
    # (e.g. "No module named 'rank_bm25'") in the server logs while keeping the
    # honest safe-abstention behavior for clients (we do NOT fake analysis).
    logger.warning("LLM pipeline unavailable -- classification/generation will degrade to safe abstention")
    logger.exception("Failed to initialize LLM pipeline")


CATEGORY_DISPLAY_MAP = {
    "classical_ayurvedic_medicine": "Classical Ayurvedic Medicine",
    "proprietary_ayurvedic_medicine": "Proprietary Ayurvedic Medicine",
    "phytopharmaceutical": "Phytopharmaceutical",
    "nutraceutical": "Nutraceutical",
    "cosmetic": "Cosmetic",
    "unknown_insufficient_information": "Unknown / Insufficient Information",
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
        is_text_input = q.get("input_type") == "text"

        # Fix (2026-09-13): ClarificationWizard.tsx (frontend) has no free-
        # text input UI at all -- it only renders clickable option buttons,
        # and the submit button stays permanently disabled until
        # answers[field_key] is set by clicking one. M3's q5 (jurisdiction)
        # is input_type="text" with zero options, which meant this question
        # could never be answered and users got stuck at step 5/5 forever.
        # Since Roadmap.md explicitly scopes the MVP to India only, a real
        # free-text field isn't even meaningful yet -- so we present it as a
        # single clickable "India" option instead of waiting on a frontend
        # change. If the MVP later supports multiple jurisdictions, this is
        # the one place to add more options (or coordinate with M1 on adding
        # real text-input support to the wizard).
        if is_text_input and not options:
            options = ["India"]

        wire_questions.append(
            {
                "id": q["id"],
                "field_key": q["id"],  # q1..q5 -- matches routing.py / classify_formulation
                "question": q["question"],
                "description": q.get("purpose", ""),
                "options": [{"value": opt, "label": opt} for opt in options],
                "allow_text": False,
            }
        )
    return wire_questions


def _clarifications_to_answers(clarifications: Dict[str, str]) -> List[Dict]:
    """Direct passthrough: clarify() above uses M3's own question ids
    (q1..q5) as field_key, so the dict the frontend submits is already
    keyed exactly how classify_formulation()/route() expect it."""
    return [{"id": k, "answer": v} for k, v in clarifications.items()]


def _compute_input_completeness(clarifications: Dict[str, str]) -> float:
    """Fraction (0..1) of clarification answers that are genuinely
    informative. 'Not sure' / 'unsure' / empty / placeholder answers carry no
    usable signal and are NOT counted — a mostly-'Not sure' input is too vague
    for the system to classify reliably (feeds M5's insufficient_input gate).

    q5 (jurisdiction) defaults to 'India' in the UI, so it is informative
    when present unless it is itself a vague token."""
    values = [str(v or "").strip().casefold() for v in clarifications.values()]
    informative = sum(
        1 for v in values if v and v not in _VAGUE_ANSWER_TOKENS
    )
    total = len(values)
    if total == 0:
        return 0.0
    return round(informative / total, 2)


def _required_domains_for_category(category: str) -> List[str]:
    """Legal-domain expectations for an M3 classification category.
    Unknown/insufficient categories yield an empty list — the system cannot
    confirm ANY domain coverage, which M5 scores as zero on-domain evidence."""
    return list(_CATEGORY_TO_REQUIRED_DOMAINS.get(category or "", []))


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


def _fallback_verification_payload(claims: List[Dict]) -> Dict:
    """Used when there are no claims/evidence to verify at all, or when
    verification_adapter.verify() itself fails -- gives analyze() a
    uniform shape to read confidence/abstain from either way."""
    return {
        "verification": [],
        "summary": {
            "total_claims": len(claims),
            "supported_claims": 0,
            "partially_supported_claims": 0,
            "unsupported_claims": [],
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
            "No claims or no evidence were available to verify, so no confident "
            "analysis could be produced."
        ),
    }


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

    # --- Evidence-sufficiency context for M5 safe abstention ---------------
    # 1. input_completeness: fraction of informative clarification answers.
    #    Vague/miracle inputs answer mostly "Not sure" → low → M5 abstains.
    # 2. required_domains: legal domains expected for this product type. An
    #    unknown product type → empty list → M5 scores on-domain evidence as
    #    0 and the classification_unknown gate forces abstention.
    input_completeness = _compute_input_completeness(clarifications)
    required_domains = _required_domains_for_category(
        raw_classification.get("category", "unknown_insufficient_information")
    )

    # Debugging fix (2026-09-13): "confidence always 0" with no exception
    # anywhere means this branch below is silently taking the fallback path
    # -- almost certainly because generate_roadmap()'s internal RAG call
    # (Member 4) returned zero evidence for the query. Logging the actual
    # counts here turns "confidence is 0, no idea why" into a concrete
    # number instead of a guess.
    print(f"[DEBUG] analyze(): {len(claims)} claims, {len(all_evidence)} evidence chunks from generate_roadmap()")
    logger.info(
        "analyze(): input_completeness=%s category=%s required_domains=%s",
        input_completeness,
        raw_classification.get("category"),
        required_domains,
    )

    if claims and all_evidence:
        # verify() now returns confidence + abstention computed by Member 5
        # (verification/confidence.py, added 2026-09-12) -- this SUPERSEDES
        # backend's own homebrew _confidence()/abstain logic, which was only
        # ever a stand-in because nothing existed yet. M5's version does
        # real authority-list scoring and citation-integrity checks that
        # backend could not replicate.
        verification_payload = verification_adapter.verify(
            claims,
            all_evidence,
            jurisdiction=jurisdiction,
            classification=raw_classification,
            input_completeness=input_completeness,
            required_domains=required_domains,
        )
    else:
        verification_payload = _fallback_verification_payload(claims)

    verification_results = verification_payload.get("verification", [])
    summary = verification_payload.get("summary", {})
    confidence = verification_payload.get("confidence") or _fallback_verification_payload(claims)["confidence"]

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

    m5_abstain = verification_payload.get("abstain", False)
    m5_abstain_reason = verification_payload.get("abstain_reason")

    abstain = generated.get("abstain", False) or m5_abstain or guardrail_violation
    abstain_reasons = list(verification_payload.get("abstain_reasons") or [])
    if guardrail_violation:
        if "guardrail_violation" not in abstain_reasons:
            abstain_reasons = ["guardrail_violation"] + abstain_reasons
        abstain_reason = (
            "The generated analysis used language that reads as a binding guarantee "
            "rather than cautious decision support, so it's being withheld pending review. "
            f"({cautious_check.get('note', '')})"
        )
    elif m5_abstain_reason:
        abstain_reason = m5_abstain_reason
    else:
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
        "abstain_reasons": abstain_reasons,
    }
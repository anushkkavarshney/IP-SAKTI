"""
Adapter for Member 4's rag_engine.

WHY THIS FILE EXISTS (read this before touching it):

1. llm_pipeline/generator.py calls `LegalRetriever(corpus_path=...)` and
   `.retrieve_evidence(query, top_k=...)`. Member 4's actual class is
   `LegalRetriever()` (no constructor args) with a method called
   `.get_relevant_context(query, jurisdiction, top_k)`. Calling generator.py
   as-is will raise a TypeError/AttributeError. We do NOT fix generator.py
   (that's Member 3's file) -- instead this backend calls Member 4's real
   method directly and builds the LLM prompt itself using the (working)
   llm_pipeline.prompts templates.

2. rag_engine has no __init__.py and retriever.py does a bare
   `from search import LegalSearchEngine` (not `from rag_engine.search`).
   That only works if rag_engine/'s own directory is on sys.path. We add it
   here so the import succeeds without editing rag_engine/retriever.py.

3. Member 4's evidence dicts use different field names (`content`,
   `act_name`, `doc_id`) than what Member 5's verifier and the frontend
   contract expect (`text`, `document`, `evidence_id`, `source_url`,
   `authority`, `legal_domain`). This adapter normalizes that shape.
   Fields Member 4 hasn't started populating yet (authority, source_url,
   legal_domain) are filled with an honest placeholder string rather than
   invented values -- see LEGAL SAFETY note below.

LEGAL SAFETY: this file must never invent legal content. If a metadata
field is missing from the corpus, say so plainly ("not provided by the
legal corpus yet") instead of guessing an authority or URL.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# parents[0]=services, [1]=app, [2]=backend, [3]=repo root
_REPO_ROOT = str(Path(__file__).resolve().parents[3])
_RAG_ENGINE_DIR = os.path.join(_REPO_ROOT, "rag_engine")

# Make `from search import LegalSearchEngine` (inside retriever.py) resolve.
if _RAG_ENGINE_DIR not in sys.path:
    sys.path.append(_RAG_ENGINE_DIR)
# Make `from rag_engine.retriever import LegalRetriever` resolve from here.
if _REPO_ROOT not in sys.path:
    sys.path.append(_REPO_ROOT)

_retriever = None
_import_error: Exception | None = None

try:
    from rag_engine.retriever import LegalRetriever  # type: ignore
except Exception as exc:  # pragma: no cover - defensive, corpus may not exist yet
    LegalRetriever = None  # type: ignore
    _import_error = exc


def _get_retriever():
    """Lazily construct Member 4's retriever so a missing corpus file
    doesn't crash the whole backend at import time."""
    global _retriever
    if _retriever is None and LegalRetriever is not None:
        _retriever = LegalRetriever()
    return _retriever


NOT_PROVIDED = "Not provided by the legal corpus yet"


def fetch_evidence(query: str, jurisdiction: str = "India", top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Calls Member 4's real retriever and returns evidence normalized to the
    shape used everywhere else in this backend (and in the frontend's
    LegalEvidenceChunk type).

    Returns an empty list (never raises) if the corpus/retriever isn't
    available yet -- callers must treat "no evidence" as a trigger for
    safe abstention, per Roadmap.md Section 22.
    """
    retriever = _get_retriever()
    if retriever is None:
        return []

    try:
        raw_results = retriever.get_relevant_context(query, jurisdiction=jurisdiction, top_k=top_k)
    except Exception:
        # RAG failure -> no evidence, not a crash. Pipeline decides to abstain.
        return []

    normalized = []
    for item in raw_results:
        normalized.append(
            {
                "id": item.get("doc_id"),
                "jurisdiction": item.get("jurisdiction") or jurisdiction,
                "legal_domain": item.get("category") or NOT_PROVIDED,
                "document_name": item.get("act_name") or NOT_PROVIDED,
                "section": item.get("section") or NOT_PROVIDED,
                "authority": NOT_PROVIDED,
                "effective_date": item.get("as_of_date"),
                "source_url": NOT_PROVIDED,
                "text": item.get("content") or "",
            }
        )
    return normalized

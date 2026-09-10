# Member 2 Backend — IP-SAKTI Navigator

This is the FastAPI backend that connects the frontend, the RAG engine (Member 4),
and the verification module (Member 5). It does not reimplement any other
member's logic — it calls their real code and adapts the shapes in between.

## Decisions made while building this (so nobody has to re-litigate them)

**1. `api/` (the existing root-level FastAPI prototype) was left untouched.**
It implements a single debug-style endpoint (`/api/v1/analyze`) that isn't the
roadmap's `/analyze` and isn't what the frontend calls. `/backend` is the real
integration layer going forward. If `api/` turns out to be dead code, that's a
call for whoever owns it (unclear ownership) — not something I deleted or
merged in unilaterally.

**2. `/clarify` and classification have no logic to call yet (Member 3's
scope, not yet built), so `/backend` ships a small, clearly-labeled
placeholder** instead of returning "not implemented" errors. This was the
"help everyone move fast" call: the frontend, and anyone testing the pipeline,
gets a working end-to-end flow *today*, and it's isolated to two files:
- `app/services/classification_stub.py` — clarification questions (identical
  to the frontend's own mock data) + a keyword-based classifier.
- `app/services/decision_router.py` — the rule-based router from Roadmap.md
  Section 8.

Both files have a docstring explaining exactly what to replace and why.
**Nothing else in the backend needs to change** when Member 3's real
classification/routing lands — `pipeline.py` only calls these two modules'
public functions.

**3. Two real bugs were found in Member 3's and Member 4's code
(`llm_pipeline/generator.py` calling a method on Member 4's retriever that
doesn't exist, and `rag_engine`/`verification` using bare imports that only
work from inside their own directory). Per the "prefer adapting inside
`/backend`" rule, these were worked around with adapters instead of raising
Integration Change Requests, since the fix is purely on the calling side and
doesn't require changing either member's files:**
- `app/services/rag_adapter.py` — calls Member 4's *actual* method
  (`get_relevant_context`), adds `rag_engine/` to `sys.path` so its internal
  `from search import ...` import resolves, and normalizes field names
  (`content` → `text`, `act_name` → `document_name`, etc.) to what the rest
  of the backend and the frontend expect. Fields Member 4's corpus doesn't
  populate yet (`authority`, `source_url`, `legal_domain`) are marked
  `"Not provided by the legal corpus yet"` — never invented.
- `app/services/verification_adapter.py` — same `sys.path` fix for
  `verification/`'s bare imports, then calls `verify_claims(...)` exactly as
  documented in `verification/HANDOFF.md`.

Worth flagging to Member 3 and Member 4 directly at some point (their bare
imports will also break for *them* the moment their code is imported from
anywhere outside its own folder), but it wasn't blocking for us, so no
Integration Change Request was filed.

**4. No LLM generation is wired in.** `llm_pipeline/generator.py` is broken
(see above) and there's no claim-extraction module in the repo at all yet.
Rather than fake an LLM call or invent claim-extraction logic that belongs to
Member 3, `pipeline.py` builds a small number of cautious, templated claims
("may / potentially / requires further assessment" language, per Roadmap.md
Section 9) and runs *those* through the real RAG + verification pipeline.
Every fact in the response is either backed by retrieved evidence or
explicitly marked as not yet evidence-backed — nothing is fabricated. Swap in
real LLM generation by changing `_build_claims()` in `pipeline.py` only.

**5. No MongoDB integration exists yet (Member 6's scope), so `/report`
uses an in-memory dict** (`app/services/report_store.py`). Reports are lost
on server restart. `[OPTIONAL ENHANCEMENT]`: swap this for MongoDB once
Member 6's collections are ready — it's one file.

## Folder structure

```
backend/
├── app/
│   ├── main.py                  FastAPI app, CORS, router registration
│   ├── routes/
│   │   ├── clarify.py           POST /clarify
│   │   ├── analyze.py           POST /analyze
│   │   └── report.py            GET  /report/{session_id}
│   ├── schemas/
│   │   ├── requests.py          Matches what frontend/src/lib/api.ts sends
│   │   └── responses.py         1:1 mirror of frontend/src/types/roadmap.ts
│   ├── services/
│   │   ├── pipeline.py          Orchestrator — the main integration logic
│   │   ├── classification_stub.py   [TEMPORARY] see decision #2 above
│   │   ├── decision_router.py       [TEMPORARY] see decision #2 above
│   │   ├── rag_adapter.py           Calls Member 4, see decision #3
│   │   ├── verification_adapter.py  Calls Member 5, see decision #3
│   │   └── report_store.py          In-memory store, see decision #5
│   └── utils/errors.py          Consistent, safe error responses
└── tests/test_api.py
```

## How to run it

From the **repo root** (not from inside `backend/` — Member 4's default
corpus path is relative to the repo root):

```bash
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

Then point the frontend at it — it already defaults to
`http://localhost:8000` (see `frontend/src/lib/api.ts`).

## How to test each endpoint

```bash
# Health check
curl http://localhost:8000/

# Clarification questions
curl -X POST http://localhost:8000/clarify \
  -H "Content-Type: application/json" \
  -d '{"description": "An Ashwagandha extract for stress relief"}'

# Full analysis
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "innovation_description": "A modified Ashwagandha formulation using a new extraction process for stress relief.",
    "clarifications": {
      "intended_use": "therapeutic_internal",
      "classical_heritage": "modified_classical",
      "novel_process": "yes_novel_process",
      "biological_resource": "yes_biological"
    },
    "jurisdiction": "India"
  }'

# Retrieve a saved report (use the session_id from the /analyze response above)
curl http://localhost:8000/report/<session_id>
```

Or run the automated tests:

```bash
pytest backend/tests/test_api.py -v
```

These cover: valid request, invalid request (empty description → 400,
missing field → 422), a full end-to-end run, and the report round-trip
(including a 404 for an unknown session).

**Note on imports:** every file under `app/` uses relative imports
(`from .routes import ...`, `from ..schemas import ...`) rather than
`from app.xxx import ...`. This is required because uvicorn loads this
module as `backend.app.main` when run from the repo root — a bare
`from app.routes import ...` would fail with `ModuleNotFoundError: No
module named 'app'` since `app` isn't a top-level importable name in that
context. Don't "simplify" these back to absolute `app.` imports.

**Note:** `/clarify` works with zero extra installs. `/analyze` needs
`sentence-transformers` (used by both Member 4's search and Member 5's
verifier) actually installed — that's in the root `requirements.txt`, it's
just a heavier install (pulls in `torch`).

## What's genuinely working end-to-end right now

Classification (rule-based) → routing → real RAG retrieval → real Member 5
verification → confidence scoring → safe abstention → response shaped
exactly like the frontend expects. Verified locally with the FastAPI test
client (see commit history / this file's author for the smoke test).

## What's still a placeholder, and who owns replacing it

| Piece | Status | Owner |
|---|---|---|
| Classification logic | Rule-based stub in `/backend` | Member 3 |
| Clarification questions | Static, copied from frontend mock | Member 3 |
| Decision routing | Rule-based stub in `/backend` | Member 3 |
| LLM-generated roadmap text | Not wired (generator.py is broken, see decision #3) | Member 3 |
| Claim extraction | Templated placeholder claims in `pipeline.py` | Member 3 |
| Evidence metadata (`authority`, `source_url`, `legal_domain`) | Not populated by the corpus yet | Member 4 |
| Report persistence | In-memory only | Member 6 |

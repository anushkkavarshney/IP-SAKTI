# IP-SAKTI Navigator — Member 5 Integration Handoff Document

This document provides exact specifications for integrating **Member 5 (Verification + Confidence module)** into the IP-SAKTI Navigator pipeline.

---

## 1. Module Pipeline

```text
M3 Claims Payload (LLM Claims)  ───┐
                                   ├──> Member 5 `verify_claims()` ──> M5 Verification Payload
M4 Evidence Payload (Legal RAG) ───┘
```

M5 also owns the **confidence engine** (0–100) and the **safe-abstention**
decision (Roadmap §19–23, §29, §44–48).

---

## 2. Member Integration Guidelines

### MEMBER 3 — AI / Claim Generation
- **What Member 3 provides**: Structured JSON payload of generated claims requiring verification.
- **Expected Data Contract**:
  ```json
  {
    "jurisdiction": "India",
    "claims": [
      {
        "claim_id": "C1",
        "text": "The formulation uses Ashwagandha root extract as a biological resource.",
        "claim_type": "ABS",
        "jurisdiction": "India",
        "evidence_ids": ["E1", "E2"]
      }
    ]
  }
  ```
- **Field Aliasing**: M5 accepts `claim_id` or `id`. String claims or bare lists are also automatically normalized.
- **`evidence_ids` (optional)**: explicit citations the claim grounds on.
  M5 preserves them and validates each id against the supplied evidence set:
  matches appear in `valid_citation_ids`; ids that do not exist in the evidence
  are listed in `unknown_citation_ids` and flagged with
  `UNKNOWN_CITATION_REFERENCE` — a fabricated id is **never** made valid by
  semantic similarity. Claims without `evidence_ids` are verified semantically
  as before.
- **Extraction interface**: `from verification import extract_claims` returns the normalized `{"jurisdiction", "claims"}` payload and is None/malformed-safe.

---

### MEMBER 4 — Legal RAG
- **What Member 4 provides**: Array of retrieved statutory evidence chunks from official legal sources.
- **Expected Data Contract** (two shapes; both normalize identically):
  ```json
  {
    "jurisdiction": "India",
    "evidence": [
      {
        "evidence_id": "E1",
        "text": "Extraction of plant material from biological species requires ABS compliance under Section 3.",
        "document": "The Biological Diversity Act, 2002",
        "section": "Section 3",
        "jurisdiction": "India",
        "legal_domain": "ABS",
        "authority": "National Biodiversity Authority",
        "effective_date": "2003-02-05",
        "source_url": "https://nbaindia.org/act/"
      }
    ]
  }
  ```
  Raw Member 4 native chunks (`doc_id`, `act_name`, `content`, `category`,
  `as_of_date`) are accepted **directly, with no upstream adapter**:
  ```json
  {
    "doc_id": "patent_act_1970",
    "act_name": "The Patents Act, 1970",
    "section": "Section 3",
    "as_of_date": "2026-01-01",
    "effective_date": "2026-01-01",
    "jurisdiction": "India",
    "category": "Patent",
    "authority": "Indian Patent Office",
    "source_url": "https://ipindia.gov.in/",
    "content": "An invention may not be a patentable invention if it is a mere discovery of a scientific principle..."
  }
  ```
- **Alias vocabulary**: M5 accepts `id`/`evidence_id`/`doc_id`,
  `document`/`document_name`/`act_name`, `text`/`content`,
  `legal_domain`/`category`, `source`/`source_url`, plus `section`,
  `as_of_date`, `effective_date`, `authority`, `jurisdiction`.
- **Authority handling**: a recognized Indian authority (IPO / Indian Patent
  Office, National Biodiversity Authority, CDSCO, FSSAI, Ministry of AYUSH,
  DCGI, etc.) scores 100; a real-looking unrecognized authority scores a
  conservative 40 and raises `UNKNOWN_CITATION`; **missing or placeholder
  authorities ("Not provided by the legal corpus yet", "unknown",
  "unavailable", empty) score 0** — absence of information earns no credit.
- **Citation safety**: `UNKNOWN_CITATION` (unrecognized authority) and
  `UNKNOWN_CITATION_REFERENCE` (fabricated/stale claim-declared evidence id)
  both withhold the analysis pending verification.
- **Traceability Rule**: Member 4 must preserve statutory metadata (`document`, `section`, `authority`, `source_url`, `effective_date`, `legal_domain`) on every chunk. Member 5 will retain all metadata intact in the verification output.

---

### MEMBER 2 — Backend API Integration
- **How Member 2 calls Member 5**:
  ```python
  from verification import verify_claims

  @app.post("/api/verify")
  def verify_endpoint(claims_payload: dict, evidence_payload: dict):
      result = verify_claims(
          claims=claims_payload,
          evidence=evidence_payload,
          top_k=3,
          target_jurisdiction="India"
      )
      return result
  ```
- **Execution Model**: Pure Python function call. Synchronous, deterministic, in-memory execution. No external database or network dependency.
- **New top-level keys** in the returned payload: `confidence` (0–100, signals,
  level), `abstain` (bool), `abstain_reason`, `abstain_reasons`. Existing keys
  (`support_type`, `note`, `verification`, `summary`) are unchanged.

---

### MEMBER 6 — Database & Storage
- **What Member 6 should persist**:
  - `claim_id` and `claim` text
  - `status` (`SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`)
  - `similarity_score`
  - `best_evidence_id` and `best_evidence` metadata (`document`, `section`, `source_url`, `authority`, `legal_domain`)
  - `flags` (e.g. `["JURISDICTION_MISMATCH"]`, `["NO_EVIDENCE"]`, `["UNKNOWN_CITATION"]`, `["UNKNOWN_CITATION_REFERENCE"]`)
  - citation fields: `declared_evidence_ids`, `valid_citation_ids`, `unknown_citation_ids`
  - `summary` counts (`total_claims`, `supported_claims`, `unsupported_claims`)
  - `confidence` object (`score`, `level`, `signals`)
  - `abstain` flag and `abstain_reason`

---

## 3. Confidence & Abstention Contract

### Confidence (0–100 scale)
```json
{
  "score": 72.5,
  "level": "MEDIUM",
  "signals": {
    "retrieval_quality": 50.0,
    "source_authority": 100.0,
    "claim_support": 50.0,
    "jurisdiction_match": 100.0
  },
  "note": null
}
```
Weights: retrieval 0.30, source authority 0.25, claim support 0.25,
jurisdiction match 0.20. Levels: HIGH 80–100, MEDIUM 50–79, LOW < 50.
`source_authority` is never hardcoded to 0 and is never inflated by
placeholders — recognized authorities feed 100, missing/placeholder feeds 0,
and an unrecognized-but-real authority feeds a conservative 40.

### Abstention (safe refusal)
`abstain: true` when: no evidence, no claims, confidence < 30 (default), or a
citation-integrity warning is present (`UNKNOWN_CITATION` unrecognized
authority, or `UNKNOWN_CITATION_REFERENCE` fabricated evidence id).

---

## 4. Disclaimers & Safety Rules

- **Semantic Relevance Signal**: `status` and `similarity_score` measure semantic similarity and relevance against retrieved statutory passages.
- **Not Legal Advice**: Cosine similarity scores do **not** represent legal proof, validity, or binding legal determinations.
- **No Hallucination**: If evidence is missing, M5 returns `UNSUPPORTED` with `FLAG_NO_EVIDENCE` rather than inventing citations. Unrecognized authorities are flagged (`UNKNOWN_CITATION`), and fabricated / stale claim-declared evidence ids are flagged (`UNKNOWN_CITATION_REFERENCE`) — never silently accepted.
- **No Fake Contradiction**: M5 never emits "the evidence contradicts the claim". NLI-based contradiction detection is explicitly out of scope and is a future / P2 capability.
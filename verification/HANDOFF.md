# IP-SAKTI Navigator — Member 5 Integration Handoff Document

This document provides exact specifications for integrating **Member 5 (Verification + Confidence module)** into the IP-SAKTI Navigator pipeline.

---

## 1. Module Pipeline

```text
M3 Claims Payload (LLM Claims)  ───┐
                                   ├──> Member 5 `verify_claims()` ──> M5 Verification Payload
M4 Evidence Payload (Legal RAG) ───┘
```

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
        "jurisdiction": "India"
      }
    ]
  }
  ```
- **Field Aliasing**: M5 accepts `claim_id` or `id`. String claims or bare lists are also automatically normalized.

---

### MEMBER 4 — Legal RAG
- **What Member 4 provides**: Array of retrieved statutory evidence chunks from official legal sources.
- **Expected Data Contract**:
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
- **Traceability Rule**: Member 4 must preserve statutory metadata (`document`, `section`, `authority`, `source_url`, `effective_date`) on every chunk. Member 5 will retain all metadata intact in the verification output.

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

---

### MEMBER 6 — Database & Storage
- **What Member 6 should persist**:
  - `claim_id` and `claim` text
  - `status` (`SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`)
  - `similarity_score`
  - `best_evidence_id` and `best_evidence` metadata (`document`, `section`, `source_url`)
  - `flags` (e.g. `["JURISDICTION_MISMATCH"]`, `["NO_EVIDENCE"]`)
  - `summary` counts (`total_claims`, `supported_claims`, `unsupported_claims`)

---

## 3. Disclaimers & Safety Rules

- **Semantic Relevance Signal**: `status` and `similarity_score` measure semantic similarity and relevance against retrieved statutory passages.
- **Not Legal Advice**: Cosine similarity scores do **not** represent legal proof, validity, or binding legal determinations.
- **No Hallucination**: If evidence is missing, M5 returns `UNSUPPORTED` with `FLAG_NO_EVIDENCE` rather than inventing citations.

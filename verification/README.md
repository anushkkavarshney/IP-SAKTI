# IP-SAKTI Navigator — Member 5 (Day 1)

First-stage **claim → evidence semantic matching** for IP-SAKTI Navigator (SIH 2026, PS SIH26045).

This module does **not** decide whether a legal claim is true. It only measures how closely a claim matches retrieved text.

## What this module does

```text
Claim
  → Sentence embedding
  → Cosine similarity vs each evidence passage
  → Rank evidence
  → Best evidence
  → Preliminary semantic support status
```

Possible preliminary labels:

- `SUPPORTED`
- `PARTIALLY_SUPPORTED`
- `UNSUPPORTED`

These labels mean **preliminary semantic support**, not legal proof.

## Model

`sentence-transformers/all-MiniLM-L6-v2`

Chosen because it is small, fast on a laptop, and good enough for a 5-day MVP semantic-matching prototype.

## How embeddings work

An embedding is a list of numbers that represents the **meaning** of a sentence. Two sentences about biological resources should land close together in that numeric space, even if they do not share the exact same words.

## What cosine similarity means

Cosine similarity compares two embeddings.

- Values closer to **1** → stronger semantic similarity
- Values closer to **0** (or lower) → weaker semantic similarity

Similarity is a **relevance signal**. It does not mean the claim is legally correct.

## Important limitation

Semantic similarity is only a first-stage relevance signal and is **not sufficient by itself** to establish legal support.

Day 1 does **not** include NLI, a cross-encoder, a confidence engine, or abstention. Those come later.

All passages in `test_cases.py` are **synthetic demo evidence**. They are not official Indian Acts, rules, or citations. Real evidence will later come from Member 4's RAG module.

Similarity thresholds in `verifier.py` (`SUPPORTED_MIN`, `PARTIALLY_SUPPORTED_MIN`) are **starting constants** for this demo set. They are not scientifically or legally validated.

## How to run

From the `verification` folder:

```bash
pip install -r requirements.txt
python verifier.py
```

The first run downloads the model. Later runs reuse it from the local cache.

## Day 2 Task 1 — Interface Contracts & Schema Design

M3 and M4 code are not in this repository yet. `schemas.py` defines the canonical, implementation-ready JSON data contracts between modules:

```text
M3 Generated Claims  →  M5 Verification Module  ←  M4 Retrieved Legal Evidence
                                ↓
                    Verification Output JSON
```

### 1. M3 → M5 Contract (Claims Payload)
M3 provides extracted claims requiring verification.
```json
{
  "jurisdiction": "India",
  "claims": [
    {
      "claim_id": "C1",
      "text": "The innovation may involve a biological resource under Indian law.",
      "claim_type": "ABS",
      "jurisdiction": "India"
    }
  ]
}
```

### 2. M4 → M5 Contract (Evidence Payload)
M4 provides authoritative legal chunks retrieved from official statutory sources.
```json
{
  "jurisdiction": "India",
  "evidence": [
    {
      "evidence_id": "E1",
      "text": "Section 2(c) defines biological resources...",
      "document": "The Biological Diversity Act, 2002",
      "section": "Section 2(c)",
      "jurisdiction": "India",
      "legal_domain": "ABS",
      "authority": "National Biodiversity Authority",
      "effective_date": "2003-02-05",
      "source_url": "https://nbaindia.org/act/"
    }
  ]
}
```

### 3. M5 → Downstream Contract (Verification Results Payload)
M5 produces claim-by-claim preliminary semantic support status, similarity scores, ranked evidence, jurisdiction matching, and warning flags.
```json
{
  "support_type": "preliminary_semantic_support",
  "note": "Similarity is a first-stage relevance signal only. It does not establish legal validity or legal proof.",
  "verification": [
    {
      "claim_id": "C1",
      "claim": "The innovation may involve a biological resource under Indian law.",
      "status": "SUPPORTED",
      "score": 0.85,
      "similarity_score": 0.85,
      "support_type": "preliminary_semantic_support",
      "note": "Similarity is a first-stage relevance signal only. It does not establish legal validity or legal proof.",
      "best_evidence_id": "E1",
      "best_evidence": { ... },
      "ranked_evidence": [ ... ],
      "jurisdiction_match": true,
      "flags": []
    }
  ],
  "summary": {
    "total_claims": 1,
    "supported_claims": 1,
    "partially_supported_claims": 0,
    "unsupported_claims": []
  }
}
```

### Backwards Compatibility & Field Aliasing
The schema normalizers in `schemas.py` automatically adapt:
- Claim ID: accepts both `id` and `claim_id`
- Evidence ID: accepts both `id` and `evidence_id`
- Source URL: accepts both `source` and `source_url`
- Document Name: accepts both `document` and `document_name`
- Input format: accepts string claims / bare lists (Day 1 format) as well as full JSON payloads.

`status` signifies preliminary semantic support, NOT legal proof or validation.
Confidence scoring and abstention are isolated in subsequent tasks.

## Day 2 Task 2 — Batch Claim Verification Engine

`verify_claims_batch` in `verifier.py` provides multi-claim, multi-evidence batch verification.

### Capabilities
- **Batch Embedding**: Vectorizes all evidence chunks in a single matrix pass for performance.
- **Top-K Ranking**: Slices evidence passages per claim to configurable `top_k` (default `top_k=3`).
- **Deduplication**: Automatically filters duplicate evidence passages by ID or text content.
- **Jurisdiction Safety**: Flags jurisdiction mismatches (`JURISDICTION_MISMATCH`) when evaluating non-India evidence against India claims.
- **Metadata Integrity**: Retains statutory metadata (`document`, `section`, `authority`, `source_url`, `effective_date`) without inventing missing fields.

### Python API Usage
```python
from verifier import verify_claims_batch

result = verify_claims_batch(
    claims=m3_claims_payload,
    evidence=m4_evidence_payload,
    top_k=3,
    target_jurisdiction="India",
)
```

### Running Batch Tests
From the `verification` folder:
```bash
python test_batch.py
```
Runs 10 scenario edge-case tests (single/multi-claims, empty claims/evidence, irrelevant evidence, duplicate deduplication, metadata preservation, `top_k` slicing, and jurisdiction mismatch flagging).

## Day 2 Task 3 — Testing, Validation & Edge Cases

The test suite in `verification/tests/test_verifier.py` covers 12 required edge-case categories.

### How to Run Tests
From the `verification` folder:
```bash
# Run using Pytest
pytest tests/test_verifier.py

# Or run directly via Python
python tests/test_verifier.py
```

### 12 Category Test Breakdown
1. **Strong Semantic Match**: Asserts high similarity (>= 0.70) and correct rank-1 statutory evidence selection.
2. **Partial Support**: Asserts proper partial similarity signal handling when claim text exceeds evidence coverage.
3. **Unsupported Claim**: Asserts low similarity / unsupported classification when evidence contradicts or lacks support.
4. **Irrelevant Evidence**: Asserts `UNSUPPORTED` status and score < 0.45 for off-topic evidence.
5. **Multiple Evidence Chunks**: Asserts correct Top-K ranking order across 5–10 mixed evidence chunks.
6. **Multiple Claims**: Asserts independent claim evaluation, ID tracking, and separate evidence ranking in batch runs.
7. **No Evidence Handling**: Asserts `UNSUPPORTED` status and `NO_EVIDENCE` flag when evidence list is empty.
8. **Empty Claim List Handling**: Asserts zero total claims and empty output array without crashing.
9. **Jurisdiction Mismatch Flagging**: Asserts `jurisdiction_match: false` and `JURISDICTION_MISMATCH` flag for non-India evidence.
10. **Duplicate Evidence Deduplication**: Asserts deduplication by ID or text content without wasting Top-K slots.
11. **Missing Metadata Preservation**: Asserts preservation of empty metadata strings (`""`) without fabricating missing legal fields.
12. **Ambiguous Semantic Match (Topical vs Entailment)**: Demonstrates topical similarity overlap vs logical entailment limitations.

### Key Architectural Finding & Limitation
**Semantic Similarity $\neq$ Logical Entailment**:
Sentence embeddings calculate topical relevance and vocabulary overlap. A claim asserting an absolute outcome (e.g., *"A patent will definitely be granted"*) may receive a high similarity score against conditional legal text (*"Patent protection depends on applicable requirements"*) because both share patent terminology. This empirical finding explicitly justifies the subsequent NLI (Natural Language Inference) and Cross-Encoder entailment layers.

## Day 2 Task 4 — Integration Readiness & Public Entry Point

The `verification` folder is structured as a clean, importable Python package with centralized configuration constants.

### Clean Public Entry Point
```python
from verification import verify_claims

# Run batch verification
result = verify_claims(
    claims=m3_claims_payload,
    evidence=m4_evidence_payload,
    top_k=3,
    target_jurisdiction="India"
)
```

### Integration Handoff & Example
- **Integration Example Script**: `python examples/integration_example.py`
- **Handoff Document**: `HANDOFF.md` contains detailed contract expectations for Member 3 (Claims), Member 4 (Evidence RAG), Member 2 (Backend API), and Member 6 (Database).

### Centralized Configuration Constants
Located in `verifier.py` and `schemas.py`:
- `MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"`
- `SUPPORTED_MIN = 0.70`
- `PARTIALLY_SUPPORTED_MIN = 0.45`
- `DEFAULT_TOP_K = 3`
- `DEFAULT_JURISDICTION = "India"`





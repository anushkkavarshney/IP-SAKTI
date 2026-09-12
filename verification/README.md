# IP-SAKTI Navigator — Member 5 (Verification + Confidence)

First-stage **claim → evidence semantic matching**, plus the M5 **confidence**
and **safe-abstention** engine, for IP-SAKTI Navigator (SIH 2026, PS SIH26045).

This module does **not** decide whether a legal claim is true. It only measures
how closely a claim matches retrieved text and how confident the platform
should be about presenting that analysis.

## What this module does

```text
M3 Claims
   ↓ extract_claims
Claim
   → Sentence embedding
   → Cosine similarity vs each evidence passage
   → Rank evidence (top_k)
   → Best evidence
   → Preliminary semantic support status
   → Flags (NO_EVIDENCE, EMPTY_CLAIM, JURISDICTION_MISMATCH,
            UNKNOWN_CITATION, LONG_CLAIM, MODEL_ERROR)
   ↓
Confidence engine (0–100) + safe abstention decision
```

Possible preliminary labels:

- `SUPPORTED`
- `PARTIALLY_SUPPORTED`
- `UNSUPPORTED`

These labels mean **preliminary semantic support**, not legal proof.

## Confidence engine (M5-owned)

Computed in `confidence.py` (`calculate_confidence`), always on a **0–100**
scale for both the overall score and each signal:

| Signal              | Weight | Meaning                                              |
|---------------------|--------|------------------------------------------------------|
| `retrieval_quality` | 0.30   | How much evidence was provided (≤ 6 items → 100)     |
| `source_authority`  | 0.25   | Best-evidence authority from the known list          |
| `claim_support`     | 0.25   | Share of claims supported / partially supported      |
| `jurisdiction_match`| 0.20   | Share of claims whose best evidence matches jurisdiction |

Levels: **HIGH = 80–100**, **MEDIUM = 50–79**, **LOW < 50**.

## Safe abstention (M5-owned)

`calculate_abstention` decides whether the analysis should be **withheld**:
- no evidence provided → abstain;
- confidence below the safe-decision threshold (default 30) → abstain;
- no claims → abstain;
- an unrecognized citation on the best evidence lowers the score and triggers
  a withholding warning.

Unsupported claims are **flagged, never presented as fact**.

## No fake contradiction detection

M5 performs *semantic relevance ranking only*. It intentionally never emits
"the evidence contradicts the claim" statements — contradiction/NLI detection
is out of scope and documented as a limitation (`validate_no_contradiction_detection`).

## Model

`sentence-transformers/all-MiniLM-L6-v2`

Loaded **once per process** (`load_model`), small, fast on a laptop, and good
enough for a 5-day MVP semantic-matching prototype.

## How embeddings work

An embedding is a list of numbers that represents the **meaning** of a
sentence. Two sentences about biological resources should land close together
in that numeric space, even if they do not share the exact same words.

## What cosine similarity means

Cosine similarity compares two embeddings.

- Values closer to **1** → stronger semantic similarity
- Values closer to **0** (or lower) → weaker semantic similarity

Similarity is a **relevance signal**. It does not mean the claim is legally
correct.

## Important limitation

Semantic similarity is only a first-stage relevance signal and is **not
sufficient by itself** to establish legal support. It is also **not
contradiction detection** — high topical overlap can coexist with an absolute,
untrue claim (see `test_category_12_ambiguous_semantic_match`).

All passages in `test_cases.py` are **synthetic demo evidence**. They are not
official Indian Acts, rules, or citations. Real evidence will later come from
Member 4's RAG module.

Similarity thresholds in `verifier.py` (`SUPPORTED_MIN = 0.70`,
`PARTIALLY_SUPPORTED_MIN = 0.45`) are **starting constants** for this demo set.
They are not scientifically or legally validated.

## How to run

From the repository root (the package uses relative imports):

```bash
pip install -r requirements.txt

python -m verification.verifier          # Day-1 synthetic test cases (13/13)
python -m verification.test_batch        # batch scenarios (10/10)
python -m verification.schemas           # print contract examples
python -m verification.examples.integration_example   # M3 → M5 → M4 demo
```

Run the full test suite:

```bash
python -m pytest verification/tests -q
```

The first run downloads the model. Later runs reuse it from the local cache.

## Public API

```python
from verification import (
    extract_claims,        # canonical claim extraction (T1)
    verify_claims,         # batch verification + confidence + abstention
    verify_claim,          # single-claim verification
    calculate_confidence,  # 0–100 confidence engine
    calculate_abstention,  # safe abstention decision
)
```

`verify_claims(claims, evidence, top_k=3, target_jurisdiction="India")` returns:

```json
{
  "support_type": "preliminary_semantic_support",
  "note": "Similarity is a first-stage relevance signal only. It does not establish legal validity or legal proof.",
  "verification": [
    {
      "claim_id": "C1",
      "claim": "...",
      "status": "SUPPORTED",
      "score": 0.85,
      "similarity_score": 0.85,
      "support_type": "preliminary_semantic_support",
      "note": "Similarity is a first-stage relevance signal only. It does not establish legal validity or legal proof.",
      "best_evidence_id": "E1",
      "best_evidence": { "...": "..." },
      "ranked_evidence": [ "...": "..." ],
      "jurisdiction_match": true,
      "flags": []
    }
  ],
  "summary": {
    "total_claims": 1,
    "supported_claims": 1,
    "partially_supported_claims": 0,
    "unsupported_claims": []
  },
  "confidence": {
    "score": 100.0,
    "level": "HIGH",
    "signals": {
      "retrieval_quality": 100.0,
      "source_authority": 100.0,
      "claim_support": 100.0,
      "jurisdiction_match": 100.0
    },
    "note": null
  },
  "abstain": false,
  "abstain_reason": null,
  "abstain_reasons": []
}
```

## Interface contracts

```text
M3 Generated Claims  →  M5 Verification Module  ←  M4 Retrieved Legal Evidence
                                ↓
                    Verification Output JSON (+ confidence + abstention)
```

### M3 → M5 (Claims Payload)
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

### M4 → M5 (Evidence Payload)
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

### Backwards Compatibility & Field Aliasing
The schema normalizers in `schemas.py` automatically adapt:
- Claim ID: accepts both `id` and `claim_id`
- Evidence ID: accepts both `id` and `evidence_id`
- Source URL: accepts both `source` and `source_url`
- Document Name: accepts both `document` and `document_name`
- Input format: accepts string claims / bare lists (Day 1 format) as well as
  full JSON payloads, and is **None / malformed-safe** for both claims and
  evidence.

## Batch verification engine

`verify_claims_batch` in `verifier.py` provides multi-claim, multi-evidence
batch verification.

### Capabilities
- **Batch Embedding**: Vectorizes all evidence chunks in a single matrix pass
  (one batched `encode` call) for performance.
- **Top-K Ranking**: Slices evidence passages per claim to configurable
  `top_k` (default `top_k=3`).
- **Claim Deduplication**: Filters duplicate claims by normalized text.
- **Evidence Deduplication**: Filters duplicate evidence passages by ID or text.
- **Jurisdiction Safety**: Flags jurisdiction mismatches
  (`JURISDICTION_MISMATCH`).
- **Citation Safety**: Flags unrecognized authorities (`UNKNOWN_CITATION`).
- **Long-claim awareness**: Marks overlength claims (`LONG_CLAIM`).
- **Defensive failures**: Model/embedding errors produce structured
  `MODEL_ERROR` results instead of crashing.
- **Metadata Integrity**: Retains statutory metadata without inventing fields.

## Test suite

- `verification/tests/test_verifier.py` — 12 edge-case categories (Day 2 / T3).
- `verification/tests/test_integration.py` — importability + determinism.
- `verification/tests/test_m5_full.py` — 32 mandatory M5 tests (confidence,
  abstention, citation safety, normalization hardening, dedup, long claims,
  model errors, M4 alias compatibility, evidence link integrity).

```bash
python -m pytest verification/tests -q
```

## Package layout

```
verification/
  __init__.py      public API exports
  schemas.py       normalization + flags + claim extraction
  verifier.py      embedding, ranking, batch verification
  confidence.py    confidence engine + safe abstention
  test_cases.py    synthetic Day-1 cases (13)
  test_batch.py    batch scenario runner (10)
  examples/integration_example.py   M3→M5→M4 demo
  tests/           pytest suite (12 + 8 + 32)
```

Run the integration example from the repo root:

```bash
python -m verification.examples.integration_example
```
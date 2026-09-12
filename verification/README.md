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
            UNKNOWN_CITATION, UNKNOWN_CITATION_REFERENCE,
            LONG_CLAIM, MODEL_ERROR)
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
| `source_authority`  | 0.25   | Best-evidence authority score (see below)            |
| `claim_support`     | 0.25   | Share of claims supported / partially supported      |
| `jurisdiction_match`| 0.20   | Share of claims whose best evidence matches jurisdiction |

Levels: **HIGH = 80–100**, **MEDIUM = 50–79**, **LOW < 50**.

### Source authority scoring (honest, conservative)

| Authority value                                      | Score |
|------------------------------------------------------|-------|
| On the known-authority list (IPO, NBA, CDSCO, ...)   | 100   |
| Present but not on the known list (real-looking)     | 40    |
| Missing / `None` / empty                             | 0     |
| Placeholder ("Not provided by the legal corpus yet", "unknown", "unavailable") | 0 |

A placeholder carries **no information**, so it earns **no credit** — unknown
authority ≠ 40 points. A real-looking but unrecognized authority gets a
conservative 40: it is not assumed fake, and it is not treated as verified.

## Claim-declared citations (`evidence_ids`)

M3 may attach explicit evidence citations to a claim:

```json
{
  "claim_id": "C1",
  "text": "A new extraction process may warrant patentability review.",
  "claim_type": "IP",
  "jurisdiction": "India",
  "evidence_ids": ["E1", "E2"]
}
```

M5 **preserves** `evidence_ids` and **validates** every declared id against
the evidence set actually supplied to M5:

- id found in the supplied evidence → listed in `valid_citation_ids`;
- id **not** found → listed in `unknown_citation_ids` and the claim is flagged
  with `UNKNOWN_CITATION_REFERENCE`.

Citation identity and semantic similarity are **separate concepts**: a fake
evidence id is never made valid because another passage happens to score high.
These fields are present on every claim result:

```json
{
  "declared_evidence_ids": ["E1", "fake_e3"],
  "valid_citation_ids": ["E1"],
  "unknown_citation_ids": ["fake_e3"]
}
```

Claims without `evidence_ids` (or with `[]` / `None`) are verified
semantically as before — no fabricated-citation flag is forced.

## Safe abstention (M5-owned)

`calculate_abstention` decides whether the analysis should be **withheld**:
- no evidence provided → abstain;
- confidence below the safe-decision threshold (default 30) → abstain;
- no claims → abstain;
- a citation-integrity flag (`UNKNOWN_CITATION` on an unrecognized best-evidence
  authority, or `UNKNOWN_CITATION_REFERENCE` for a fabricated/stale evidence id)
  withholds the analysis pending verification.

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
    normalize_evidence_ids,# normalize a claim's declared citation ids
    split_citation_ids,    # split declared ids into (valid, unknown)
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
      "declared_evidence_ids": ["E1"],
      "valid_citation_ids": ["E1"],
      "unknown_citation_ids": [],
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

Two evidence shapes are supported; both normalize to the same canonical fields
(`id`, `document`, `section`, `text`, `legal_domain`, `authority`,
`effective_date`, `as_of_date`, `source_url`, `jurisdiction`, `source`).

**Backend-normalized shape** (`id` / `text` / `document_name` / `legal_domain`):

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

**Native / raw M4 shape** (`doc_id` / `act_name` / `content` / `category`
/ `as_of_date`) — accepted directly, no upstream adapter required:

```json
{
  "jurisdiction": "India",
  "evidence": [
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
  ]
}
```

### Field aliasing (both shapes accepted)

The schema normalizers in `schemas.py` automatically adapt:

| Canonical      | Accepted aliases                              |
|----------------|-----------------------------------------------|
| `id`           | `id`, `evidence_id`, `doc_id`                 |
| `document`     | `document`, `document_name`, `act_name`       |
| `text`         | `text`, `content`                             |
| `legal_domain` | `legal_domain`, `category`                    |
| `source_url`   | `source_url`, `source`                        |
| `authority`    | `authority`                                   |
| `section`      | `section`                                     |
| `as_of_date`   | `as_of_date`                                  |
| `effective_date` | `effective_date`                            |
| `jurisdiction` | `jurisdiction`                                |

Minimal evidence records (just `id` + `text`) and Day-1 `source`-based records
also work. Inputs may be a full payload (`{"evidence": [...]}`) or a bare list,
and are **None / malformed-safe**. Metadata is never invented — missing values
stay empty.

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
- **Citation Safety**: Flags unrecognized authorities (`UNKNOWN_CITATION`) and
  fabricated / stale claim-declared evidence references
  (`UNKNOWN_CITATION_REFERENCE`), never presenting a fake id as valid.
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
- `verification/tests/test_m5_citations_and_m4_vocab.py` — raw M4 evidence
  vocabulary, `evidence_ids` preservation, fabricated-citation validation,
  honest authority scoring, raw-M4 end-to-end (21 tests).

```bash
python -m pytest verification/tests -q
```

Expected: **78 passed** (57 original + 21 new).

## Package layout

```
verification/
  __init__.py      public API exports
  schemas.py       normalization + flags + claim extraction + citation split
  verifier.py      embedding, ranking, batch verification + citation validation
  confidence.py    confidence engine + safe abstention + authority scoring
  test_cases.py    synthetic Day-1 cases (13)
  test_batch.py    batch scenario runner (10)
  examples/integration_example.py   M3→M5→M4 demo
  tests/           pytest suite (12 + 8 + 32 + 21)
```

Run the integration example from the repo root:

```bash
python -m verification.examples.integration_example
```
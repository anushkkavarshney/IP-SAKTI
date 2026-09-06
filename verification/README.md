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

## Later integration

- Member 3 will send claims extracted from the LLM answer.
- Member 4 will send retrieved evidence (`text`, `document`, `section`, `jurisdiction`, `source_url`).
- This verifier already accepts either `source` or `source_url`.

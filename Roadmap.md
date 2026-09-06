# IP-SAKTI Navigator — Master AI Working Brief

### SIH 2026 · Problem Statement SIH26045


# 1. PROJECT NAME

## IP-SAKTI Navigator

**IP-SAKTI Navigator is an AI-powered decision-support platform for Ayurvedic innovators that converts a plain-language innovation description into an evidence-backed IP, biodiversity/ABS, and regulatory commercialization roadmap.**

The system is NOT a generic chatbot.

The system is NOT a replacement for a patent attorney, regulatory expert, or legal professional.

The system assists users in understanding:

* What type of Ayurvedic product they may be developing
* Which regulatory pathway may apply
* Whether IP considerations may exist
* Whether biodiversity/ABS considerations may arise
* Which authoritative legal sources support the guidance
* How confident the system is in the available evidence
* When human expert review may be required

---

# 2. CORE PROBLEM WE ARE SOLVING

An Ayurvedic innovator may develop something such as:

> "A modified Ashwagandha formulation using a new extraction technique for stress relief."

But the innovator may not know:

* Is this a classical Ayurvedic medicine?
* Is it a proprietary Ayurvedic medicine?
* Is it a phytopharmaceutical?
* Is it a nutraceutical?
* Is it a cosmetic?
* Can some part of the innovation potentially receive IP protection?
* Is traditional knowledge relevant?
* Does biodiversity / ABS need to be considered?
* Which Indian regulatory pathway is applicable?
* Which laws or regulations support these conclusions?

Currently, such information is fragmented across multiple laws, regulatory authorities, documents, and domains.

IP-SAKTI Navigator brings these decisions into **one structured decision-support workflow**.

---

# 3. MAIN INNOVATION / USP

The main innovation is NOT simply:

> "We use an LLM."

The real innovation is:

> **Hybrid Legal RAG + Intelligent Classification + Decision Routing + Independent Claim Verification + Evidence-Based Confidence + Safe Abstention**

The system does not directly ask an LLM to answer legal questions.

Instead, it follows a controlled pipeline.

---

# 4. FIXED SYSTEM ARCHITECTURE

Every AI tool working on this project must follow this architecture.

Do NOT redesign the project unless the team explicitly changes this document.

```text
User describes Ayurvedic innovation
                ↓
Clarification Engine
4–5 targeted questions
                ↓
Formulation Classification
                ↓
Decision Router
        ┌───────┼────────┐
        ↓       ↓        ↓
       IP      ABS    Regulatory
        └───────┼────────┘
                ↓
Jurisdiction Filter
India for current MVP
                ↓
Hybrid Legal Retrieval
Vector Search + Keyword Search
                ↓
Optional Reranking
                ↓
Authoritative Legal Evidence
                ↓
LLM Structured Generation
using retrieved evidence only
                ↓
Claim Extraction
                ↓
Claim ↔ Evidence Verification
                ↓
Supported / Partial / Unsupported
                ↓
Confidence Engine
                ↓
Safe Abstention when required
                ↓
Structured Commercialization Roadmap
                ↓
Optional Human Expert Escalation
```

---

# 5. NON-NEGOTIABLE AI RULE

## The LLM must NEVER be treated as the legal knowledge source.

The LLM receives:

```text
User Information
+
Classification
+
Decision Routing
+
Retrieved Legal Evidence
```

and generates an answer based on that evidence.

It must NOT rely on its pretrained memory to invent:

* Acts
* Rules
* Sections
* Regulatory requirements
* Patent outcomes
* Approval outcomes
* Authorities
* Legal conclusions

If authoritative evidence is unavailable:

> The system must say that sufficient evidence was not found.

---

# 6. FORMULATION CLASSIFICATION

The system classifies the user's innovation into one of the following categories:

1. Classical Ayurvedic Medicine
2. Proprietary Ayurvedic Medicine
3. Phytopharmaceutical
4. Nutraceutical
5. Cosmetic
6. Unknown / Insufficient Information

Classification must return:

```json
{
  "category": "",
  "reason": "",
  "confidence": 0
}
```

The classification should NOT return only a label.

It must provide:

* classification
* short explanation
* confidence

---

# 7. CLARIFICATION ENGINE

Before classification, the system may ask approximately 4–5 targeted questions.

Questions should determine things such as:

* What is the intended use of the product?
* Is this based on an existing Ayurvedic formulation?
* Is there a new extraction/process/formulation involved?
* Does the innovation use biological resources?
* Is the product intended as medicine, supplement/food, or cosmetic?
* What jurisdiction is being considered?

For the current MVP:

## India is the primary jurisdiction.

Do not spend significant development time on international jurisdictions until the India MVP works completely.

---

# 8. DECISION ROUTER

After classification, the system determines which analysis modules are required.

Example rules:

```text
Biological resource involved?
        ↓
       YES
        ↓
     ABS PATH
```

```text
Novel process / formulation?
        ↓
       YES
        ↓
      IP PATH
```

```text
Medicinal / Ayurvedic claim?
        ↓
       YES
        ↓
AYUSH / Drug Regulatory Path
```

```text
Food / Supplement?
        ↓
       YES
        ↓
    FSSAI Path
```

```text
Cosmetic product?
        ↓
       YES
        ↓
 Cosmetic Regulatory Path
```

Example router output:

```json
{
  "category": "proprietary_ayurvedic",
  "ip_required": true,
  "abs_check": true,
  "regulatory_path": "ayush",
  "jurisdiction": "india"
}
```

---

# 9. IP ANALYSIS MODULE

For the MVP, the IP module provides decision support regarding:

* Possible patentability considerations
* Novel formulation/process indicators
* Traditional knowledge flags
* Prior-art concerns
* Patent-related legal evidence
* Need for further professional patentability assessment

The system must NEVER say:

> "Your patent will be granted."

It may say:

> "The described extraction process may warrant further patentability assessment."

The system should use cautious terms such as:

* may
* potentially
* appears to
* requires further assessment
* further prior-art analysis is recommended

---

# 10. TRADITIONAL KNOWLEDGE / TK

The system should identify when traditional Ayurvedic knowledge may be relevant.

Traditional Knowledge should be treated as an important patentability/prior-art consideration.

For the current MVP, this may initially be represented as:

> Traditional Knowledge / prior-art risk flag

A full TKDL search engine is NOT required for the 5-day MVP.

The system must NOT pretend that it has direct TKDL integration unless this is actually implemented.

---

# 11. ABS / BIODIVERSITY MODULE

ABS means:

## Access and Benefit Sharing.

The ABS module determines whether use of biological resources may require additional biodiversity-related review.

The module should identify:

* Whether a biological resource appears to be involved
* Whether ABS considerations may apply
* Relevant authoritative biodiversity evidence
* Whether further expert assessment is necessary

It must NOT make absolute legal determinations.

---

# 12. REGULATORY MODULE

The regulatory engine determines the likely regulatory pathway based on classification.

Possible pathways include:

* AYUSH / Ayurvedic medicine
* Drug/phytopharmaceutical pathway
* FSSAI / nutraceutical pathway
* Cosmetic pathway

Output should be structured as:

```json
{
  "jurisdiction": "India",
  "pathway": "",
  "steps": [],
  "evidence": []
}
```

---

# 13. JURISDICTION RULE

For the MVP:

# INDIA FIRST.

India is the primary supported jurisdiction.

Future versions may add:

* European Union
* USA
* ASEAN
* Australia
* Japan
* other jurisdictions

India and international laws must NEVER be mixed together.

When international support is introduced, every jurisdiction must have its own:

* corpus
* filters
* evidence
* answer section

---

# 14. LEGAL KNOWLEDGE BASE

The legal corpus should contain selected authoritative Indian sources relevant to:

* Patent law
* Biodiversity / ABS
* AYUSH
* Drug regulations
* Nutraceutical / FSSAI
* Cosmetics

For the 5-day MVP:

## Do NOT attempt to ingest the entire Indian legal system.

Use approximately:

> **10–20 highly relevant authoritative documents / sections**

Quality is more important than quantity.

---

# 14A. CORPUS SOURCE LIST — WHERE MEMBER 4 SHOULD ACTUALLY PULL DOCUMENTS FROM

This is a starting list of official, authoritative sources. Member 4 should download the specific Act/Rule PDFs from these sites — do NOT use blog posts, summary articles, or unofficial compilations as legal source text. Every downloaded document must be logged with its exact source URL and date accessed (see Section 15 metadata format).

### Patents / IP
* **Indian Patent Office (IPO)** — ipindia.gov.in
  → The Patents Act, 1970 and Patent Rules (full text, amendments)
* **India Code** — indiacode.nic.in
  → Official consolidated repository of central Acts; use as the canonical fallback if IPO's own PDF is hard to parse
* **WIPO Lex (India country page)** — wipolex.wipo.int
  → English-translated official texts, useful cross-check copy

### Traditional Knowledge / Prior Art
* **Traditional Knowledge Digital Library (TKDL)** — tkdl.res.in
  → Public-facing information about TKDL scope and access policy (note: full TKDL database access is restricted/licensed — do NOT claim live TKDL integration unless access is actually granted; see Section 10)
* **CSIR** — csir.res.in
  → Background/policy documents on TKDL and traditional knowledge protection

### Biodiversity / ABS
* **National Biodiversity Authority (NBA)** — nbaindia.org
  → The Biological Diversity Act, 2002; Biological Diversity Rules, 2004; ABS Guidelines and amendment notifications
* **Ministry of Environment, Forest and Climate Change (MoEFCC)** — moefcc.gov.in
  → Notifications and amendments related to biodiversity law

### AYUSH / Ayurvedic Drug Regulation
* **Ministry of AYUSH** — ayush.gov.in
  → AYUSH-specific notifications, classical formulation lists, licensing guidance
* **Central Drugs Standard Control Organisation (CDSCO)** — cdsco.gov.in
  → The Drugs and Cosmetics Act, 1940 and Rules, 1945 (including ASU&H drug provisions, Schedule T for manufacturing)
* **Pharmacopoeia Commission for Indian Medicine & Homoeopathy (PCIM&H)** — pcimh.gov.in
  → Ayurvedic Pharmacopoeia references for classical formulation verification

### Nutraceutical / Food
* **FSSAI** — fssai.gov.in
  → FSSAI Act, 2006; Nutraceutical/Health Supplements Regulations, 2016

### Cosmetics
* **CDSCO** — cdsco.gov.in
  → Cosmetic Rules, 2020 (under the Drugs and Cosmetics Act)
* **BIS (Bureau of Indian Standards)** — bis.gov.in
  → Relevant cosmetic product standards, if needed for specific claims

### General Fallback
* **India Code** — indiacode.nic.in
  → Use this as the single canonical source whenever a specific ministry site's PDF is broken, outdated, or hard to extract text from

**Practical Day 1 instruction for Member 4:** pick 2–3 documents from each category above (roughly 12–18 total, matching the 10–20 target in Section 14), prioritizing the Patents Act, Biological Diversity Act, and Drugs and Cosmetics Act/Rules as the three most demo-critical sources, since the recommended demo scenario (Section 49) touches all three.

---

# 15. LEGAL DOCUMENT METADATA

Every chunk should store metadata such as:

```json
{
  "jurisdiction": "India",
  "legal_domain": "Patent",
  "document_name": "",
  "section": "",
  "authority": "",
  "effective_date": "",
  "source_url": "",
  "text": ""
}
```

Do not store legal chunks without identifying their source.

---

# 16. RAG PIPELINE

The legal RAG pipeline is:

```text
Official Legal PDFs
        ↓
PyMuPDF
        ↓
Text Extraction
        ↓
Cleaning
        ↓
Section-Aware Chunking
        ↓
Metadata Addition
        ↓
Embeddings
        ↓
MongoDB Atlas
        ↓
Vector Search
        +
BM25 / Keyword Search
        ↓
Fusion
        ↓
Optional Cross-Encoder Reranking
        ↓
Best Legal Evidence
```

---

# 17. WHY HYBRID SEARCH

Semantic search alone is NOT enough for legal documents.

Example:

A query may contain:

> "Section 3(p)"

Exact section numbers and legal terminology require keyword-based retrieval.

Therefore the intended architecture combines:

## Meaning-based search

*

## Exact keyword/BM25 search

The MVP may implement a simpler BM25 system if necessary, but the architecture remains hybrid retrieval.

---

# 18. LLM GENERATION RULE

The LLM receives only:

```text
User Innovation
+
Clarification Answers
+
Classification
+
Routing Result
+
Retrieved Legal Evidence
```

The system prompt must instruct the LLM:

1. Use retrieved evidence only for legal/regulatory claims.
2. Do not invent laws or sections.
3. Cite the supporting evidence.
4. Use cautious language.
5. Clearly indicate uncertainty.
6. Do not make binding legal determinations.
7. Return structured JSON.

---

# 19. CLAIM VERIFICATION ENGINE

This is one of the project's strongest technical differentiators.

Most systems stop at:

```text
Retrieve
↓
Generate
↓
Answer
```

IP-SAKTI uses:

```text
Retrieve
↓
Generate
↓
Extract Claims
↓
Verify Claims
↓
Confidence
↓
Answer / Abstain
```

The verification engine takes:

```text
LLM-generated answer
+
Retrieved evidence
```

and evaluates individual claims.

Possible outputs:

```text
SUPPORTED
PARTIALLY SUPPORTED
UNSUPPORTED
```

Example:

```json
{
  "claim": "Patent protection may be possible.",
  "status": "partially_supported",
  "evidence": ["relevant source"],
  "score": 0.72
}
```

Unsupported legal claims must:

* be removed
* be rewritten cautiously
* or be explicitly flagged

They must NOT silently remain in the final answer.

---

# 20. MEMBER 5 — VERIFICATION APPROACH

For the current MVP, verification may use:

### Stage 1 — Semantic Matching

* Sentence Transformer embeddings
* Cosine similarity

Used to identify the evidence most related to a claim.

### Stage 2 — Stronger Verification

Use one of:

* Cross-Encoder
* Natural Language Inference model
* claim/evidence classification logic

Possible relationship:

```text
Claim
+
Evidence
↓
Supported
Contradicted
Uncertain
```

Cosine similarity alone must NOT be treated as final legal verification.

It is primarily a relevance signal.

---

# 21. CONFIDENCE ENGINE

Confidence must NOT be generated simply by asking:

> "LLM, how confident are you?"

Confidence must come from measurable signals.

Initial MVP formula:

```text
Overall Confidence =

30% Retrieval Quality
+
25% Source Authority
+
25% Citation / Claim Support
+
20% Jurisdiction Match
```

Initial interpretation:

```text
80–100 → HIGH

50–79 → MEDIUM

Below 50 → LOW
```

These values are initial MVP thresholds and may be tuned using test cases.

---

# 22. SAFE ABSTENTION

Low-quality evidence is NOT a failure.

Correct abstention is an intended feature.

Example:

> "The available authoritative sources do not provide sufficient evidence to confidently determine this. Further expert review is recommended."

Do not remove abstention simply to make the demo appear smoother.

A system that refuses to hallucinate is more trustworthy than one that always produces an answer.

---

# 23. HUMAN ESCALATION

Human escalation means:

> Generate a structured case summary that can later be reviewed by an IP/regulatory professional.

It does NOT mean:

> Instant live connection to a lawyer.

Unless the team explicitly implements an expert network, never advertise it that way.

A case summary may include:

* Innovation description
* Clarification answers
* Classification
* Activated pathways
* Retrieved legal evidence
* Unsupported/uncertain claims
* Confidence score
* Questions requiring expert review

---

# 24. FINAL USER REPORT

The intended final report may contain:

1. Innovation Summary
2. Product Classification
3. Classification Confidence
4. IP Opportunities
5. Patentability / Prior-Art Flags
6. Traditional Knowledge Flags
7. ABS / Biodiversity Considerations
8. India Regulatory Roadmap
9. Recommended Next Actions
10. Evidence & Citations
11. Claim Verification Status
12. Overall Confidence
13. Human Expert Escalation Recommendation

For the 5-day MVP, some sections may be simplified, but the structure should remain consistent.

---

# 25. FIXED MVP TECH STACK

## FRONTEND — MEMBER 1

```text
Next.js
React
TypeScript
Tailwind CSS
shadcn/ui
Fetch / Axios
```

Responsibilities:

* Landing page
* Innovation input page
* Clarification wizard
* Analyze button
* Loading state
* Final roadmap dashboard
* Evidence/citations
* Confidence display

---

# 26. BACKEND — MEMBER 2

```text
Python
FastAPI
Pydantic
Uvicorn
REST APIs
JSON
```

Responsibilities:

* `/analyze`
* `/clarify`
* `/report`
* Pipeline orchestration
* API schemas
* Error handling
* Module integration

Member 2 is the main integration owner.

---

# 27. AI CLASSIFICATION + ROUTING + GENERATION — MEMBER 3

```text
Python
LLM API
Prompt Engineering
Pydantic
Structured JSON Outputs
```

Responsibilities:

* Clarification logic
* Product classification
* Classification reasoning
* Classification confidence
* Decision routing
* Prompt engineering
* Structured LLM roadmap generation

Member 3 determines:

> What the AI should reason about.

---

# 28. LEGAL RAG — MEMBER 4

```text
Python
PyMuPDF
Embedding Model
MongoDB Atlas
MongoDB Atlas Vector Search
BM25 / Keyword Search
Optional Cross-Encoder Reranker
```

Responsibilities:

* Collect authoritative legal sources (see Section 14A for exact source list)
* PDF extraction
* Cleaning
* Chunking
* Metadata
* Embeddings
* Hybrid retrieval
* Evidence output

Member 4 determines:

> What evidence the AI should see.

---

# 29. VERIFICATION + CONFIDENCE — MEMBER 5

```text
Python
sentence-transformers
Cosine Similarity
Cross-Encoder / NLI Model
Custom Claim Verification Logic
Optional NumPy / Pandas
```

Responsibilities:

* Extract individual claims
* Match claims to retrieved evidence
* Supported / partially supported / unsupported classification
* Citation support checks
* Confidence calculation
* Safe abstention trigger
* Verification test cases

Member 5 determines:

> Did the AI's answer actually follow the evidence?

---

# 30. DATABASE + TESTING + DEPLOYMENT — MEMBER 6

```text
MongoDB Atlas
Git
GitHub
Postman
Docker
Vercel
Render / Railway
Environment Variables
```

Responsibilities:

* MongoDB collections
* GitHub repository
* Environment setup
* Integration support
* API testing
* End-to-end testing
* Deployment
* Demo dataset
* Bug tracking

Member 6 determines:

> How the system is stored, tested and deployed.

---

# 31. DATABASE

Primary database:

# MongoDB Atlas

Possible collections:

```text
sessions
innovations
clarifications
reports
evidence
verification
audit_logs
```

MongoDB may also store vector embeddings using:

# MongoDB Atlas Vector Search

This allows the MVP to avoid unnecessary extra vector databases.

Do NOT add PostgreSQL, Neo4j, Qdrant, Pinecone, etc. unless the team explicitly decides that they are required.

---

# 32. COMMON DATA FLOW

```text
MEMBER 1
Frontend
    ↓
MEMBER 2
FastAPI
    ↓
MEMBER 3
Classification + Routing
    ↓
MEMBER 4
Legal RAG
    ↓
MEMBER 3
LLM Generation
    ↓
MEMBER 5
Claim Verification
    ↓
MEMBER 5
Confidence + Abstention
    ↓
MEMBER 2
Final API Response
    ↓
MEMBER 1
Dashboard

MEMBER 6
supports database + testing + deployment
throughout the pipeline
```

---

# 33. SHARED FINAL JSON CONTRACT

All modules should work toward a common response structure similar to:

```json
{
  "classification": {
    "category": "",
    "reason": "",
    "confidence": 0
  },

  "ip": {
    "analysis": "",
    "flags": [],
    "evidence": []
  },

  "abs": {
    "applicable": false,
    "analysis": "",
    "evidence": []
  },

  "regulatory": {
    "jurisdiction": "India",
    "pathway": "",
    "steps": [],
    "evidence": []
  },

  "verification": {
    "total_claims": 0,
    "supported_claims": 0,
    "partially_supported_claims": 0,
    "unsupported_claims": []
  },

  "confidence": {
    "score": 0,
    "level": ""
  },

  "abstain": false
}
```

Exact fields may evolve slightly during integration, but do not redesign the entire structure unnecessarily.

---

# 34. FIVE-DAY MVP PLAN

## DAY 1 — FOUNDATION

### Member 1

* Landing page
* Innovation input
* Clarification UI

### Member 2

* FastAPI project
* Pydantic schemas
* Base endpoints

### Member 3

* Classification categories
* Clarification questions
* Routing logic

### Member 4

* Collect legal corpus (use Section 14A source list)
* PDF extraction
* Basic chunks

### Member 5

* Claim/evidence format
* Create verification test cases
* Sentence embeddings
* Cosine similarity
* Basic claim-to-evidence matching

### Member 6

* MongoDB Atlas setup
* GitHub setup
* Environment variables
* Base collections

### Day 1 milestone:

Every module has an independent basic version.

---

# 35. DAY 2 — CORE INTELLIGENCE

### Member 1

Complete input/clarification flow.

### Member 2

Connect frontend → backend → classifier.

### Member 3

Complete classification + routing.

### Member 4

Complete embeddings + vector retrieval + keyword search.

### Member 5

Implement:

```text
LLM Answer
↓
Claim Extraction
↓
Claim-by-Claim Evidence Matching
↓
Supported / Partial / Unsupported
```

### Member 6

Persist pipeline data in MongoDB.

### Day 2 milestone:

```text
User Input
→
Classification
→
Routing
→
Evidence Retrieval
```

works.

---

# 36. DAY 3 — FIRST END-TO-END MVP

### Member 1

Final dashboard.

### Member 2

Full pipeline integration.

### Member 3

Structured LLM generation.

### Member 4

Improve retrieval + filters.

### Member 5

Connect real:

```text
M3 LLM Answer
+
M4 Legal Evidence
```

into the verifier.

### Member 6

End-to-end testing and bug tracking.

### Day 3 milestone:

```text
Input
→
Classification
→
RAG
→
LLM
→
Verification
→
Report
```

works end-to-end.

---

# 37. DAY 4 — VERIFICATION + CONFIDENCE + POLISH

### Member 5 priority:

Implement:

* Stronger verification
* Confidence engine
* Abstention
* Unsupported claim handling
* Test thresholds

Other members:

* UI polish
* Retrieval testing
* API stability
* End-to-end testing

### Day 4 milestone:

Stable MVP.

---

# 38. DAY 5 — DEMO READY

No major new features.

Focus on:

* Bug fixes
* Deployment
* Test cases
* Demo scenario
* PPT
* Presentation
* Backup screenshots/video if necessary

Every member must understand:

* their module
* input
* output
* tech stack
* reason it exists

---

# 39. MVP MUST-HAVE FEATURES

The current MVP should prioritize:

* User innovation input
* 4–5 clarification questions
* Formulation classification
* Classification reasoning/confidence
* Decision routing
* IP pathway
* ABS pathway
* Regulatory pathway
* India legal corpus
* Legal RAG
* Citations
* Structured LLM roadmap
* Basic claim verification
* Confidence score
* Safe abstention
* Final dashboard
* Working frontend/backend/database

---

# 40. BUILD ONLY IF TIME REMAINS

Possible enhancements:

* Better BM25
* Cross-encoder reranking
* Stronger NLI verifier
* Human escalation summary
* Audit logging
* Hindi support

These must NOT block the core MVP.

---

# 41. DO NOT BUILD DURING THE 5-DAY MVP

Do NOT spend time on:

* Neo4j knowledge graph
* LangGraph multi-agent architecture
* Autonomous AI agents
* Full international regulatory system
* Many jurisdictions
* Mobile application
* Full expert marketplace
* Custom model training
* LLM fine-tuning
* Huge legal corpus
* Live TKDL integration unless access is actually available
* Voice interface
* Complex microservices architecture

A simple working system is better than an impressive architecture that does not work.

---

# 42. HARD SAFETY RULES

Every AI working on this project must follow these.

### Rule 1

Never fabricate:

* legal acts
* laws
* rules
* section numbers
* cases
* regulations
* regulatory authorities
* citations

---

### Rule 2

Never state legal outcomes as guaranteed.

Avoid:

* definitely
* guaranteed
* certainly eligible
* will receive patent
* will be approved

Prefer:

* may
* potentially
* likely based on available evidence
* requires further assessment

---

### Rule 3

Never present unsupported legal statements as facts.

---

### Rule 4

Every important legal/regulatory claim must have supporting evidence.

---

### Rule 5

Confidence must come from evidence signals, not LLM self-confidence.

---

### Rule 6

When evidence is weak:

## ABSTAIN.

---

### Rule 7

Never claim:

> "Legally validated by experts"

unless real experts have actually validated the system.

---

### Rule 8

Do not claim features that have not been implemented.

---

### Rule 9

Do not advertise Human Escalation as an actual live lawyer connection unless such a system exists.

---

### Rule 10

The tool provides:

## Decision Support

not:

## Final Legal Advice.

---

# 43. DATA-HANDLING RULE

Do not invent privacy claims.

The team must state only what is actually implemented.

For example, if data is stored in MongoDB for the MVP, do not claim:

> "We never store any user data."

Similarly, do not claim enterprise-level encryption/security systems unless implemented.

Be technically honest.

---

# 44. CORPUS FRESHNESS

Every legal source should preferably contain:

* authority
* year
* effective date where available
* source URL
* jurisdiction

The system should avoid presenting outdated legal material as definitely current.

---

# 45. FRONTEND UX RULE

Legal language should be converted into understandable language.

Preferred:

> "ABS — Access and Benefit Sharing — may need to be reviewed because your innovation uses a biological resource."

Avoid showing only:

> "ABS applicability triggered."

The user should understand what the system means.

---

# 46. MEMBER 5 — FIXED DAY 1 SCOPE

For Member 5 specifically, Day 1 is ONLY:

```text
Claim
+
Evidence
↓
Semantic Matching
↓
Best Evidence
↓
Initial Support Status
```

Technology:

```text
Python
sentence-transformers
cosine similarity
```

Do NOT build the entire confidence system on Day 1.

Do NOT integrate MongoDB.

Do NOT build FastAPI.

Do NOT build frontend.

Do NOT collect the main legal corpus.

Those belong to other members.

Day 1 success means:

> Given a test claim and several evidence passages, the verifier can find the most relevant evidence and return a preliminary support result.

---

# 47. MEMBER 5 — VERIFICATION INPUT CONTRACT

Member 3 should eventually provide:

```json
{
  "claims": [
    {
      "id": "claim_1",
      "text": ""
    }
  ]
}
```

Member 4 should provide:

```json
{
  "evidence": [
    {
      "id": "evidence_1",
      "text": "",
      "document": "",
      "section": "",
      "jurisdiction": "India",
      "source_url": ""
    }
  ]
}
```

Member 5 should produce:

```json
{
  "verification": [
    {
      "claim_id": "claim_1",
      "claim": "",
      "best_evidence_id": "evidence_1",
      "status": "supported",
      "score": 0.82
    }
  ]
}
```

Later this expands to confidence and abstention.

---

# 48. TESTING RULE

The team must create a fixed test set.

Especially test:

* Correct evidence
* Partially related evidence
* Completely unrelated evidence
* Contradictory evidence
* Missing evidence
* Wrong jurisdiction
* Leading questions
* Questions asking the system for certainty
* User trying to force unsupported conclusions

Do not keep changing the test set just to obtain better results.

---

# 49. DEMO SCENARIO

Recommended demo example:

> "I developed a modified Ashwagandha formulation using a new extraction process for stress relief."

The system should demonstrate:

```text
Input
↓
Clarification
↓
Classification
↓
IP / ABS / Regulatory Routing
↓
Legal Evidence Retrieval
↓
Structured AI Guidance
↓
Citation Verification
↓
Confidence
↓
Final Roadmap
```

This scenario allows most major features to be demonstrated together.

---

# 50. HOW EACH MEMBER SHOULD DESCRIBE THEIR ROLE

## Member 1

> "I build how the user interacts with the system."

## Member 2

> "I connect all system modules through the backend."

## Member 3

> "I handle classification, routing and evidence-grounded AI generation."

## Member 4

> "I provide the authoritative legal evidence through our RAG system."

## Member 5

> "I independently check whether the AI's claims are actually supported by the retrieved evidence and calculate confidence."

## Member 6

> "I manage database infrastructure, testing and deployment."

---

# 51. BUSINESS / FUTURE POSITIONING

Long term, IP-SAKTI Navigator may evolve into an:

## AI Innovation-to-Commercialization Intelligence Platform

Potential evolution:

```text
Idea
↓
Classification
↓
Prior Art
↓
IP Strategy
↓
TK / ABS
↓
Regulatory Pathway
↓
International Expansion
↓
Commercialization
```

Potential future customers:

* Ayurvedic startups
* Universities
* Research institutes
* Incubators
* Pharmaceutical companies
* AYUSH innovation centres
* IP/regulatory professionals

Possible business model:

* B2B SaaS
* Institutional subscription
* Enterprise/API licensing
* Premium innovator reports
* Expert-review marketplace in future

These are FUTURE directions, not current MVP capabilities.

---

# 52. CURRENT PROJECT TAGLINE

## Recommended technical tagline

> **Hybrid Legal RAG + LLM + Independent Claim Verification + Confidence-Based Abstention**

## Recommended pitch line

> **IP-SAKTI Navigator converts an Ayurvedic innovation into an evidence-backed IP, biodiversity and regulatory commercialization roadmap.**

## Strong judge-facing USP

> **We are not building another legal chatbot. We are building an evidence-first decision engine that tells an Ayurvedic innovator what pathway may apply, why it applies, what authoritative evidence supports it, and when the system does not have enough evidence to answer confidently.**

---

# 53. BEFORE ACCEPTING ANY AI-GENERATED OUTPUT

Every team member should check:

* [ ] Does it follow the fixed architecture?
* [ ] Does it remain within the 5-day MVP?
* [ ] Is it using our agreed tech stack?
* [ ] Is India the primary jurisdiction?
* [ ] Does it avoid inventing legal information?
* [ ] Does every legal claim have evidence?
* [ ] Does it avoid guaranteed legal outcomes?
* [ ] Does it preserve claim verification?
* [ ] Does it preserve confidence scoring?
* [ ] Does it preserve safe abstention?
* [ ] Does it avoid adding unnecessary databases/frameworks?
* [ ] Does it use the common JSON contracts?
* [ ] Is it describing only features that actually exist?

If any answer is NO:

## Correct the AI before using its output.

---

# 54. INSTRUCTION TO ANY AI TOOL

If you are an AI assistant reading this document:

1. Treat this document as the project's current source of truth.
2. Do not redesign the architecture unless explicitly requested.
3. Do not introduce scope creep.
4. Use the fixed technologies unless there is a genuine technical blocker.
5. When helping a team member, stay within that member's responsibility.
6. Explain code in beginner-friendly language when requested.
7. Never fabricate legal information.
8. Clearly distinguish dummy/test legal data from real authoritative evidence.
9. Prefer working MVP implementations over over-engineered solutions.
10. Preserve the project's evidence-verification and safe-abstention philosophy.
11. Do not mix India and international regulatory guidance.
12. Do not claim unimplemented functionality.
13. When suggesting changes, explicitly say whether they are:

* required for MVP,
* optional enhancement,
* or future scope.

14. For the current 5-day build, prioritize successful end-to-end integration.

---

# 55. CURRENT DEVELOPMENT PRIORITY

The team's current priority is NOT:

> Build the most sophisticated AI system possible.

It is:

> **Build one reliable end-to-end flow that demonstrates classification → routing → authoritative retrieval → AI generation → verification → confidence → roadmap.**

A smaller working system is preferred over a larger unfinished system.

---

# 56. FINAL RULE

Until the team intentionally changes this document:

# THIS DOCUMENT DEFINES THE PROJECT.

Any architectural, scope, terminology, module-responsibility, or major technology change must first be agreed upon by the team and then reflected here.

Do not allow individual AI sessions to independently redefine the project.
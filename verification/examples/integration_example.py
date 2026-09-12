"""
IP-SAKTI Navigator — Member 5 Integration Handoff Example.

Demonstrates complete data flow:
  M3 Generated Claims
          ↓
  M4 Legal Evidence Chunks
          ↓
  M5 Claim Verification Engine (`verify_claims`)
          ↓
  M5 Verification Output Payload (Structured JSON + confidence + abstention)
"""

import json
import os
import sys

# Ensure the repository root is in sys.path so `verification` is importable.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from verification import (
    calculate_abstention,
    calculate_confidence,
    validate_no_contradiction_detection,
    verify_claims,
)


def main():
    print("=" * 70)
    print("IP-SAKTI NAVIGATOR — MEMBER 5 VERIFICATION INTEGRATION EXAMPLE")
    print("=" * 70)

    # Step 1: Simulated M3 Output (Claims Payload)
    m3_output = {
        "jurisdiction": "India",
        "claims": [
            {
                "claim_id": "C1",
                "text": "The formulation uses Ashwagandha root extract as a biological resource.",
                "claim_type": "ABS",
                "jurisdiction": "India",
            },
            {
                "claim_id": "C2",
                "text": "A new solvent extraction process may warrant patentability review.",
                "claim_type": "IP",
                "jurisdiction": "India",
            },
        ],
    }

    # Step 2: Simulated M4 Output (Retrieved Legal Evidence Chunks)
    m4_output = {
        "jurisdiction": "India",
        "evidence": [
            {
                "evidence_id": "E1",
                "text": "Extraction of plant material from biological species requires ABS compliance under Section 3 of the Biological Diversity Act.",
                "document": "The Biological Diversity Act, 2002",
                "section": "Section 3",
                "jurisdiction": "India",
                "source_url": "https://nbaindia.org/act/",
                "authority": "National Biodiversity Authority",
                "effective_date": "2003-02-05",
                "legal_domain": "ABS",
            },
            {
                "evidence_id": "E2",
                "text": "A novel process of extraction not previously disclosed may be considered for patent protection under Section 2(1)(j).",
                "document": "The Patents Act, 1970",
                "section": "Section 2(1)(j)",
                "jurisdiction": "India",
                "source_url": "https://ipindia.gov.in/",
                "authority": "Indian Patent Office",
                "effective_date": "1970-09-19",
                "legal_domain": "Patent",
            },
            {
                "evidence_id": "E3",
                "text": "Cosmetic products must comply with safety labelling standards under the Cosmetic Rules.",
                "document": "Cosmetic Rules, 2020",
                "section": "Rule 34",
                "jurisdiction": "India",
                "source_url": "https://cdsco.gov.in/",
                "authority": "CDSCO",
                "effective_date": "2020-12-15",
                "legal_domain": "Cosmetics",
            },
        ],
    }

    print("\n[INPUT 1] M3 Claims:")
    print(json.dumps(m3_output, indent=2))

    print("\n[INPUT 2] M4 Evidence Chunks:")
    print(json.dumps(m4_output, indent=2))

    # Step 3: Execute M5 Verification Engine
    verification_result = verify_claims(
        claims=m3_output,
        evidence=m4_output,
        top_k=2,
        target_jurisdiction="India",
    )

    print("\n" + "=" * 70)
    print("[OUTPUT] M5 Verification Payload (Structured JSON):")
    print("=" * 70)
    print(json.dumps(verification_result, indent=2))

    # Step 4: Independent confidence + abstention (also embedded in the payload)
    print("\n" + "=" * 70)
    print("[OUTPUT] Confidence summary:")
    print("=" * 70)
    print(
        json.dumps(
            {
                "confidence": verification_result.get("confidence"),
                "abstain": verification_result.get("abstain"),
                "abstain_reason": verification_result.get("abstain_reason"),
            },
            indent=2,
        )
    )
    print("\nLimitation note:")
    print(validate_no_contradiction_detection())


if __name__ == "__main__":
    main()

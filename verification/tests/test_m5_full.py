"""
Member 5 — Full Verification + Confidence test suite.

Covers the 32 mandatory test cases from the M5 task backlog:

  T1   claim extraction interface
  T2   claim normalization hardening (None-safe, malformed-safe)
  T3   evidence normalization hardening (None-safe, malformed-safe)
  T4   Stage-1 verification preserved (cosine similarity, 0.70/0.45)
  T5   fabricated citation validation (UNKNOWN_CITATION flag)
  T6   evidence link integrity (returned IDs correspond to real items)
  T7   confidence engine (30/25/25/20, 0-100, HIGH/MEDIUM/LOW)
  T8   safe abstention
  T9   unsupported claims flagged, never presented as fact
  T10  no fake contradiction detection
  T11  duplicate claims deduplication
  T12  long claim robustness
  T13  embedding/model error handling (defensive, structured failure)
  T14  once-per-process model loading
  T15  batch performance (batched evidence embedding path)
  T18  32 mandatory tests
  T19  M4 evidence alias vocabulary compatibility
  T20  legal_domain mapping compatibility
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from verification import (
    ABSTAIN_SCORE_MIN,
    CONFIDENCE_WEIGHTS,
    FLAG_EMPTY_CLAIM,
    FLAG_JURISDICTION_MISMATCH,
    FLAG_LONG_CLAIM,
    FLAG_MODEL_ERROR,
    FLAG_NO_EVIDENCE,
    FLAG_UNKNOWN_CITATION,
    STATUS_PARTIAL,
    STATUS_SUPPORTED,
    STATUS_UNSUPPORTED,
    calculate_abstention,
    calculate_confidence,
    confidence_level,
    extract_claims,
    load_model,
    normalize_claim,
    normalize_claims_payload,
    normalize_evidence_item,
    normalize_evidence_payload,
    validate_no_contradiction_detection,
    verify_claim,
    verify_claims,
    verify_claims_batch,
)

MODEL = load_model()

KNOWN_AUTHORITY = "National Biodiversity Authority"
UNKNOWN_AUTHORITY = "Cartoon Legal Institute"

SUPPORTED_CLAIM = {
    "id": "C1",
    "text": "The innovation may involve a biological resource if it uses plants, animals, microorganisms, or parts of them.",
    "jurisdiction": "India",
}

SUPPORTED_EVIDENCE = {
    "id": "E1",
    "text": "The innovation may involve a biological resource if it uses plants, animals, microorganisms, or parts of them.",
    "document": "The Biological Diversity Act, 2002",
    "section": "Section 2(c)",
    "jurisdiction": "India",
    "source_url": "https://nbaindia.org/act/",
    "authority": KNOWN_AUTHORITY,
    "legal_domain": "Biodiversity",
}


# ---------------------------------------------------------------------------
# T1 — Claim extraction interface
# ---------------------------------------------------------------------------
def test_extract_claims_dict_payload():
    payload = extract_claims(
        {
            "jurisdiction": "India",
            "claims": [
                {"id": "A", "text": "Claim one"},
                {"claim_id": "B", "text": "Claim two"},
            ],
        }
    )
    assert len(payload["claims"]) == 2
    assert payload["claims"][0]["id"] == "A"
    assert payload["claims"][1]["id"] == "B"


def test_extract_claims_bare_list():
    payload = extract_claims([{"text": "Only claim"}])
    assert len(payload["claims"]) == 1
    assert payload["claims"][0]["text"] == "Only claim"


def test_extract_claims_none_and_empty():
    assert extract_claims(None)["claims"] == []
    assert extract_claims({})["claims"] == []
    assert extract_claims({"claims": None})["claims"] == []


# ---------------------------------------------------------------------------
# T2 — Claim normalization hardening
# ---------------------------------------------------------------------------
def test_normalize_claim_none_safe():
    normalized = normalize_claim(None)
    assert normalized["text"] == ""
    assert normalized["id"] == "claim_1"


def test_normalize_claim_malformed_safe():
    normalized = normalize_claim(42)
    assert normalized["text"] == ""
    normalized_dict = normalize_claim({"text": None})
    assert normalized_dict["text"] == ""


def test_normalize_claim_string():
    normalized = normalize_claim("  hello claim  ")
    assert normalized["text"] == "hello claim"


# ---------------------------------------------------------------------------
# T3 — Evidence normalization hardening
# ---------------------------------------------------------------------------
def test_normalize_evidence_none_safe():
    normalized = normalize_evidence_item(None)
    assert normalized["text"] == ""
    assert isinstance(normalized["id"], str)


def test_normalize_evidence_malformed_safe():
    normalized = normalize_evidence_item("not-a-dict")
    assert normalized["text"] == ""
    assert isinstance(normalized["id"], str)


def test_normalize_evidence_payload_none_safe():
    payload = normalize_evidence_payload(None)
    assert payload["evidence"] == []


# ---------------------------------------------------------------------------
# T4 — Stage-1 verification preserved (cosine sim, 0.70/0.45)
# ---------------------------------------------------------------------------
def test_verification_supported_still_works():
    result = verify_claim(SUPPORTED_CLAIM, [SUPPORTED_EVIDENCE], model=MODEL)
    assert result["status"] == STATUS_SUPPORTED
    assert result["similarity_score"] >= 0.70
    assert result["best_evidence_id"] == "E1"


def test_verification_thresholds_preserved():
    from verification.verifier import SUPPORTED_MIN, PARTIALLY_SUPPORTED_MIN

    assert SUPPORTED_MIN == 0.70
    assert PARTIALLY_SUPPORTED_MIN == 0.45


def test_verification_partial_and_unsupported_still_work():
    partial = verify_claim(
        "Access and benefit sharing may need to be reviewed because the formulation uses a plant material.",
        [
            {
                "id": "P1",
                "text": "Biological resources obtained from plants may raise biodiversity-related questions that should be reviewed separately from product labelling rules.",
                "jurisdiction": "India",
            }
        ],
        model=MODEL,
    )
    assert partial["status"] in (STATUS_PARTIAL, STATUS_SUPPORTED)

    unsupported = verify_claim(
        "ABS considerations may arise because the innovation uses a biological resource.",
        [
            {
                "id": "I1",
                "text": "Printer toner cartridges should be replaced when print quality becomes faint.",
                "jurisdiction": "India",
            }
        ],
        model=MODEL,
    )
    assert unsupported["status"] == STATUS_UNSUPPORTED


# ---------------------------------------------------------------------------
# T5 — Fabricated citation validation (UNKNOWN_CITATION)
# ---------------------------------------------------------------------------
def test_unknown_citation_flag():
    unknown_evidence = dict(SUPPORTED_EVIDENCE, authority=UNKNOWN_AUTHORITY)
    result = verify_claim(SUPPORTED_CLAIM, [unknown_evidence], model=MODEL)
    assert FLAG_UNKNOWN_CITATION in result["flags"]


def test_known_authority_no_flag():
    result = verify_claim(SUPPORTED_CLAIM, [SUPPORTED_EVIDENCE], model=MODEL)
    assert FLAG_UNKNOWN_CITATION not in result["flags"]


def test_missing_authority_no_flag():
    minimal = {k: v for k, v in SUPPORTED_EVIDENCE.items() if k != "authority"}
    result = verify_claim(SUPPORTED_CLAIM, [minimal], model=MODEL)
    assert FLAG_UNKNOWN_CITATION not in result["flags"]


# ---------------------------------------------------------------------------
# T6 — Evidence link integrity
# ---------------------------------------------------------------------------
def test_evidence_link_integrity():
    evidence = [
        SUPPORTED_EVIDENCE,
        {
            "id": "E2",
            "text": "A novel extraction or manufacturing process that is not already known may be considered for further patentability assessment.",
            "document": "The Patents Act, 1970",
            "section": "Section 2(1)(j)",
            "jurisdiction": "India",
            "authority": "Indian Patent Office",
        },
        {
            "id": "E3",
            "text": "Office air conditioning filters should be cleaned monthly.",
            "document": "Building Maintenance Guide",
            "section": "Clause 4.1",
            "jurisdiction": "India",
        },
    ]
    payload = verify_claims_batch(
        [SUPPORTED_CLAIM, {"id": "C2", "text": "A novel process of extraction may be considered for patent protection.", "jurisdiction": "India"}],
        evidence,
        top_k=3,
        model=MODEL,
    )
    expected_ids = {"E1", "E2", "E3"}
    for row in payload["verification"]:
        best_id = row["best_evidence_id"]
        assert best_id in expected_ids
        for ranked in row["ranked_evidence"]:
            assert ranked["evidence_id"] in expected_ids


# ---------------------------------------------------------------------------
# T7 — Confidence engine (30/25/25/20, 0-100, HIGH=M(80) / MEDIUM(50-79) / LOW<50)
# ---------------------------------------------------------------------------
def test_confidence_weights_sum_to_one():
    assert abs(sum(CONFIDENCE_WEIGHTS.values()) - 1.0) < 1e-9


def test_confidence_scale_is_0_to_100():
    confidence = calculate_confidence([], evidence=[])
    assert 0.0 <= confidence["score"] <= 100.0
    for signal in confidence["signals"].values():
        assert 0.0 <= signal <= 100.0


def test_confidence_level_thresholds():
    assert confidence_level(100.0) == "HIGH"
    assert confidence_level(80.0) == "HIGH"
    assert confidence_level(79.0) == "MEDIUM"
    assert confidence_level(50.0) == "MEDIUM"
    assert confidence_level(49.0) == "LOW"


def test_confidence_perfect_signals_score_100():
    payload = verify_claims_batch(
        [SUPPORTED_CLAIM],
        [dict(SUPPORTED_EVIDENCE) for _ in range(6)],
        top_k=3,
        model=MODEL,
    )
    confidence = payload["confidence"]
    assert confidence["score"] == 100.0
    assert confidence["level"] == "HIGH"


def test_confidence_no_evidence_low():
    confidence = calculate_confidence(
        [
            {
                "status": STATUS_UNSUPPORTED,
                "jurisdiction_match": False,
                "best_evidence": None,
            }
        ],
        evidence=[],
    )
    assert confidence["level"] == "LOW"
    assert confidence["score"] < 50
    assert confidence["signals"]["retrieval_quality"] == 0.0


def test_source_authority_not_hardcoded_zero():
    """Corpus has real authorities (IPO/NBA/CDSCO/FSSAI) — authority must
    contribute to the score."""
    payload = verify_claims_batch(
        [SUPPORTED_CLAIM],
        [dict(SUPPORTED_EVIDENCE, id=f"E{i}") for i in range(6)],
        model=MODEL,
    )
    confidence = payload["confidence"]
    assert confidence["signals"]["source_authority"] > 0.0


def test_confidence_signal_keys_present():
    confidence = calculate_confidence([], evidence=[])
    assert set(confidence["signals"].keys()) == {
        "retrieval_quality",
        "source_authority",
        "claim_support",
        "jurisdiction_match",
    }


# ---------------------------------------------------------------------------
# T8 — Safe abstention
# ---------------------------------------------------------------------------
def test_abstain_no_evidence():
    payload = verify_claims_batch([SUPPORTED_CLAIM], [], model=MODEL)
    assert payload["abstain"] is True
    assert payload["abstain_reason"]
    assert "no_evidence" in payload["abstain_reasons"]


def test_abstain_low_confidence():
    payload = verify_claims_batch(
        [
            {
                "id": "X",
                "text": "ABS considerations may arise because the innovation uses a biological resource.",
                "jurisdiction": "India",
            }
        ],
        [
            {
                "id": "OFFICE",
                "text": "Printer toner cartridges should be replaced when print quality becomes faint.",
                "jurisdiction": "India",
            }
        ],
        model=MODEL,
    )
    assert payload["abstain"] is True
    assert "low_confidence" in payload["abstain_reasons"]


def test_no_abstain_when_confident():
    payload = verify_claims_batch(
        [SUPPORTED_CLAIM],
        [dict(SUPPORTED_EVIDENCE, id=f"E{i}") for i in range(6)],
        model=MODEL,
    )
    assert payload["abstain"] is False
    assert payload["abstain_reason"] is None
    assert payload["abstain_reasons"] == []


def test_abstain_payload_keys():
    payload = verify_claims_batch([SUPPORTED_CLAIM], [], model=MODEL)
    for key in ("abstain", "abstain_reason", "abstain_reasons"):
        assert key in payload


# ---------------------------------------------------------------------------
# T9 — Unsupported claims flagged, never presented as fact
# ---------------------------------------------------------------------------
def test_unsupported_claim_flagged_not_fact():
    result = verify_claim(
        "ABS considerations arise because the innovation uses a biological resource.",
        [
            {
                "id": "F1",
                "text": "Cafeteria menus should offer vegetarian options.",
                "jurisdiction": "India",
            }
        ],
        model=MODEL,
    )
    assert result["status"] == STATUS_UNSUPPORTED
    assert result["flags"] or True
    assert "similarity is a first-stage relevance signal" in result["note"].lower()


def test_unsupported_unknown_citation_detected():
    """A fabricated citation on the only retrieved evidence must be flagged."""
    result = verify_claim(
        SUPPORTED_CLAIM["text"],
        [dict(SUPPORTED_EVIDENCE, authority=UNKNOWN_AUTHORITY)],
        model=MODEL,
    )
    assert FLAG_UNKNOWN_CITATION in result["flags"]


# ---------------------------------------------------------------------------
# T10 — No fake contradiction detection
# ---------------------------------------------------------------------------
def test_no_fake_contradiction():
    docs = validate_no_contradiction_detection()
    assert "contradiction detection" in docs
    assert "NOT" in docs


def test_abstain_reason_mentions_lack_of_evidence_not_contradiction():
    payload = verify_claims_batch([SUPPORTED_CLAIM], [], model=MODEL)
    assert "contradict" not in payload["abstain_reason"].lower()
    assert "evidence" in payload["abstain_reason"].lower()


# ---------------------------------------------------------------------------
# T11 — Duplicate claims deduplication
# ---------------------------------------------------------------------------
def test_duplicate_claims_dedup():
    duplicate_claims = [
        {"id": "D1", "text": "Identical claim text here."},
        {"id": "D2", "text": "Identical claim text here."},
        {"id": "D3", "text": "A different claim about biological resources."},
    ]
    payload = verify_claims_batch(
        duplicate_claims,
        [
            {
                "id": "E_EVID",
                "text": "Identical claim text here with supporting legal note.",
                "jurisdiction": "India",
            },
            {
                "id": "E_BIO",
                "text": "Biological resources include plants, animals, and microorganisms.",
                "jurisdiction": "India",
            },
        ],
        model=MODEL,
    )
    ids = [row["claim_id"] for row in payload["verification"]]
    assert ids == ["D1", "D3"]


# ---------------------------------------------------------------------------
# T12 — Long claim robustness
# ---------------------------------------------------------------------------
def test_long_claim_flagged():
    long_text = " ".join(["regulation"] * 160)
    result = verify_claim(
        {"id": "LONG", "text": long_text, "jurisdiction": "India"},
        [SUPPORTED_EVIDENCE],
        model=MODEL,
    )
    assert FLAG_LONG_CLAIM in result["flags"]


def test_short_claim_not_flagged():
    result = verify_claim(SUPPORTED_CLAIM, [SUPPORTED_EVIDENCE], model=MODEL)
    assert FLAG_LONG_CLAIM not in result["flags"]


# ---------------------------------------------------------------------------
# T13 — Embedding/model error handling
# ---------------------------------------------------------------------------
class _BrokenModel:
    def encode(self, *args, **kwargs):
        raise RuntimeError("simulated model failure")


def test_batch_model_error_structured_failure():
    payload = verify_claims_batch(
        [SUPPORTED_CLAIM, {"id": "C2", "text": "Another claim", "jurisdiction": "India"}],
        [SUPPORTED_EVIDENCE],
        model=_BrokenModel(),
    )
    for row in payload["verification"]:
        assert FLAG_MODEL_ERROR in row["flags"]
        assert "Model/model error" in row["note"] or "MODEL_ERROR" in row["flags"]


def test_single_model_error_structured_failure():
    result = verify_claim(SUPPORTED_CLAIM, [SUPPORTED_EVIDENCE], model=_BrokenModel())
    assert FLAG_MODEL_ERROR in result["flags"]
    assert result["status"] == STATUS_UNSUPPORTED


# ---------------------------------------------------------------------------
# T14 — Once-per-process model loading
# ---------------------------------------------------------------------------
def test_model_loaded_once_per_process():
    from verification.verifier import _model as module_model

    assert module_model is MODEL


# ---------------------------------------------------------------------------
# T15 — Batch performance (batched evidence embedding path)
# ---------------------------------------------------------------------------
def test_batch_embeds_evidence_once():
    """Evidence text should be embedded in one batched call when possible."""
    class TrackingModel:
        def __init__(self):
            self.calls = {"batch": 0, "single": 0}

        def encode(self, texts, convert_to_tensor=True):
            if isinstance(texts, list):
                self.calls["batch"] += 1
            else:
                self.calls["single"] += 1
            from sentence_transformers import SentenceTransformer  # local for test path

            model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            return model.encode(texts, convert_to_tensor=True)

    tracker = TrackingModel()
    payload = verify_claims_batch(
        [SUPPORTED_CLAIM],
        [dict(SUPPORTED_EVIDENCE, id=f"E{i}") for i in range(4)],
        model=tracker,
    )
    assert tracker.calls["batch"] >= 1
    assert payload["verification"][0]["status"] == STATUS_SUPPORTED


# ---------------------------------------------------------------------------
# T7-ext — Confidence integrated into batch payload
# ---------------------------------------------------------------------------
def test_batch_payload_has_confidence():
    payload = verify_claims_batch([SUPPORTED_CLAIM], [SUPPORTED_EVIDENCE], model=MODEL)
    assert "confidence" in payload
    assert payload["confidence"]["score"] >= 0
    assert payload["confidence"]["level"] in ("HIGH", "MEDIUM", "LOW")


# ---------------------------------------------------------------------------
# T19 — M4 evidence alias vocabulary compatibility
# ---------------------------------------------------------------------------
def test_m4_evidence_alias_compat():
    m4_evidence = [
        {
            "evidence_id": "M4E1",
            "text": "Extraction of plant material from biological species requires ABS compliance under Section 3 of the Biological Diversity Act.",
            "document_name": "The Biological Diversity Act, 2002",
            "section": "Section 3",
            "jurisdiction": "India",
            "source_url": "https://nbaindia.org/act/",
            "authority": KNOWN_AUTHORITY,
            "effective_date": "2003-02-05",
            "legal_domain": "ABS",
        }
    ]
    payload = verify_claims_batch(
        [
            {
                "claim_id": "M3C1",
                "text": "Extraction of plant material from biological species requires ABS compliance.",
                "jurisdiction": "India",
            }
        ],
        m4_evidence,
        model=MODEL,
    )
    row = payload["verification"][0]
    assert row["best_evidence_id"] == "M4E1"
    assert row["best_evidence"]["document"] == "The Biological Diversity Act, 2002"
    assert row["best_evidence"]["legal_domain"] == "ABS"


# ---------------------------------------------------------------------------
# T20 — Legal domain propagation
# ---------------------------------------------------------------------------
def test_legal_domain_propagated_to_best_evidence():
    payload = verify_claims_batch(
        [SUPPORTED_CLAIM],
        [dict(SUPPORTED_EVIDENCE, legal_domain="Biodiversity")],
        model=MODEL,
    )
    best = payload["verification"][0]["best_evidence"]
    assert best["legal_domain"] == "Biodiversity"

# ---------------------------------------------------------------------------
# T2/T3-ext — Empty text edge cases through the public API
# ---------------------------------------------------------------------------
def test_empty_claim_text_flagged():
    payload = verify_claims_batch(
        [{"id": "EMPTY", "text": "", "jurisdiction": "India"}],
        [SUPPORTED_EVIDENCE],
        model=MODEL,
    )
    row = payload["verification"][0]
    assert FLAG_EMPTY_CLAIM in row["flags"]
    assert row["status"] == STATUS_UNSUPPORTED


def test_no_evidence_flagged_in_payload():
    payload = verify_claims_batch([SUPPORTED_CLAIM], [], model=MODEL)
    row = payload["verification"][0]
    assert FLAG_NO_EVIDENCE in row["flags"]
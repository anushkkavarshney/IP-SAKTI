"""
Run from the repo root:
    pytest backend/tests/test_api.py -v
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_is_online():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "online"


def test_clarify_returns_questions():
    # As of the M3 LLM-wiring commit (b52e525), /clarify serves Member 3's
    # real 5-question clarification set (llm_pipeline/clarification.py),
    # with field_key = M3's own question id (q1..q5) -- see pipeline.py's
    # clarify() docstring for why that alignment matters functionally.
    res = client.post("/clarify", json={"description": "An Ashwagandha extract for stress relief."})
    assert res.status_code == 200
    body = res.json()
    assert len(body["questions"]) == 5
    assert body["questions"][0]["field_key"] == "q1"
    assert body["questions"][-1]["allow_text"] is True  # q5 is free-text jurisdiction


def test_analyze_rejects_empty_description():
    res = client.post(
        "/analyze",
        json={"innovation_description": "", "clarifications": {}, "jurisdiction": "India"},
    )
    assert res.status_code == 400


def test_analyze_missing_field_is_422():
    res = client.post("/analyze", json={"clarifications": {}})
    assert res.status_code == 422  # Pydantic validation error, not a 500


def test_analyze_end_to_end_ashwagandha_scenario():
    # Clarification keys are M3's own question ids (q1..q5) -- see
    # pipeline.py's clarify() docstring for why this alignment matters.
    payload = {
        "innovation_description": "A modified Ashwagandha formulation using a new extraction process for stress relief.",
        "clarifications": {
            "q1": "Medicine / therapeutic use",
            "q2": "Based on a classical formulation but modified",
            "q3": "Yes, a new process/technique",
            "q4": "Yes",
            "q5": "India",
        },
        "jurisdiction": "India",
    }
    res = client.post("/analyze", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["classification"]["category"] in [
        "Phytopharmaceutical",
        "Proprietary Ayurvedic Medicine",
        "Unknown / Insufficient Information",
    ]
    assert 0.0 <= body["classification"]["confidence"] <= 1.0
    assert isinstance(body["abs"]["applicable"], bool)
    assert "session_id" in body
    if body["abstain"]:
        assert body["abstain_reason"]


def test_report_not_found_for_unknown_session():
    res = client.get("/report/does-not-exist")
    assert res.status_code == 404


def test_report_roundtrip_after_analyze():
    payload = {
        "innovation_description": "A herbal face cream using known ingredients.",
        "clarifications": {"q1": "Cosmetic"},
        "jurisdiction": "India",
    }
    analyze_res = client.post("/analyze", json=payload)
    session_id = analyze_res.json()["session_id"]

    report_res = client.get(f"/report/{session_id}")
    assert report_res.status_code == 200
    assert report_res.json()["session_id"] == session_id

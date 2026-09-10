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
    res = client.post("/clarify", json={"description": "An Ashwagandha extract for stress relief."})
    assert res.status_code == 200
    body = res.json()
    assert len(body["questions"]) == 4
    assert body["questions"][0]["field_key"] == "intended_use"


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
    payload = {
        "innovation_description": "A modified Ashwagandha formulation using a new extraction process for stress relief.",
        "clarifications": {
            "intended_use": "therapeutic_internal",
            "classical_heritage": "modified_classical",
            "novel_process": "yes_novel_process",
            "biological_resource": "yes_biological",
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
    assert body["abs"]["applicable"] is True
    assert "session_id" in body
    # abstain is a valid bool either way depending on whether the demo
    # corpus has been ingested yet -- we only check the field exists and
    # is internally consistent with the reason.
    if body["abstain"]:
        assert body["abstain_reason"]


def test_report_not_found_for_unknown_session():
    res = client.get("/report/does-not-exist")
    assert res.status_code == 404


def test_report_roundtrip_after_analyze():
    payload = {
        "innovation_description": "A herbal face cream using known ingredients.",
        "clarifications": {"intended_use": "cosmetic_external"},
        "jurisdiction": "India",
    }
    analyze_res = client.post("/analyze", json=payload)
    session_id = analyze_res.json()["session_id"]

    report_res = client.get(f"/report/{session_id}")
    assert report_res.status_code == 200
    assert report_res.json()["session_id"] == session_id

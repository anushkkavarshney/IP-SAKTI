from fastapi import APIRouter

from ..schemas.requests import AnalyzeRequest
from ..schemas.responses import FinalRoadmapResponse
from ..services import pipeline, report_store
from ..utils.errors import bad_request

router = APIRouter()


@router.post("/analyze", response_model=FinalRoadmapResponse)
def analyze(request: AnalyzeRequest):
    if not request.innovation_description.strip():
        raise bad_request("innovation_description is required.")

    report = pipeline.analyze(
        innovation_description=request.innovation_description,
        clarifications=request.clarifications,
        jurisdiction=request.jurisdiction,
    )
    session_id = report_store.save(report)
    report["session_id"] = session_id
    return report

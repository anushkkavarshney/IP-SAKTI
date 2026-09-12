import logging
import uuid

from fastapi import APIRouter

from ..schemas.requests import AnalyzeRequest
from ..schemas.responses import FinalRoadmapResponse
from ..services import pipeline, report_store
from ..utils.errors import bad_request

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze", response_model=FinalRoadmapResponse)
def analyze(request: AnalyzeRequest):
    if not request.innovation_description.strip():
        raise bad_request("innovation_description is required.")

    report = pipeline.analyze(
        innovation_description=request.innovation_description,
        clarifications=request.clarifications,
        jurisdiction=request.jurisdiction,
    )
    try:
        session_id = report_store.save(report)
    except RuntimeError:
        logger.warning("Report persistence unavailable; returning transient MVP session_id")
        session_id = str(uuid.uuid4())
    report["session_id"] = session_id
    return report

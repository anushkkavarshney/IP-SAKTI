from fastapi import APIRouter

from ..schemas.responses import FinalRoadmapResponse
from ..services import report_store
from ..utils.errors import not_found

router = APIRouter()


@router.get("/report/{session_id}", response_model=FinalRoadmapResponse)
def get_report(session_id: str):
    report = report_store.get(session_id)
    if report is None:
        raise not_found(f"No report found for session_id '{session_id}'.")
    return report

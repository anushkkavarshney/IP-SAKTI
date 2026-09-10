from fastapi import APIRouter

from ..schemas.requests import ClarifyRequest
from ..schemas.responses import ClarifyResponse
from ..services import pipeline

router = APIRouter()


@router.post("/clarify", response_model=ClarifyResponse)
def clarify(request: ClarifyRequest):
    questions = pipeline.clarify(request.description)
    return {"questions": questions}

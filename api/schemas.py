"""
Pydantic Schemas for IP-SAKTI API Request and Response Models.
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class AnalysisRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3


class AnalysisResponse(BaseModel):
    status: str
    query: str
    matched_entities: List[str]
    system_prompt: str
    user_prompt: str
    evidence: List[Dict[str, Any]]
    guardrail_check: Dict[str, Any]
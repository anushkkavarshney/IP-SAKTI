"""
Request schemas for Member 2's backend.

These mirror what the frontend actually sends (see frontend/src/lib/api.ts
and frontend/src/types/roadmap.ts) so we don't need to guess field names.
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field


class ClarifyRequest(BaseModel):
    """Body sent by frontend to POST /clarify (see lib/api.ts: getClarificationQuestions)."""
    description: str = Field(default="", description="Raw innovation description typed by the user so far.")


class AnalyzeRequest(BaseModel):
    """Body sent by frontend to POST /analyze (matches AnalyzePayload in types/roadmap.ts)."""
    preset_id: Optional[str] = None  # "ashwagandha" | "triphala" | "abstention" | "custom"
    innovation_description: str
    clarifications: Dict[str, str] = Field(default_factory=dict)
    jurisdiction: str = "India"

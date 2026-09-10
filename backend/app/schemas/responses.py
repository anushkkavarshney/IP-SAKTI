"""
Response schemas for Member 2's backend.

IMPORTANT: These are deliberately a 1:1 mirror of
frontend/src/types/roadmap.ts (Member 1's contract) rather than only the
shorter skeleton in Roadmap.md Section 33 -- the frontend type is what
actually gets rendered, so matching it is what makes /analyze "just work"
against the existing UI without frontend changes.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ClarificationOption(BaseModel):
    value: str
    label: str
    hint: Optional[str] = None


class ClarificationQuestion(BaseModel):
    id: str
    question: str
    field_key: str
    description: str
    options: List[ClarificationOption] = Field(default_factory=list)
    allow_text: Optional[bool] = None


class ClarifyResponse(BaseModel):
    questions: List[ClarificationQuestion]


class LegalEvidenceChunk(BaseModel):
    id: Optional[str] = None
    jurisdiction: str
    legal_domain: str  # "Patent" | "Biodiversity / ABS" | "AYUSH / Drug" | "Nutraceutical / Food" | "Cosmetic"
    document_name: str
    section: str
    authority: str
    effective_date: Optional[str] = None
    source_url: str
    text: str


class ClassificationResult(BaseModel):
    category: str  # one of the 6 roadmap categories, see services/classification_stub.py
    reason: str
    confidence: float


class IPAnalysisResult(BaseModel):
    analysis: str
    flags: List[str] = Field(default_factory=list)
    evidence: List[LegalEvidenceChunk] = Field(default_factory=list)
    patentability_considerations: Optional[List[str]] = None
    traditional_knowledge_flags: Optional[List[str]] = None


class ABSAnalysisResult(BaseModel):
    applicable: bool
    analysis: str
    evidence: List[LegalEvidenceChunk] = Field(default_factory=list)
    biological_resource_identified: Optional[str] = None
    nba_action_items: Optional[List[str]] = None


class RegulatoryStep(BaseModel):
    step_number: int
    title: str
    authority: str
    description: str
    requirements: Optional[List[str]] = None


class RegulatoryAnalysisResult(BaseModel):
    jurisdiction: str
    pathway: str
    steps: List[RegulatoryStep] = Field(default_factory=list)
    evidence: List[LegalEvidenceChunk] = Field(default_factory=list)


class ClaimVerificationItem(BaseModel):
    claim_id: str
    claim: str
    best_evidence_id: Optional[str] = None
    status: str  # "supported" | "partially_supported" | "unsupported"
    score: float
    explanation: Optional[str] = None
    evidence_snippet: Optional[str] = None
    source_document: Optional[str] = None
    source_section: Optional[str] = None


class VerificationSummary(BaseModel):
    total_claims: int
    supported_claims: int
    partially_supported_claims: int
    unsupported_claims: List[str] = Field(default_factory=list)
    items: Optional[List[ClaimVerificationItem]] = None


class ConfidenceSignals(BaseModel):
    retrieval_quality: float
    source_authority: float
    claim_support: float
    jurisdiction_match: float


class ConfidenceResult(BaseModel):
    score: float
    level: str  # "HIGH" | "MEDIUM" | "LOW"
    signals: Optional[ConfidenceSignals] = None
    note: Optional[str] = None

class ExpertEscalation(BaseModel):
    recommended: bool
    reason: str
    key_questions_for_counsel: List[str] = Field(default_factory=list)


class FinalRoadmapResponse(BaseModel):
    classification: ClassificationResult
    ip: IPAnalysisResult
    abs: ABSAnalysisResult
    regulatory: RegulatoryAnalysisResult
    verification: VerificationSummary
    confidence: ConfidenceResult
    abstain: bool
    abstain_reason: Optional[str] = None
    expert_escalation: Optional[ExpertEscalation] = None
    # Extra field, not in the frontend type but harmless to include (TS only
    # checks the fields it reads) -- lets /report/{id} retrieve this later.
    session_id: Optional[str] = None

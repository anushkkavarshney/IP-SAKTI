/**
 * Shared Type Definitions for IP-SAKTI Navigator
 * Strictly aligned with roadmap.md (Master AI Working Brief - SIH 2026 Problem Statement SIH26045)
 */

export type FormulationCategory =
  | "Classical Ayurvedic Medicine"
  | "Proprietary Ayurvedic Medicine"
  | "Phytopharmaceutical"
  | "Nutraceutical"
  | "Cosmetic"
  | "Unknown / Insufficient Information";

export type VerificationStatus =
  | "supported"
  | "partially_supported"
  | "unsupported";

export type ConfidenceLevel = "HIGH" | "MEDIUM" | "LOW";

export interface LegalEvidenceChunk {
  id?: string;
  jurisdiction: string;
  legal_domain: "Patent" | "Biodiversity / ABS" | "AYUSH / Drug" | "Nutraceutical / Food" | "Cosmetic";
  document_name: string;
  section: string;
  authority: string;
  effective_date?: string;
  source_url: string;
  text: string;
}

export interface ClaimVerificationItem {
  claim_id: string;
  claim: string;
  best_evidence_id?: string;
  status: VerificationStatus;
  score: number;
  explanation?: string;
  evidence_snippet?: string;
  source_document?: string;
  source_section?: string;
}

export interface ClassificationResult {
  category: FormulationCategory;
  reason: string;
  confidence: number;
}

export interface IPAnalysisResult {
  analysis: string;
  flags: string[];
  evidence: LegalEvidenceChunk[];
  patentability_considerations?: string[];
  traditional_knowledge_flags?: string[];
}

export interface ABSAnalysisResult {
  applicable: boolean;
  analysis: string;
  evidence: LegalEvidenceChunk[];
  biological_resource_identified?: string;
  nba_action_items?: string[];
}

export interface RegulatoryStep {
  step_number: number;
  title: string;
  authority: string;
  description: string;
  requirements?: string[];
}

export interface RegulatoryAnalysisResult {
  jurisdiction: string;
  pathway: string;
  steps: RegulatoryStep[];
  evidence: LegalEvidenceChunk[];
}

export interface VerificationSummary {
  total_claims: number;
  supported_claims: number;
  partially_supported_claims: number;
  unsupported_claims: string[];
  items?: ClaimVerificationItem[];
}

export interface ConfidenceSignals {
  retrieval_quality: number; // 30% weight
  source_authority: number;  // 25% weight
  claim_support: number;     // 25% weight
  jurisdiction_match: number;// 20% weight
}

export interface ConfidenceResult {
  score: number;
  level: ConfidenceLevel;
  signals?: ConfidenceSignals;
}

export interface FinalRoadmapResponse {
  classification: ClassificationResult;
  ip: IPAnalysisResult;
  abs: ABSAnalysisResult;
  regulatory: RegulatoryAnalysisResult;
  verification: VerificationSummary;
  confidence: ConfidenceResult;
  abstain: boolean;
  abstain_reason?: string;
  expert_escalation?: {
    recommended: boolean;
    reason: string;
    key_questions_for_counsel: string[];
  };
}

export interface ClarificationQuestion {
  id: string;
  question: string;
  field_key: string;
  description: string;
  options: {
    value: string;
    label: string;
    hint?: string;
  }[];
  allow_text?: boolean;
}

export interface ClarificationAnswers {
  [key: string]: string;
}

export type PresetScenarioId = "ashwagandha" | "triphala" | "abstention" | "custom";

export interface AnalyzePayload {
  preset_id?: PresetScenarioId;
  innovation_description: string;
  clarifications: ClarificationAnswers;
  jurisdiction: string;
}


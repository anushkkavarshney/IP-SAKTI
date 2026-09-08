import {
  AnalyzePayload,
  ClarificationAnswers,
  ClarificationQuestion,
  FinalRoadmapResponse,
} from "../types/roadmap";
import {
  CLARIFICATION_QUESTIONS,
  getMockRoadmapByScenario,
} from "./mockData";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_API_URL || "http://localhost:8000";

/**
 * Interface with Member 2's FastAPI backend
 * Gracefully falls back to authoritative mock data when backend is not running.
 */
export async function getClarificationQuestions(
  innovationDescription?: string
): Promise<{ questions: ClarificationQuestion[]; isLiveBackend: boolean }> {
  try {
    const res = await fetch(`${BACKEND_URL}/clarify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description: innovationDescription || "" }),
    });

    if (res.ok) {
      const data = await res.json();
      return {
        questions: data.questions || CLARIFICATION_QUESTIONS,
        isLiveBackend: true,
      };
    }
  } catch {
    // Backend offline; fallback to roadmap.md standard questions
  }

  return {
    questions: CLARIFICATION_QUESTIONS,
    isLiveBackend: false,
  };
}

/**
 * Submit complete payload to FastAPI /analyze endpoint
 * Gracefully routes to the selected demo scenario if offline.
 */
export async function analyzeInnovation(
  payload: AnalyzePayload
): Promise<{ report: FinalRoadmapResponse; isLiveBackend: boolean; isSampleData: boolean }> {
  try {
    const res = await fetch(`${BACKEND_URL}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      const data = await res.json();
      return {
        report: data,
        isLiveBackend: true,
        isSampleData: false,
      };
    }
  } catch {
    // Backend offline: Use centralized mock selector responding to preset and clarification answers
  }

  const mockReport = getMockRoadmapByScenario(payload);
  return {
    report: mockReport,
    isLiveBackend: false,
    isSampleData: true,
  };
}

/**
 * Retrieve saved report by session ID from FastAPI /report/{session_id}
 */
export async function getReportById(
  sessionId: string
): Promise<FinalRoadmapResponse | null> {
  try {
    const res = await fetch(`${BACKEND_URL}/report/${sessionId}`);
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // Offline fallback
  }
  return null;
}

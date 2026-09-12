import {
  AnalyzePayload,
  ClarificationQuestion,
  FinalRoadmapResponse,
} from "../types/roadmap";
import {
  CLARIFICATION_QUESTIONS,
  getMockRoadmapByScenario,
} from "./mockData";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_API_URL || "http://localhost:8000";

const DEFAULT_TIMEOUT_MS = 15000;
const ANALYZE_TIMEOUT_MS = 120000;
const NETWORK_ERROR_WORD =
  "We couldn't connect to the analysis service. Check that the backend is running and try again.";

export type ApiErrorKind =
  | "network"
  | "timeout"
  | "aborted"
  | "http"
  | "empty"
  | "malformed"
  | "unavailable"
  | "unknown";

export class ApiError extends Error {
  kind: ApiErrorKind;
  status?: number;

  constructor(kind: ApiErrorKind, message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.kind = kind;
    this.status = status;
  }
}

export function apiErrorMessage(err: unknown): string {
  if (err instanceof ApiError) {
    switch (err.kind) {
      case "network":
        return NETWORK_ERROR_WORD;
      case "timeout":
        return "The analysis service took too long to respond. It may be busy — please retry.";
      case "aborted":
        return "The request was cancelled.";
      case "http":
        if (err.status && err.status >= 500) {
          return "The analysis service hit an internal error. Please retry in a moment.";
        }
        if (err.status && err.status >= 400) {
          return "The analysis service couldn't process this request. Please review your input and try again.";
        }
        return "The analysis service returned an unexpected response.";
      case "empty":
        return "The analysis service returned an empty response.";
      case "unavailable":
        return err.message;
      case "malformed":
        return "The analysis service returned an incomplete or unexpected response.";
      default:
        return "Something went wrong while reaching the analysis service.";
    }
  }
  return "Something went wrong while reaching the analysis service.";
}

export function apiErrorTitle(err: unknown): string {
  if (err instanceof ApiError) {
    switch (err.kind) {
      case "network":
      case "timeout":
        return "Analysis service unavailable";
      case "http":
        return "Analysis could not be completed";
      case "unavailable":
        return "Analysis service unavailable";
      case "empty":
      case "malformed":
        return "Incomplete response from the analysis service";
      default:
        return "Something went wrong";
    }
  }
  return "Something went wrong";
}

type FetchOptions = RequestInit & {
  timeoutMs?: number;
  signal?: AbortSignal;
};

async function fetchJson(url: string, options: FetchOptions): Promise<unknown> {
  const controller = new AbortController();
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  let externallyAborted = false;
  const { signal: externalSignal } = options;
  if (externalSignal) {
    if (externalSignal.aborted) {
      clearTimeout(timer);
      throw new ApiError("aborted", "Request was cancelled.");
    }
    const onAbort = () => {
      externallyAborted = true;
      controller.abort();
    };
    externalSignal.addEventListener("abort", onAbort, { once: true });
  }

  let res: Response;
  try {
    res = await fetch(url, { ...options, signal: controller.signal });
  } catch {
    if (externallyAborted) {
      throw new ApiError("aborted", "Request was cancelled.");
    }
    if (controller.signal.aborted) {
      throw new ApiError("timeout", "Request timed out.");
    }
    throw new ApiError("network", NETWORK_ERROR_WORD);
  } finally {
    clearTimeout(timer);
  }

  if (!res.ok) {
    throw new ApiError("http", `HTTP ${res.status}`, res.status);
  }

  const text = await res.text();
  if (!text.trim()) {
    throw new ApiError("empty", "Empty response body.");
  }

  let data: unknown;
  try {
    data = JSON.parse(text);
  } catch {
    throw new ApiError("malformed", "Response body was not valid JSON.");
  }
  return data;
}

function isRoadmapResponse(value: unknown): value is FinalRoadmapResponse {
  if (!value || typeof value !== "object") return false;
  const v = value as Partial<FinalRoadmapResponse>;
  return (
    !!v.classification &&
    typeof v.classification === "object" &&
    !!v.classification.category &&
    !!v.confidence &&
    typeof v.confidence === "object" &&
    typeof v.confidence.score === "number" &&
    !!v.verification &&
    typeof v.verification === "object"
  );
}

export interface ClarifyResult {
  questions: ClarificationQuestion[];
  isLiveBackend: boolean;
}

/**
 * Fetch clarification questions. The standard 5-question set doubles as the
 * offline fallback, so a failed probe does not block the flow — it just means
 * the default questions are used.
 */
export async function getClarificationQuestions(
  innovationDescription?: string,
  externalSignal?: AbortSignal
): Promise<ClarifyResult> {
  try {
    const data = await fetchJson(`${BACKEND_URL}/clarify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description: innovationDescription || "" }),
      timeoutMs: DEFAULT_TIMEOUT_MS,
      signal: externalSignal,
    });
    const list = (data as { questions?: unknown })?.questions;
    if (Array.isArray(list) && list.length > 0) {
      return { questions: list as ClarificationQuestion[], isLiveBackend: true };
    }
  } catch {
    // Backend offline — fall back to the standard question set.
  }
  return { questions: CLARIFICATION_QUESTIONS, isLiveBackend: false };
}

export interface AnalyzeResult {
  report: FinalRoadmapResponse;
  isLiveBackend: boolean;
}

const SERVICE_UNAVAILABLE_MARKERS = [
  "service is currently unavailable",
  "Classification/generation service unavailable",
  "missing dependency or API key",
] as const;

/**
 * The backend's _llm_unavailable_report() is an all-zero abstain object it
 * returns with HTTP 200 when the LLM dependency/API key is missing. It is an
 * infrastructure failure, not a genuine abstention, so we surface it as an
 * error and let the user retry or opt into sample data.
 */
function isServiceUnavailableReport(report: FinalRoadmapResponse): boolean {
  const haystack = [
    report.abstain_reason || "",
    report.classification.reason || "",
  ]
    .join("\n")
    .toLowerCase();
  return (
    report.abstain === true &&
    SERVICE_UNAVAILABLE_MARKERS.some((marker) =>
      haystack.includes(marker.toLowerCase())
    )
  );
}

/**
 * Submit a complete payload to POST /analyze.
 *
 * NOTE: this intentionally THROWS on failure instead of silently returning
 * mock data. The caller decides whether to show an error state or let the user
 * opt into sample data via getMockRoadmap().
 */
export async function analyzeInnovation(
  payload: AnalyzePayload,
  externalSignal?: AbortSignal
): Promise<AnalyzeResult> {
  const data = await fetchJson(`${BACKEND_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    timeoutMs: ANALYZE_TIMEOUT_MS,
    signal: externalSignal,
  });

  if (!isRoadmapResponse(data)) {
    throw new ApiError("malformed", "Analyze response did not match the roadmap contract.");
  }

  if (isServiceUnavailableReport(data)) {
    throw new ApiError(
      "unavailable",
      "The backend is reachable, but its LLM classification service can't start because the groq dependency or GROQ_API_KEY is missing. Retry once it's configured, or use sample data to see the demo roadmap now. Sample data is clearly marked as illustrative and is never presented as a live result."
    );
  }

  return { report: data, isLiveBackend: true };
}

/** Explicit opt-in to sample data (shown with a clear illustrative banner). */
export function getMockRoadmap(
  payload: AnalyzePayload
): AnalyzeResult {
  return {
    report: getMockRoadmapByScenario(payload),
    isLiveBackend: false,
  };
}

export async function getReportById(
  sessionId: string,
  externalSignal?: AbortSignal
): Promise<FinalRoadmapResponse | null> {
  try {
    const data = await fetchJson(`${BACKEND_URL}/report/${sessionId}`, {
      method: "GET",
      timeoutMs: DEFAULT_TIMEOUT_MS,
      signal: externalSignal,
    });
    if (isRoadmapResponse(data)) return data;
    return null;
  } catch {
    return null;
  }
}
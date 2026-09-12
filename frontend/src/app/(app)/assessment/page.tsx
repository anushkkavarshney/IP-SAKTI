"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import InnovationInput from "@/components/InnovationInput";
import ClarificationWizard from "@/components/ClarificationWizard";
import PipelineLoader from "@/components/PipelineLoader";
import RoadmapDashboard from "@/components/RoadmapDashboard";
import AnalysisError, {
  AnalysisErrorInfo,
  toAnalysisError,
} from "@/components/AnalysisError";
import {
  AnalyzePayload,
  ClarificationAnswers,
  ClarificationQuestion,
  FinalRoadmapResponse,
  PresetScenarioId,
} from "@/types/roadmap";
import {
  analyzeInnovation,
  getClarificationQuestions,
  getMockRoadmap,
} from "@/lib/api";
import { CLARIFICATION_QUESTIONS } from "@/lib/mockData";
import { AssessmentRecord } from "@/types/assessment";
import { saveReport } from "@/lib/storage";
import { truncate } from "@/lib/utils";

type Step = "input" | "clarifying" | "loading" | "dashboard" | "error";

interface CachedSession {
  roadmap: FinalRoadmapResponse;
  description: string;
  isSampleData: boolean;
  record: AssessmentRecord;
}

let cachedSession: CachedSession | null = null;

function toRecord(
  roadmap: FinalRoadmapResponse,
  description: string,
  isSampleData: boolean
): AssessmentRecord {
  const verification = roadmap.verification;
  const claims = verification.items?.length ?? verification.total_claims ?? 0;
  const id =
    typeof crypto !== "undefined" && typeof crypto.randomUUID === "function"
      ? crypto.randomUUID()
      : `report-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  return {
    id,
    title: truncate(description, 72) || "Untitled assessment",
    createdAt: new Date().toISOString(),
    classification: roadmap.classification?.category ?? "Unknown / Insufficient Information",
    confidence: roadmap.confidence?.score ?? 0,
    confidenceLevel: roadmap.confidence?.level ?? "LOW",
    abstained: roadmap.abstain ?? false,
    abstainReason: roadmap.abstain_reason,
    summary: roadmap.classification?.reason,
    isSampleData,
    verification: {
      total: claims,
      supported: verification.supported_claims ?? 0,
      partial: verification.partially_supported_claims ?? 0,
      unsupported: verification.unsupported_claims?.length ?? 0,
    },
  };
}

export default function AssessmentPage() {
  const router = useRouter();

  const [step, setStep] = useState<Step>("input");
  const [description, setDescription] = useState("");
  const [presetId, setPresetId] = useState<PresetScenarioId>("custom");
  const [questions, setQuestions] = useState<ClarificationQuestion[] | null>(null);
  const [answers, setAnswers] = useState<ClarificationAnswers>({});
  const [roadmap, setRoadmap] = useState<FinalRoadmapResponse | null>(null);
  const [isSampleData, setIsSampleData] = useState(false);
  const [error, setError] = useState<AnalysisErrorInfo | null>(null);

  const abortRef = useRef<AbortController | null>(null);
  const answersRef = useRef<ClarificationAnswers>({});
  const descriptionRef = useRef("");
  const presetRef = useRef<PresetScenarioId>("custom");

  const initialStep = useRef(false);

  // Restore or redirect based on the ?step= URL on first mount only.
  useEffect(() => {
    if (initialStep.current) return;
    initialStep.current = true;

    const rawStep =
      typeof window !== "undefined"
        ? new URLSearchParams(window.location.search).get("step")
        : null;
    if (rawStep === "dashboard") {
      if (cachedSession) {
        const session = cachedSession;
        // eslint-disable-next-line react-hooks/set-state-in-effect -- restores a cached in-memory session on client mount
        setDescription(session.description);
        setRoadmap(session.roadmap);
        setIsSampleData(session.isSampleData);
        setStep("dashboard");
      } else {
        router.replace("/assessment");
      }
    } else if (rawStep === "clarifying") {
      if (descriptionRef.current) {
        setStep("clarifying");
      } else {
        router.replace("/assessment");
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Prefetch clarification questions so the Wizard is ready when reached.
  useEffect(() => {
    let active = true;
    getClarificationQuestions().then((result) => {
      if (active) setQuestions(result.questions);
    });
    return () => {
      active = false;
    };
  }, []);

  const cancelInFlight = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
  }, []);

  useEffect(() => cancelInFlight, [cancelInFlight]);

  const presentRoadmap = useCallback(
    (
      result: { report: FinalRoadmapResponse },
      desc: string,
      sample: boolean
    ) => {
      const record = toRecord(result.report, desc, sample);
      saveReport(record);
      cachedSession = { roadmap: result.report, description: desc, isSampleData: sample, record };
      setDescription(desc);
      setRoadmap(result.report);
      setIsSampleData(sample);
      setError(null);
      router.replace("/assessment?step=dashboard");
      setStep("dashboard");
      window.scrollTo({ top: 0 });
    },
    [router]
  );

  const runAnalysis = useCallback(
    async (ans: ClarificationAnswers) => {
      cancelInFlight();
      const controller = new AbortController();
      abortRef.current = controller;
      setStep("loading");
      setError(null);

      answersRef.current = ans;
      const desc = descriptionRef.current;
      const preset = presetRef.current;
      const payload: AnalyzePayload = {
        preset_id: preset === "custom" ? undefined : preset,
        innovation_description: desc,
        clarifications: ans,
        jurisdiction: "India",
      };

      try {
        const result = await analyzeInnovation(payload, controller.signal);
        const sample = !result.isLiveBackend;
        presentRoadmap(result, desc, sample);
      } catch (err) {
        if (err instanceof DOMException && err.name === "AbortError") return;
        if (abortRef.current?.signal.aborted) return;
        setError(toAnalysisError(err));
        setStep("error");
      } finally {
        if (abortRef.current === controller) abortRef.current = null;
      }
    },
    [cancelInFlight, presentRoadmap]
  );

  const setAnswersRefFromPreset = useCallback(
    (preset: PresetScenarioId, desc: string) => {
      const lower = desc.toLowerCase();
      const next: ClarificationAnswers = {
        intended_use: "therapeutic_internal",
        classical_heritage:
          preset === "triphala" || lower.includes("triphala")
            ? "classical_exact"
            : preset === "abstention" ||
              lower.includes("guaranteed") ||
              lower.includes("miracle")
            ? "completely_new"
            : "classical_modified",
        novel_extraction:
          preset === "abstention" ? "unsure_process" : "novel_process_claimed",
        biological_resources: "indian_wild_cultivated",
        jurisdiction: "india_primary",
      };
      answersRef.current = next;
      setAnswers(next);
    },
    []
  );

  const handleInputSubmit = useCallback(
    (desc: string, preset: PresetScenarioId) => {
      descriptionRef.current = desc;
      presetRef.current = preset;
      setDescription(desc);
      setPresetId(preset);
      setAnswersRefFromPreset(preset, desc);
      router.replace("/assessment?step=clarifying");
      setStep("clarifying");
      window.scrollTo({ top: 0 });
    },
    [router, setAnswersRefFromPreset]
  );

  const handleClarifySubmit = useCallback(
    (ans: ClarificationAnswers) => {
      void runAnalysis(ans);
    },
    [runAnalysis]
  );

  const handleBackToInput = useCallback(() => {
    cancelInFlight();
    cachedSession = null;
    setRoadmap(null);
    setError(null);
    router.replace("/assessment");
    setStep("input");
  }, [cancelInFlight, router]);

  const handleUseSample = useCallback(() => {
    const payload: AnalyzePayload = {
      preset_id: presetRef.current === "custom" ? undefined : presetRef.current,
      innovation_description: descriptionRef.current,
      clarifications: answersRef.current,
      jurisdiction: "India",
    };
    const result = getMockRoadmap(payload);
    presentRoadmap(result, descriptionRef.current, true);
  }, [presentRoadmap]);

  // Roadmap jump links need the sections in the DOM; the Sidebar relies on
  // the dashboard step staying URL-encoded.
  const effectiveQuestions = questions ?? CLARIFICATION_QUESTIONS;

  return (
    <div className="space-y-8">
      {step === "input" && (
        <InnovationInput
          initialValue={description}
          initialPreset={presetId}
          onSubmit={handleInputSubmit}
        />
      )}

      {step === "clarifying" && (
        <ClarificationWizard
          questions={effectiveQuestions}
          initialAnswers={answers}
          innovationDescription={description}
          presetId={presetId}
          onBackToInput={handleBackToInput}
          onSubmitForAnalysis={handleClarifySubmit}
        />
      )}

      {step === "loading" && (
        <PipelineLoader detail="POST /analyze · awaiting response" />
      )}

      {step === "dashboard" && roadmap && (
        <RoadmapDashboard
          roadmap={roadmap}
          innovationDescription={description}
          isSampleData={isSampleData}
          onReset={handleBackToInput}
        />
      )}

      {step === "error" && error && (
        <AnalysisError
          error={error}
          onRetry={() => void runAnalysis(answersRef.current)}
          onUseSample={handleUseSample}
          onBack={handleBackToInput}
        />
      )}
    </div>
  );
}
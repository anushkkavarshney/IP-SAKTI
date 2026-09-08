"use client";

import React, { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import DisclaimerModal from "../components/DisclaimerModal";
import LandingHero from "../components/LandingHero";
import InnovationInput from "../components/InnovationInput";
import ClarificationWizard from "../components/ClarificationWizard";
import PipelineLoader from "../components/PipelineLoader";
import RoadmapDashboard from "../components/RoadmapDashboard";
import {
  ClarificationAnswers,
  ClarificationQuestion,
  FinalRoadmapResponse,
  PresetScenarioId,
} from "../types/roadmap";
import { getClarificationQuestions, analyzeInnovation } from "../lib/api";
import { CLARIFICATION_QUESTIONS } from "../lib/mockData";
import { Scale } from "lucide-react";

type AppStep = "input" | "clarifying" | "loading" | "dashboard";

export default function Home() {
  const [step, setStep] = useState<AppStep>("input");
  const [selectedPreset, setSelectedPreset] = useState<PresetScenarioId>("ashwagandha");
  const [innovationDescription, setInnovationDescription] = useState<string>(
    "I developed a modified Ashwagandha formulation using a new extraction process for stress relief."
  );
  const [questions, setQuestions] = useState<ClarificationQuestion[]>(CLARIFICATION_QUESTIONS);
  const [clarificationAnswers, setClarificationAnswers] = useState<ClarificationAnswers>({});
  const [roadmap, setRoadmap] = useState<FinalRoadmapResponse | null>(null);
  const [isLiveBackend, setIsLiveBackend] = useState<boolean>(false);
  const [isSampleData, setIsSampleData] = useState<boolean>(true);
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(false);
  const [isDisclaimerOpen, setIsDisclaimerOpen] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Probe backend on mount to check if Member 2 FastAPI backend is running
  useEffect(() => {
    async function checkBackend() {
      const res = await getClarificationQuestions();
      setIsLiveBackend(res.isLiveBackend);
      if (res.questions && res.questions.length > 0) {
        setQuestions(res.questions);
      }
    }
    checkBackend();
  }, []);

  // Handle Initial Innovation submission from InnovationInput
  const handleInnovationSubmit = async (desc: string, presetId: PresetScenarioId) => {
    setInnovationDescription(desc);
    setSelectedPreset(presetId);
    setError(null);

    // Refresh dynamic clarification questions if backend is live
    const res = await getClarificationQuestions(desc);
    if (res.questions && res.questions.length > 0) {
      setQuestions(res.questions);
    }
    setIsLiveBackend(res.isLiveBackend);
    setStep("clarifying");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // Switch scenario directly from Sidebar or Quick Selector
  const handleQuickSelectPreset = async (presetId: PresetScenarioId) => {
    setSelectedPreset(presetId);
    let desc = "";
    if (presetId === "triphala") {
      desc =
        "A classical Triphala Churna prepared strictly according to Sharangadhara Samhita textual references for digestive balance.";
    } else if (presetId === "abstention") {
      desc =
        "A miracle herbal powder 100% guaranteed to cure all stress and chronic ailments in 3 days with fast-track patent grant without clinical trials.";
    } else {
      desc =
        "I developed a modified Ashwagandha formulation using a new extraction process for stress relief.";
    }
    setInnovationDescription(desc);
    setStep("loading");
    window.scrollTo({ top: 0, behavior: "smooth" });

    try {
      const result = await analyzeInnovation({
        preset_id: presetId,
        innovation_description: desc,
        clarifications: {},
        jurisdiction: "india",
      });

      setIsLiveBackend(result.isLiveBackend);
      setIsSampleData(result.isSampleData);
      setRoadmap(result.report);

      setTimeout(() => {
        setStep("dashboard");
        window.scrollTo({ top: 0, behavior: "smooth" });
      }, 3600);
    } catch (err: any) {
      setError(err?.message || "Failed to analyze innovation. Please try again.");
      setStep("input");
    }
  };

  // Handle Clarification submission -> proceed to analysis
  const handleClarificationSubmit = async (answers: ClarificationAnswers) => {
    setClarificationAnswers(answers);
    setStep("loading");
    window.scrollTo({ top: 0, behavior: "smooth" });

    try {
      const result = await analyzeInnovation({
        preset_id: selectedPreset,
        innovation_description: innovationDescription,
        clarifications: answers,
        jurisdiction: "india",
      });

      setIsLiveBackend(result.isLiveBackend);
      setIsSampleData(result.isSampleData);
      setRoadmap(result.report);

      // Allow pipeline loader to complete all 6 stages smoothly
      setTimeout(() => {
        setStep("dashboard");
        window.scrollTo({ top: 0, behavior: "smooth" });
      }, 3600);
    } catch (err: any) {
      setError(err?.message || "Failed to analyze innovation. Please try again.");
      setStep("clarifying");
    }
  };

  // Reset back to innovation input
  const handleReset = () => {
    setStep("input");
    setRoadmap(null);
    setClarificationAnswers({});
    setError(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const getScenarioLabel = () => {
    switch (selectedPreset) {
      case "ashwagandha":
        return "Ashwagandha Extraction";
      case "triphala":
        return "Classical Triphala";
      case "abstention":
        return "Safe Abstention Test";
      default:
        return "Custom Input";
    }
  };

  return (
    <div className="min-h-screen flex bg-stone-50/40 text-stone-900 dark:bg-stone-950 dark:text-stone-100 font-sans">
      {/* Sidebar Navigation */}
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        currentStep={step}
        activePreset={selectedPreset}
        onSelectPreset={handleQuickSelectPreset}
        onNewAnalysis={handleReset}
        onOpenDisclaimer={() => setIsDisclaimerOpen(true)}
        hasActiveRoadmap={step === "dashboard" && !!roadmap}
      />

      {/* Main Content Area (offset by sidebar on desktop) */}
      <div className="flex-1 flex flex-col min-w-0 lg:pl-72 transition-all duration-300">
        {/* Navigation Header */}
        <Navbar
          isLiveBackend={isLiveBackend}
          onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
          onOpenDisclaimer={() => setIsDisclaimerOpen(true)}
          activeScenarioName={step === "dashboard" ? getScenarioLabel() : undefined}
        />

        {/* Main Body */}
        <main className="flex-1 pb-16">
          {step === "input" && (
            <>
              <LandingHero
                onStartAnalysis={() => {
                  const el = document.getElementById("innovation-input-section");
                  el?.scrollIntoView({ behavior: "smooth" });
                }}
              />
              <div id="innovation-input-section">
                <InnovationInput
                  initialValue={innovationDescription}
                  initialPreset={selectedPreset}
                  onSubmit={handleInnovationSubmit}
                />
              </div>
            </>
          )}

          {step === "clarifying" && (
            <ClarificationWizard
              questions={questions}
              initialAnswers={clarificationAnswers}
              innovationDescription={innovationDescription}
              presetId={selectedPreset}
              onBackToInput={() => setStep("input")}
              onSubmitForAnalysis={handleClarificationSubmit}
            />
          )}

          {step === "loading" && (
            <PipelineLoader
              isAbstentionScenario={selectedPreset === "abstention"}
            />
          )}

          {step === "dashboard" && roadmap && (
            <RoadmapDashboard
              roadmap={roadmap}
              innovationDescription={innovationDescription}
              isSampleData={isSampleData}
              onReset={handleReset}
            />
          )}
        </main>

        {/* Footer */}
        <footer className="border-t border-stone-200 bg-white py-6 text-center text-xs text-stone-500 dark:border-stone-800 dark:bg-stone-900 dark:text-stone-400 print:hidden">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-1.5">
            <div className="flex items-center justify-center gap-2">
              <Scale className="h-4 w-4 text-amber-600" />
              <span className="font-bold text-stone-700 dark:text-stone-300">
                IP-SAKTI Navigator
              </span>
              <span>— Smart India Hackathon 2026 (Problem Statement SIH26045)</span>
            </div>
            <p className="text-[11px] text-stone-400 dark:text-stone-500 max-w-2xl mx-auto">
              Evidence-first decision engine for Ayurvedic innovators. Incorporates Hybrid Legal RAG, Intelligent Classification, Decision Routing, Independent Claim Verification, and Safe Abstention.
            </p>
          </div>
        </footer>
      </div>

      {/* 10 Safety Rules Disclaimer Modal */}
      <DisclaimerModal
        isOpen={isDisclaimerOpen}
        onClose={() => setIsDisclaimerOpen(false)}
      />
    </div>
  );
}

"use client";

import React, { useState } from "react";
import {
  ClarificationAnswers,
  ClarificationQuestion,
  PresetScenarioId,
} from "../types/roadmap";
import {
  CheckCircle2,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Info,
  Scale,
} from "lucide-react";

interface ClarificationWizardProps {
  questions: ClarificationQuestion[];
  initialAnswers?: ClarificationAnswers;
  innovationDescription: string;
  presetId?: PresetScenarioId;
  onBackToInput: () => void;
  onSubmitForAnalysis: (answers: ClarificationAnswers) => void;
}

export default function ClarificationWizard({
  questions,
  initialAnswers = {},
  innovationDescription,
  presetId = "ashwagandha",
  onBackToInput,
  onSubmitForAnalysis,
}: ClarificationWizardProps) {
  const descLower = innovationDescription.toLowerCase();

  const [answers, setAnswers] = useState<ClarificationAnswers>(() => {
    if (Object.keys(initialAnswers).length > 0) return initialAnswers;

    if (presetId === "triphala" || descLower.includes("triphala")) {
      return {
        intended_use: "therapeutic_internal",
        classical_heritage: "classical_exact",
        novel_extraction: "standard_ayurvedic_extraction",
        biological_resources: "indian_wild_cultivated",
        jurisdiction: "india_primary",
      };
    }

    if (presetId === "abstention" || descLower.includes("guaranteed") || descLower.includes("miracle")) {
      return {
        intended_use: "therapeutic_internal",
        classical_heritage: "completely_new",
        novel_extraction: "unsure_process",
        biological_resources: "indian_wild_cultivated",
        jurisdiction: "india_primary",
      };
    }

    // Default: Ashwagandha
    return {
      intended_use: "therapeutic_internal",
      classical_heritage: "classical_modified",
      novel_extraction: "novel_process_claimed",
      biological_resources: "indian_wild_cultivated",
      jurisdiction: "india_primary",
    };
  });

  const [currentStep, setCurrentStep] = useState(0);

  const currentQ = questions[currentStep];
  const isLastStep = currentStep === questions.length - 1;
  const progressPercent = Math.round(((currentStep + 1) / questions.length) * 100);

  const handleSelectOption = (fieldKey: string, value: string) => {
    setAnswers((prev) => ({ ...prev, [fieldKey]: value }));
  };

  const handleNext = () => {
    if (isLastStep) {
      onSubmitForAnalysis(answers);
    } else {
      setCurrentStep((prev) => Math.min(prev + 1, questions.length - 1));
    }
  };

  const handlePrev = () => {
    if (currentStep === 0) {
      onBackToInput();
    } else {
      setCurrentStep((prev) => Math.max(prev - 1, 0));
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-4 sm:px-6 py-8">
      <div className="rounded-3xl border border-stone-200 bg-white p-6 sm:p-8 shadow-sm dark:border-stone-800 dark:bg-stone-900">
        {/* Header & Step Counter */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-stone-100 pb-5 dark:border-stone-800">
          <div>
            <div className="flex items-center gap-2">
              <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-semibold text-amber-800 dark:bg-amber-950 dark:text-amber-300">
                Step 2: Clarification Wizard ({currentStep + 1} of {questions.length})
              </span>
              <span className="text-xs text-stone-500 dark:text-stone-400">
                Legal Decision Routing
              </span>
            </div>
            <h2 className="text-lg font-bold text-stone-900 dark:text-stone-100 mt-1">
              Targeted Statutory Clarification
            </h2>
          </div>

          <div className="text-xs font-medium text-stone-500 dark:text-stone-400">
            Progress: <strong className="text-amber-600 dark:text-amber-400">{progressPercent}%</strong>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-stone-100 h-1.5 rounded-full overflow-hidden mt-4 dark:bg-stone-800">
          <div
            className="bg-gradient-to-r from-amber-600 to-emerald-600 h-full transition-all duration-300 rounded-full"
            style={{ width: `${progressPercent}%` }}
          />
        </div>

        {/* Short Innovation Context Reminder */}
        <div className="mt-4 rounded-xl bg-stone-50 p-3 text-xs text-stone-600 dark:bg-stone-800/60 dark:text-stone-300 border border-stone-200/60 dark:border-stone-700/60 flex items-start gap-2">
          <Sparkles className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
          <div className="line-clamp-2">
            <strong className="text-stone-800 dark:text-stone-100">Evaluating: </strong>
            &quot;{innovationDescription}&quot;
          </div>
        </div>

        {/* Current Question Section */}
        {currentQ && (
          <div className="mt-6">
            <h3 className="text-base sm:text-lg font-semibold text-stone-900 dark:text-stone-100">
              {currentQ.question}
            </h3>
            <p className="mt-1 text-xs text-stone-500 dark:text-stone-400 leading-relaxed">
              {currentQ.description}
            </p>

            {/* Options List */}
            <div className="mt-5 space-y-3">
              {currentQ.options.map((opt) => {
                const isSelected = answers[currentQ.field_key] === opt.value;
                return (
                  <label
                    key={opt.value}
                    onClick={() => handleSelectOption(currentQ.field_key, opt.value)}
                    className={`block cursor-pointer rounded-2xl border p-4 transition ${
                      isSelected
                        ? "border-amber-500 bg-amber-50/60 text-stone-900 shadow-xs dark:bg-amber-950/40 dark:border-amber-600 dark:text-white ring-1 ring-amber-500/20"
                        : "border-stone-200 bg-white hover:border-stone-300 hover:bg-stone-50/70 text-stone-700 dark:border-stone-800 dark:bg-stone-800/40 dark:text-stone-200 dark:hover:bg-stone-800"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="space-y-1">
                        <div className="text-sm font-semibold flex items-center gap-2">
                          <span>{opt.label}</span>
                        </div>
                        {opt.hint && (
                          <div className="text-xs text-stone-500 dark:text-stone-400 flex items-start gap-1.5">
                            <Info className="h-3.5 w-3.5 shrink-0 text-amber-600 mt-0.5" />
                            <span>{opt.hint}</span>
                          </div>
                        )}
                      </div>

                      <div
                        className={`h-5 w-5 rounded-full border flex items-center justify-center shrink-0 mt-0.5 transition ${
                          isSelected
                            ? "border-amber-600 bg-amber-600 text-white"
                            : "border-stone-300 dark:border-stone-600"
                        }`}
                      >
                        {isSelected && <CheckCircle2 className="h-4 w-4" />}
                      </div>
                    </div>
                  </label>
                );
              })}
            </div>
          </div>
        )}

        {/* Step Navigation Bar */}
        <div className="mt-8 flex items-center justify-between border-t border-stone-100 pt-5 dark:border-stone-800">
          <button
            type="button"
            onClick={handlePrev}
            className="inline-flex items-center gap-1.5 rounded-xl border border-stone-200 px-4 py-2 text-xs font-semibold text-stone-700 hover:bg-stone-50 dark:border-stone-700 dark:text-stone-300 dark:hover:bg-stone-800 transition"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            <span>{currentStep === 0 ? "Edit Innovation" : "Previous"}</span>
          </button>

          <div className="flex items-center gap-2">
            {/* Quick Answer indicator dots */}
            <div className="hidden sm:flex items-center gap-1.5 mr-2">
              {questions.map((q, idx) => {
                const isDone = !!answers[q.field_key];
                return (
                  <button
                    key={q.id}
                    onClick={() => setCurrentStep(idx)}
                    className={`h-2.5 w-2.5 rounded-full transition-all ${
                      idx === currentStep
                        ? "w-6 bg-amber-600"
                        : isDone
                        ? "bg-emerald-500"
                        : "bg-stone-200 dark:bg-stone-700"
                    }`}
                    title={q.question}
                  />
                );
              })}
            </div>

            <button
              type="button"
              onClick={handleNext}
              disabled={!answers[currentQ?.field_key]}
              className={`inline-flex items-center gap-2 rounded-xl px-5 py-2.5 text-xs font-semibold text-white shadow-sm transition ${
                !answers[currentQ?.field_key]
                  ? "bg-stone-300 cursor-not-allowed dark:bg-stone-700"
                  : isLastStep
                  ? "bg-gradient-to-r from-emerald-600 to-amber-600 hover:from-emerald-700 hover:to-amber-700"
                  : "bg-stone-900 hover:bg-stone-800 dark:bg-stone-100 dark:text-stone-900 dark:hover:bg-stone-200"
              }`}
            >
              <span>{isLastStep ? "Analyze & Generate Roadmap" : "Next Question"}</span>
              {isLastStep ? <Scale className="h-3.5 w-3.5" /> : <ArrowRight className="h-3.5 w-3.5" />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

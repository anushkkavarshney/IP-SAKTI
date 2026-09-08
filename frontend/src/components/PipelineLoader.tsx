"use client";

import React, { useEffect, useState } from "react";
import {
  CheckCircle2,
  Loader2,
  Scale,
  Search,
  Cpu,
  ShieldCheck,
  FileText,
  Sparkles,
} from "lucide-react";

interface PipelineLoaderProps {
  onComplete?: () => void;
  isAbstentionScenario?: boolean;
}

const PIPELINE_STAGES = [
  {
    id: 1,
    title: "1. Formulation Classification",
    desc: "Classifying innovation into Classical vs Proprietary ASU Drug, Phytopharmaceutical, Nutraceutical, or Cosmetic.",
    icon: Sparkles,
  },
  {
    id: 2,
    title: "2. Decision Routing & Jurisdiction Filter",
    desc: "Activating statutory IP, ABS (Biodiversity), and Regulatory paths under sovereign Indian jurisdiction.",
    icon: Scale,
  },
  {
    id: 3,
    title: "3. Hybrid Legal Retrieval (Vector + BM25)",
    desc: "Searching curated Indian legal corpus: Patents Act 1970, Biological Diversity Act 2002, D&C Act 1940, FSSAI.",
    icon: Search,
  },
  {
    id: 4,
    title: "4. Statutory Evidence Assembly & Grounding",
    desc: "Restricting legal assertions strictly to retrieved statutes; prohibiting pre-trained memory hallucinations.",
    icon: FileText,
  },
  {
    id: 5,
    title: "5. Independent Claim Verification Engine",
    desc: "Evaluating individual claims against legal citations into Supported, Partially Supported, or Unsupported.",
    icon: ShieldCheck,
  },
  {
    id: 6,
    title: "6. Confidence Engine & Safe Abstention Check",
    desc: "Computing formulaic confidence score (30% Retrieval, 25% Authority, 25% Claim Support, 20% Jurisdiction).",
    icon: Cpu,
  },
];

export default function PipelineLoader({
  onComplete,
  isAbstentionScenario = false,
}: PipelineLoaderProps) {
  const [activeStage, setActiveStage] = useState(1);

  useEffect(() => {
    // Realistic progression simulation (approx 3.6s total, or pluggable with backend SSE)
    const interval = setInterval(() => {
      setActiveStage((prev) => {
        if (prev < PIPELINE_STAGES.length) {
          return prev + 1;
        } else {
          clearInterval(interval);
          if (onComplete) onComplete();
          return prev;
        }
      });
    }, 600);

    return () => clearInterval(interval);
  }, [onComplete]);

  const progressPercent = Math.min(
    100,
    Math.round((activeStage / PIPELINE_STAGES.length) * 100)
  );

  return (
    <div className="relative mx-auto max-w-2xl px-4 sm:px-6 py-8">
      {/* Sticky Progress Tracker Bar at top */}
      <div className="sticky top-18 z-30 mb-6 rounded-2xl border border-blue-200 bg-white/95 p-4 shadow-md backdrop-blur-md dark:border-blue-900/60 dark:bg-stone-900/95 transition">
        <div className="flex items-center justify-between text-xs font-bold text-stone-800 dark:text-stone-200">
          <div className="flex items-center gap-2">
            <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
            <span>Executing Legal AI Pipeline</span>
            <span className="text-[11px] text-stone-400 font-normal">
              (Stage {activeStage} of {PIPELINE_STAGES.length})
            </span>
          </div>
          <span className="text-blue-600 dark:text-blue-400 font-extrabold text-sm">
            {progressPercent}%
          </span>
        </div>
        <div className="mt-2.5 h-2 w-full rounded-full bg-stone-100 overflow-hidden dark:bg-stone-800">
          <div
            className="h-full bg-gradient-to-r from-blue-600 via-indigo-600 to-emerald-600 transition-all duration-300 rounded-full"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      <div className="rounded-3xl border border-stone-200 bg-white p-6 sm:p-8 shadow-sm dark:border-stone-800 dark:bg-stone-900">
        {/* Header Info */}
        <div className="text-center pb-2">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300 ring-4 ring-blue-50 dark:ring-blue-900/30">
            <Loader2 className="h-6 w-6 animate-spin text-blue-600 dark:text-blue-400" />
          </div>
          <h2 className="mt-4 text-xl font-bold text-stone-900 dark:text-stone-100">
            Running Evidence-Backed Legal Pipeline
          </h2>
          <p className="mt-1 text-xs text-stone-500 dark:text-stone-400">
            Evaluating statutory compliance under Indian Patent Office, NBA, AYUSH, and CDSCO gazettes.
          </p>
        </div>

        {/* Pipeline Stages Vertical List */}
        <div className="mt-6 space-y-3">
          {PIPELINE_STAGES.map((stage) => {
            const isCompleted = activeStage > stage.id;
            const isCurrent = activeStage === stage.id;
            const isPending = activeStage < stage.id;
            const Icon = stage.icon;

            return (
              <div
                key={stage.id}
                className={`flex items-start gap-3.5 rounded-2xl border p-3.5 transition-all ${
                  isCurrent
                    ? "border-blue-400 bg-blue-50/70 dark:border-blue-700 dark:bg-blue-950/40 shadow-xs scale-[1.01]"
                    : isCompleted
                    ? "border-emerald-200/80 bg-emerald-50/20 dark:border-emerald-900/40 dark:bg-emerald-950/10 text-stone-700 dark:text-stone-300"
                    : "border-stone-100 bg-stone-50/40 dark:border-stone-800 dark:bg-stone-800/20 text-stone-400 dark:text-stone-500 opacity-50"
                }`}
              >
                <div className="shrink-0 mt-0.5">
                  {isCompleted ? (
                    <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                  ) : isCurrent ? (
                    <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
                  ) : (
                    <div className="h-5 w-5 rounded-full border border-stone-300 dark:border-stone-600 flex items-center justify-center text-[10px] font-bold">
                      {stage.id}
                    </div>
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-xs font-bold ${
                        isCurrent
                          ? "text-blue-900 dark:text-blue-200"
                          : isCompleted
                          ? "text-stone-900 dark:text-stone-100"
                          : "text-stone-500"
                      }`}
                    >
                      {stage.title}
                    </span>
                    {isCurrent && (
                      <span className="rounded-full bg-blue-200/80 px-2 py-0.2 text-[9px] font-bold text-blue-900 dark:bg-blue-900 dark:text-blue-200 animate-pulse">
                        In Progress
                      </span>
                    )}
                    {isCompleted && (
                      <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold">
                        ✓ Verified
                      </span>
                    )}
                  </div>
                  <p className="mt-0.5 text-[11px] text-stone-500 dark:text-stone-400 leading-snug">
                    {stage.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

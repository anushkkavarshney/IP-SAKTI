"use client";

import { Loader2, Search, ShieldCheck, Sparkles } from "lucide-react";

interface PipelineLoaderProps {
  detail?: string;
}

const STAGES = [
  {
    icon: Sparkles,
    title: "Analyzing your innovation...",
    desc: "Classifying the formulation and routing it to the relevant legal domains.",
  },
  {
    icon: Search,
    title: "Retrieving relevant Indian legal evidence...",
    desc: "Searching the statutory corpus (IP, ABS, regulatory) for your innovation profile.",
  },
  {
    icon: ShieldCheck,
    title: "Verifying claims and preparing your roadmap...",
    desc: "Cross-checking each generated claim against retrieved evidence and computing confidence.",
  },
];

export default function PipelineLoader({ detail }: PipelineLoaderProps) {
  return (
    <div className="mx-auto max-w-xl px-4 py-10 sm:px-6">
      <div className="rounded-3xl border border-stone-200 bg-white p-8 text-center shadow-sm dark:border-stone-800 dark:bg-stone-900">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
          <Loader2 className="h-7 w-7 animate-spin" />
        </div>
        <h2 className="mt-5 text-lg font-bold text-stone-900 dark:text-stone-100">
          Running the evidence pipeline
        </h2>
        <p className="mx-auto mt-2 max-w-sm text-xs leading-relaxed text-stone-500 dark:text-stone-400">
          Your request is with the analysis service now. This can take a
          minute — the status below reflects the real request, not a scripted
          animation.
        </p>
        {detail && (
          <p className="mx-auto mt-3 inline-block rounded-full border border-stone-200 bg-stone-50 px-3 py-1 text-[11px] text-stone-500 dark:border-stone-700 dark:bg-stone-800 dark:text-stone-400">
            {detail}
          </p>
        )}
      </div>

      <ol className="mt-6 space-y-2.5">
        {STAGES.map((stage) => {
          const Icon = stage.icon;
          return (
            <li
              key={stage.title}
              className="flex items-start gap-3 rounded-2xl border border-stone-200 bg-white p-4 dark:border-stone-800 dark:bg-stone-900"
            >
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-stone-100 text-stone-500 dark:bg-stone-800 dark:text-stone-400">
                <Icon className="h-4 w-4" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-bold text-stone-800 dark:text-stone-200">
                  {stage.title}
                </p>
                <p className="mt-0.5 text-[11px] leading-relaxed text-stone-500 dark:text-stone-400">
                  {stage.desc}
                </p>
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
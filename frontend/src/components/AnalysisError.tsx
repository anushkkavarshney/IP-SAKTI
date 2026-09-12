"use client";

import { useState } from "react";
import {
  WifiOff,
  RefreshCw,
  FlaskConical,
  AlertTriangle,
} from "lucide-react";
import { apiErrorMessage, apiErrorTitle } from "../lib/api";

export type AnalysisErrorInfo = {
  title: string;
  message: string;
};

export function toAnalysisError(err: unknown): AnalysisErrorInfo {
  const title = apiErrorTitle(err);
  const message = apiErrorMessage(err);
  return { title, message };
}

interface AnalysisErrorProps {
  error: AnalysisErrorInfo;
  onRetry: () => void;
  onUseSample: () => void;
  onBack: () => void;
}

export default function AnalysisError({
  error,
  onRetry,
  onUseSample,
  onBack,
}: AnalysisErrorProps) {
  const [retrying, setRetrying] = useState(false);

  const handleRetry = async () => {
    setRetrying(true);
    try {
      await onRetry();
    } finally {
      setRetrying(false);
    }
  };

  return (
    <div
      role="alert"
      className="mx-auto max-w-2xl px-4 py-16 sm:px-6"
    >
      <div className="rounded-3xl border border-stone-200 bg-white p-8 text-center shadow-sm dark:border-stone-800 dark:bg-stone-900">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300">
          <AlertTriangle className="h-6 w-6" />
        </div>
        <h2 className="mt-5 text-xl font-bold text-stone-900 dark:text-stone-100">
          {error.title}
        </h2>
        <p className="mx-auto mt-2 max-w-md text-sm leading-relaxed text-stone-600 dark:text-stone-400">
          {error.message}
        </p>

        <div className="mt-7 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <button
            type="button"
            onClick={handleRetry}
            disabled={retrying}
            className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-stone-900 px-5 py-2.5 text-xs font-semibold text-white transition hover:bg-stone-800 disabled:opacity-60 dark:bg-stone-100 dark:text-stone-900 dark:hover:bg-stone-200 sm:w-auto"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${retrying ? "animate-spin" : ""}`} />
            <span>Retry</span>
          </button>

          <button
            type="button"
            onClick={onUseSample}
            className="inline-flex w-full items-center justify-center gap-2 rounded-xl border border-amber-300 bg-amber-50 px-5 py-2.5 text-xs font-semibold text-amber-900 transition hover:bg-amber-100 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-200 dark:hover:bg-amber-950 sm:w-auto"
          >
            <FlaskConical className="h-3.5 w-3.5" />
            <span>Use Sample Data</span>
          </button>

          <button
            type="button"
            onClick={onBack}
            className="inline-flex w-full items-center justify-center gap-2 rounded-xl border border-stone-200 px-5 py-2.5 text-xs font-semibold text-stone-700 transition hover:bg-stone-50 dark:border-stone-700 dark:text-stone-300 dark:hover:bg-stone-800 sm:w-auto"
          >
            <WifiOff className="h-3.5 w-3.5" />
            <span>Start Again</span>
          </button>
        </div>

        <p className="mt-6 text-[11px] leading-relaxed text-stone-400 dark:text-stone-500">
          Sample data is a fixed demo scenario. It shows the output format only
          and is clearly marked as illustrative — it is never presented as a
          live analysis.
        </p>
      </div>
    </div>
  );
}
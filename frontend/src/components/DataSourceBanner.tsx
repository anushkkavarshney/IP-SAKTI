"use client";

import { Info, Database } from "lucide-react";

export function SampleDataBanner({ className }: { className?: string }) {
  return (
    <div
      role="status"
      className={`flex flex-col gap-2 rounded-2xl border border-amber-300 bg-amber-50/90 px-4 py-3 text-xs text-amber-950 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-100 sm:flex-row sm:items-center sm:justify-between ${className ?? ""}`}
    >
      <div className="flex items-start gap-2.5">
        <Info className="h-4 w-4 shrink-0 text-amber-600 dark:text-amber-400 mt-0.5" />
        <div>
          <strong className="block font-bold">
            You&apos;re viewing illustrative sample data.
          </strong>
          <p className="mt-0.5 leading-relaxed text-amber-900 dark:text-amber-200">
            The analysis service isn&apos;t available right now, so this result is
            a pre-built demo scenario — not a live analysis of your input.
          </p>
        </div>
      </div>
      <span className="shrink-0 self-start rounded-md border border-amber-300 bg-amber-100 px-2 py-0.5 text-[10px] font-bold text-amber-900 dark:border-amber-700 dark:bg-amber-900 dark:text-amber-100 sm:self-auto">
        Illustrative / Sample Data
      </span>
    </div>
  );
}

export function LiveResultChip({ className }: { className?: string }) {
  return (
    <div
      role="status"
      className={`inline-flex items-center gap-1.5 rounded-full border border-emerald-300 bg-emerald-50 px-2.5 py-1 text-[11px] font-semibold text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-300 ${className ?? ""}`}
    >
      <Database className="h-3 w-3" />
      <span>Live result from the analysis service</span>
    </div>
  );
}
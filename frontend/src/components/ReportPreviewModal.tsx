"use client";

import { useEffect, useRef } from "react";
import {
  X,
  CalendarDays,
  ShieldAlert,
  FileCheck2,
  Layers,
  ArrowRight,
} from "lucide-react";
import { AssessmentRecord } from "../types/assessment";
import { formatConfidenceLevel, formatDate, truncate } from "../lib/utils";

interface ReportPreviewModalProps {
  record: AssessmentRecord;
  onClose: () => void;
}

export default function ReportPreviewModal({
  record,
  onClose,
}: ReportPreviewModalProps) {
  const closeRef = useRef<HTMLButtonElement>(null);
  const config = formatConfidenceLevel(record.confidenceLevel);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    closeRef.current?.focus();
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="report-preview-title"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="relative w-full max-w-lg overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-2xl dark:border-stone-800 dark:bg-stone-900">
        <div className="flex items-start justify-between gap-4 border-b border-stone-100 p-5 dark:border-stone-800">
          <div>
            <h3
              id="report-preview-title"
              className="text-base font-bold text-stone-900 dark:text-stone-100"
            >
              Assessment preview
            </h3>
            <p className="mt-0.5 text-xs text-stone-500 dark:text-stone-400">
              {record.classification}
            </p>
          </div>
          <button
            ref={closeRef}
            onClick={onClose}
            aria-label="Close assessment preview"
            className="rounded-full p-1.5 text-stone-400 transition hover:bg-stone-100 hover:text-stone-700 dark:hover:bg-stone-800 dark:hover:text-stone-200"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="max-h-[70vh] space-y-4 overflow-y-auto p-5">
          <p className="text-sm leading-relaxed text-stone-700 dark:text-stone-300">
            {record.title}
          </p>

          <dl className="grid grid-cols-2 gap-3 text-xs">
            <div className="rounded-xl border border-stone-200 bg-stone-50 p-3 dark:border-stone-800 dark:bg-stone-800/40">
              <dt className="flex items-center gap-1.5 font-semibold text-stone-500 dark:text-stone-400">
                <CalendarDays className="h-3.5 w-3.5" />
                Date
              </dt>
              <dd className="mt-1 font-bold text-stone-800 dark:text-stone-200">
                {formatDate(record.createdAt)}
              </dd>
            </div>
            <div className="rounded-xl border border-stone-200 bg-stone-50 p-3 dark:border-stone-800 dark:bg-stone-800/40">
              <dt className="flex items-center gap-1.5 font-semibold text-stone-500 dark:text-stone-400">
                <Layers className="h-3.5 w-3.5" />
                Classification
              </dt>
              <dd className="mt-1 font-bold text-stone-800 dark:text-stone-200">
                {truncate(record.classification, 34)}
              </dd>
            </div>
            <div className="rounded-xl border border-stone-200 bg-stone-50 p-3 dark:border-stone-800 dark:bg-stone-800/40">
              <dt className="font-semibold text-stone-500 dark:text-stone-400">
                Confidence
              </dt>
              <dd className="mt-1 flex items-center gap-2">
                <span className="text-lg font-black text-stone-800 dark:text-stone-200">
                  {record.confidence}
                </span>
                <span
                  className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold ${config.bg}`}
                >
                  <span className={`h-1.5 w-1.5 rounded-full ${config.dot}`} />
                  {config.label}
                </span>
              </dd>
            </div>
            <div className="rounded-xl border border-stone-200 bg-stone-50 p-3 dark:border-stone-800 dark:bg-stone-800/40">
              <dt className="flex items-center gap-1.5 font-semibold text-stone-500 dark:text-stone-400">
                <ShieldAlert className="h-3.5 w-3.5" />
                Status
              </dt>
              <dd className="mt-1 font-bold text-stone-800 dark:text-stone-200">
                {record.abstained
                  ? "Abstained"
                  : record.confidenceLevel === "LOW"
                  ? "Low confidence"
                  : "Completed"}
              </dd>
            </div>
          </dl>

          {record.abstained && (
            <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs leading-relaxed text-rose-900 dark:border-rose-900 dark:bg-rose-950/40 dark:text-rose-200">
              <strong className="block font-bold">
                Safe abstention was triggered.
              </strong>
              <p className="mt-1">
                {record.abstainReason ||
                  "The available sources did not provide enough evidence to confidently determine a pathway. Expert review is recommended."}
              </p>
            </div>
          )}

          {record.verification.total > 0 && (
            <div className="flex flex-wrap items-center gap-2 text-[11px] font-semibold">
              <span className="flex items-center gap-1.5 rounded-lg border border-emerald-300 bg-emerald-50 px-2.5 py-1 text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300">
                <FileCheck2 className="h-3 w-3" />
                {record.verification.supported} supported
              </span>
              <span className="rounded-lg border border-amber-300 bg-amber-50 px-2.5 py-1 text-amber-800 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-300">
                {record.verification.partial} partial
              </span>
              <span className="rounded-lg border border-rose-300 bg-rose-50 px-2.5 py-1 text-rose-800 dark:border-rose-800 dark:bg-rose-950/40 dark:text-rose-300">
                {record.verification.unsupported} unsupported
              </span>
            </div>
          )}

          {record.isSampleData && (
            <div className="rounded-xl border border-amber-300 bg-amber-50 p-3 text-xs text-amber-900 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-200">
              This entry is an <strong>illustrative sample</strong> — it was
              generated from demo data, not a live analysis of your innovation.
            </div>
          )}
        </div>

        <div className="flex justify-end border-t border-stone-100 p-4 dark:border-stone-800">
          <a
            href="/assessment"
            className="inline-flex items-center gap-2 rounded-xl bg-stone-900 px-5 py-2 text-xs font-semibold text-white transition hover:bg-stone-800 dark:bg-stone-100 dark:text-stone-900 dark:hover:bg-stone-200"
          >
            <span>Start a new assessment</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </a>
        </div>
      </div>
    </div>
  );
}
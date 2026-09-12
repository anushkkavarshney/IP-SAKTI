"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import {
  Sparkles,
  FileText,
  CalendarDays,
  Layers,
  ShieldAlert,
  ArrowRight,
  Info,
} from "lucide-react";
import { AssessmentRecord } from "../../../types/assessment";
import { readReports } from "../../../lib/storage";
import {
  formatConfidenceLevel,
  formatDate,
  truncate,
} from "../../../lib/utils";
import ReportPreviewModal from "../../../components/ReportPreviewModal";

export default function ReportsPage() {
  const reports = useMemo(() => readReports(), []);
  const [previewRecord, setPreviewRecord] = useState<AssessmentRecord | null>(
    null
  );

  return (
    <div className="space-y-6">
      <section>
        <h1 className="text-2xl font-extrabold tracking-tight text-stone-900 dark:text-white">
          My assessments
        </h1>
        <p className="mt-1 text-sm text-stone-500 dark:text-stone-400">
          Saved roadmap summaries stored in this browser. Select an entry to
          preview.
        </p>
      </section>

      {reports.length === 0 ? (
        <section className="rounded-3xl border border-dashed border-stone-300 bg-white p-10 text-center dark:border-stone-700 dark:bg-stone-900">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">
            <FileText className="h-7 w-7" />
          </div>
          <h2 className="mt-4 text-lg font-bold text-stone-900 dark:text-stone-100">
            No saved assessments
          </h2>
          <p className="mx-auto mt-2 max-w-sm text-sm leading-relaxed text-stone-500 dark:text-stone-400">
            Complete an assessment and it will appear here for future review.
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/assessment"
              className="inline-flex items-center gap-2 rounded-xl bg-stone-900 px-5 py-2.5 text-xs font-semibold text-white transition hover:bg-stone-800 dark:bg-stone-100 dark:text-stone-900 dark:hover:bg-stone-200"
            >
              <Sparkles className="h-3.5 w-3.5" />
              <span>Start your first assessment</span>
            </Link>
          </div>
          <div className="mt-4 inline-flex items-center gap-1.5 rounded-full border border-stone-200 bg-stone-50 px-3 py-1 text-[11px] text-stone-500 dark:border-stone-700 dark:bg-stone-800 dark:text-stone-400">
            <Info className="h-3 w-3 text-amber-600" />
            Data stays in your browser — nothing is uploaded.
          </div>
        </section>
      ) : (
        <section className="space-y-3">
          {reports.map((report) => {
            const level = formatConfidenceLevel(report.confidenceLevel);
            return (
              <button
                key={report.id}
                type="button"
                onClick={() => setPreviewRecord(report)}
                className="group flex w-full items-center gap-4 rounded-2xl border border-stone-200 bg-white p-4 text-left transition hover:border-amber-300 hover:shadow-sm dark:border-stone-800 dark:bg-stone-900 dark:hover:border-amber-700"
              >
                {report.abstained ? (
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300">
                    <ShieldAlert className="h-5 w-5" />
                  </div>
                ) : (
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                    <FileText className="h-5 w-5" />
                  </div>
                )}

                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-bold text-stone-800 dark:text-stone-200">
                    {report.title}
                  </p>
                  <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-stone-500 dark:text-stone-400">
                    <span className="inline-flex items-center gap-1">
                      <CalendarDays className="h-3 w-3" />
                      {formatDate(report.createdAt)}
                    </span>
                    <span className="inline-flex items-center gap-1">
                      <Layers className="h-3 w-3" />
                      {truncate(report.classification, 36)}
                    </span>
                    {report.isSampleData && (
                      <span className="rounded-full border border-amber-300 bg-amber-50 px-2 py-0.5 text-[10px] font-bold text-amber-800 dark:border-amber-700 dark:bg-amber-950/50 dark:text-amber-200">
                        Sample
                      </span>
                    )}
                  </div>
                </div>

                <span
                  className={`hidden shrink-0 rounded-full border px-2.5 py-1 text-[10px] font-bold sm:inline ${level.bg}`}
                >
                  {report.confidence}%
                </span>

                <ArrowRight className="h-4 w-4 shrink-0 text-stone-300 transition group-hover:text-amber-500 dark:text-stone-600" />
              </button>
            );
          })}
        </section>
      )}

      {previewRecord && (
        <ReportPreviewModal
          record={previewRecord}
          onClose={() => setPreviewRecord(null)}
        />
      )}
    </div>
  );
}
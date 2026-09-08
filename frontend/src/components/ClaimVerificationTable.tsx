"use client";

import React, { useState } from "react";
import { VerificationSummary, ClaimVerificationItem } from "../types/roadmap";
import { formatVerificationStatus } from "../lib/utils";
import {
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  FileSearch,
  ChevronDown,
  ChevronUp,
  Info,
} from "lucide-react";

interface ClaimVerificationTableProps {
  verification: VerificationSummary;
}

export default function ClaimVerificationTable({
  verification,
}: ClaimVerificationTableProps) {
  const {
    total_claims,
    supported_claims,
    partially_supported_claims,
    unsupported_claims,
    items = [],
  } = verification;

  const [expandedId, setExpandedId] = useState<string | null>(null);

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="rounded-3xl border border-stone-200 bg-white p-6 shadow-sm dark:border-stone-800 dark:bg-stone-900">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-stone-100 pb-4 dark:border-stone-800">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-stone-900 dark:text-stone-100">
                Independent Claim ↔ Evidence Verification
              </h3>
              <span className="rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-semibold text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300/60">
                Core USP
              </span>
            </div>
            <p className="text-xs text-stone-500 dark:text-stone-400">
              Each AI assertion is extracted and cross-checked against retrieved statutory evidence
            </p>
          </div>
        </div>

        {/* Claim Summary Counts */}
        <div className="flex items-center gap-2 text-xs font-semibold">
          <span className="rounded-lg bg-emerald-50 px-2.5 py-1 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800">
            {supported_claims} Supported
          </span>
          <span className="rounded-lg bg-amber-50 px-2.5 py-1 text-amber-700 border border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800">
            {partially_supported_claims} Partial
          </span>
          {unsupported_claims.length > 0 && (
            <span className="rounded-lg bg-rose-50 px-2.5 py-1 text-rose-700 border border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800">
              {unsupported_claims.length} Unsupported
            </span>
          )}
        </div>
      </div>

      {/* Unsupported Claims Alert Callout if present */}
      {unsupported_claims.length > 0 && (
        <div className="mt-4 rounded-2xl border border-rose-200 bg-rose-50/70 p-4 text-xs text-rose-900 dark:border-rose-900 dark:bg-rose-950/40 dark:text-rose-200">
          <div className="flex items-start gap-2.5">
            <XCircle className="h-4 w-4 text-rose-600 shrink-0 mt-0.5" />
            <div>
              <strong className="font-semibold block mb-1">
                Caution: {unsupported_claims.length} Claim(s) Lack Legal Grounding
              </strong>
              <p className="mb-2 text-[11px] text-rose-800 dark:text-rose-300">
                In adherence with Rule 3 and Rule 4, unsupported statements are quarantined and flagged:
              </p>
              <ul className="list-disc pl-4 space-y-1 text-[11px]">
                {unsupported_claims.map((claim, idx) => (
                  <li key={idx} className="italic">&quot;{claim}&quot;</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Detailed Claims List */}
      <div className="mt-5 space-y-3">
        {items.map((item) => {
          const statusStyle = formatVerificationStatus(item.status);
          const isExpanded = expandedId === item.claim_id;

          return (
            <div
              key={item.claim_id}
              className="rounded-2xl border border-stone-200/90 bg-stone-50/40 dark:border-stone-800 dark:bg-stone-800/30 overflow-hidden transition hover:border-stone-300"
            >
              <button
                type="button"
                onClick={() => toggleExpand(item.claim_id)}
                className="w-full flex items-start justify-between gap-3 p-4 text-left"
              >
                <div className="space-y-1.5 flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <span
                      className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[10px] font-bold ${statusStyle.badge}`}
                    >
                      {item.status === "supported" && <CheckCircle2 className="h-3 w-3" />}
                      {item.status === "partially_supported" && <AlertTriangle className="h-3 w-3" />}
                      {item.status === "unsupported" && <XCircle className="h-3 w-3" />}
                      <span>{statusStyle.label}</span>
                    </span>

                    <span className="text-[10px] font-medium text-stone-500 dark:text-stone-400">
                      Score: <strong className="text-stone-800 dark:text-stone-200">{(item.score * 100).toFixed(0)}%</strong>
                    </span>

                    {item.source_section && (
                      <span className="rounded-md bg-stone-200/70 px-2 py-0.2 text-[10px] font-medium text-stone-700 dark:bg-stone-700 dark:text-stone-300">
                        {item.source_document} · {item.source_section}
                      </span>
                    )}
                  </div>

                  <p className="text-xs sm:text-sm font-semibold text-stone-900 dark:text-stone-100">
                    &quot;{item.claim}&quot;
                  </p>
                </div>

                <div className="shrink-0 text-stone-400 mt-1">
                  {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                </div>
              </button>

              {/* Expanded Verification Evidence Details */}
              {isExpanded && (
                <div className="border-t border-stone-200/70 p-4 bg-white dark:border-stone-700 dark:bg-stone-900/60 space-y-2.5 text-xs">
                  {item.explanation && (
                    <div>
                      <strong className="text-stone-700 dark:text-stone-300 block mb-1">
                        Verification Rationale:
                      </strong>
                      <p className="text-stone-600 dark:text-stone-400 text-[11px] leading-relaxed">
                        {item.explanation}
                      </p>
                    </div>
                  )}

                  {item.evidence_snippet && (
                    <div className="rounded-xl bg-stone-50 p-2.5 border border-stone-200/80 dark:bg-stone-800/50 dark:border-stone-700">
                      <div className="flex items-center gap-1.5 text-[10px] font-semibold text-amber-800 dark:text-amber-300 mb-1">
                        <FileSearch className="h-3 w-3" />
                        <span>Matched Legal Evidence Extract:</span>
                      </div>
                      <blockquote className="italic text-stone-700 dark:text-stone-300 text-[11px]">
                        &quot;{item.evidence_snippet}&quot;
                      </blockquote>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}


"use client";

import React, { useState } from "react";
import { LegalEvidenceChunk } from "../types/roadmap";
import {
  FileText,
  ExternalLink,
  BookOpen,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  Bookmark,
} from "lucide-react";

interface EvidenceDrawerProps {
  evidenceList: LegalEvidenceChunk[];
  title?: string;
  defaultExpanded?: boolean;
}

export default function EvidenceDrawer({
  evidenceList,
  title = "Authoritative Statutory Evidence Chunks",
  defaultExpanded = false,
}: EvidenceDrawerProps) {
  const [isOpen, setIsOpen] = useState(defaultExpanded);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopyText = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  if (!evidenceList || evidenceList.length === 0) {
    return null;
  }

  // Generate preview line of cited sections
  const previewCitations = evidenceList
    .map((c) => `${c.document_name} ${c.section}`)
    .slice(0, 3)
    .join(" • ");

  return (
    <div className="rounded-2xl border border-stone-200 bg-stone-50/70 dark:border-stone-800 dark:bg-stone-900/60 overflow-hidden transition">
      {/* Toggle Header */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-4 text-left hover:bg-stone-100/60 dark:hover:bg-stone-800/40 transition flex flex-col sm:flex-row sm:items-center justify-between gap-3"
      >
        <div className="flex items-start sm:items-center gap-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 mt-0.5 sm:mt-0">
            <BookOpen className="h-4 w-4" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h4 className="text-xs sm:text-sm font-bold text-stone-900 dark:text-stone-100">
                {title}
              </h4>
              <span className="rounded-full bg-stone-200/80 px-2 py-0.2 text-[10px] font-bold text-stone-700 dark:bg-stone-700 dark:text-stone-300">
                {evidenceList.length} Official Chunks
              </span>
            </div>

            {/* Collapsed Preview Line */}
            <div className="mt-1 flex items-center gap-1.5 text-[11px] text-stone-600 dark:text-stone-400">
              <Bookmark className="h-3 w-3 text-amber-600 shrink-0" />
              <span className="truncate max-w-md sm:max-w-xl">
                <strong>Cited: </strong>
                {previewCitations}
                {evidenceList.length > 3 ? " & more..." : ""}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1 text-xs font-semibold text-amber-700 dark:text-amber-400 shrink-0 self-end sm:self-center">
          <span>{isOpen ? "Hide Full Statutes" : "View Full Statutes"}</span>
          {isOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </div>
      </button>

      {/* Expanded Chunks Content */}
      {isOpen && (
        <div className="p-4 pt-0 space-y-3 border-t border-stone-200/80 dark:border-stone-800 mt-2">
          {evidenceList.map((chunk, index) => {
            const chunkKey = chunk.id || `chunk-${index}`;
            return (
              <div
                key={chunkKey}
                className="rounded-xl border border-stone-200 bg-white p-4 shadow-2xs dark:border-stone-700/80 dark:bg-stone-800/60"
              >
                {/* Metadata Header */}
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-stone-100 pb-2.5 dark:border-stone-700/60">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded-md bg-stone-100 px-2 py-0.5 text-[10px] font-bold text-stone-800 dark:bg-stone-700 dark:text-stone-200">
                      {chunk.document_name}
                    </span>
                    <span className="rounded-md bg-amber-100 px-2 py-0.5 text-[10px] font-bold text-amber-900 dark:bg-amber-950 dark:text-amber-300">
                      {chunk.section}
                    </span>
                    <span className="text-[10px] text-stone-500 dark:text-stone-400">
                      • {chunk.authority}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    {/* Source URL Link */}
                    {chunk.source_url && (
                      <a
                        href={chunk.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-700 hover:text-amber-800 dark:text-amber-400 hover:underline"
                        title="View Official Source PDF"
                      >
                        <span>Official Gazette</span>
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    )}

                    {/* Copy Text Button */}
                    <button
                      type="button"
                      onClick={() => handleCopyText(chunk.text, chunkKey)}
                      className="inline-flex items-center gap-1 rounded-md border border-stone-200 px-2 py-0.5 text-[10px] text-stone-600 hover:bg-stone-50 dark:border-stone-700 dark:text-stone-300 dark:hover:bg-stone-700"
                      title="Copy Statutory Text"
                    >
                      {copiedId === chunkKey ? (
                        <>
                          <Check className="h-3 w-3 text-emerald-600" />
                          <span className="text-emerald-600 font-semibold">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="h-3 w-3 text-stone-500" />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* Verbatim Statutory Extract */}
                <blockquote className="mt-2.5 rounded-lg bg-stone-50 p-3 text-xs text-stone-700 italic border-l-3 border-amber-500 dark:bg-stone-900/50 dark:text-stone-300 leading-relaxed">
                  &quot;{chunk.text}&quot;
                </blockquote>

                {/* Footnote metadata */}
                <div className="mt-2 flex items-center justify-between text-[10px] text-stone-400">
                  <span>Sovereign Jurisdiction: {chunk.jurisdiction}</span>
                  {chunk.effective_date && <span>Statute Date: {chunk.effective_date}</span>}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

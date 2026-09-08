"use client";

import React from "react";
import { AlertTriangle, ShieldCheck, X, CheckCircle2 } from "lucide-react";

interface DisclaimerModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function DisclaimerModal({
  isOpen,
  onClose,
}: DisclaimerModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl rounded-2xl border border-stone-200 bg-white p-6 shadow-2xl dark:border-stone-800 dark:bg-stone-900 max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-full p-1.5 text-stone-400 hover:bg-stone-100 hover:text-stone-700 dark:hover:bg-stone-800 dark:hover:text-stone-200"
          aria-label="Close modal"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="flex items-center gap-3 border-b border-stone-200 pb-4 dark:border-stone-800">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-stone-900 dark:text-stone-100">
              Regulatory & Legal Disclaimer
            </h3>
            <p className="text-xs text-stone-500 dark:text-stone-400">
              IP-SAKTI Navigator · AI Decision-Support System
            </p>
          </div>
        </div>

        <div className="mt-4 space-y-3.5 text-sm text-stone-600 dark:text-stone-300 leading-relaxed">
          <div className="rounded-xl border border-amber-200 bg-amber-50/70 p-3.5 text-xs text-amber-900 dark:border-amber-900/50 dark:bg-amber-950/40 dark:text-amber-200">
            <div className="flex items-start gap-2">
              <AlertTriangle className="h-4 w-4 shrink-0 text-amber-600 dark:text-amber-400 mt-0.5" />
              <div>
                <strong className="font-semibold block mb-0.5">
                  Decision Support, Not Legal Advice (Rule 10):
                </strong>
                IP-SAKTI Navigator is an automated decision-support system designed to assist Ayurvedic innovators in understanding applicable Indian IP, biodiversity (ABS), and regulatory commercialization pathways. It is <strong>not a replacement</strong> for a registered Patent Attorney, Legal Counsel, or Regulatory Consultant.
              </div>
            </div>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex items-start gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
              <span>
                <strong>No Guaranteed Outcomes (Rule 2):</strong> The system uses cautious terms such as <em>&quot;may&quot;</em>, <em>&quot;potentially&quot;</em>, and <em>&quot;requires further assessment&quot;</em>. It never guarantees patent grant or regulatory approval.
              </span>
            </div>

            <div className="flex items-start gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
              <span>
                <strong>Evidence-Grounded (Rule 1 &amp; 4):</strong> Legal findings are strictly grounded in authoritative Indian statutes (The Patents Act 1970, The Biological Diversity Act 2002, The Drugs and Cosmetics Act 1940 &amp; Rules 1945, FSSAI Act 2006).
              </span>
            </div>

            <div className="flex items-start gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
              <span>
                <strong>Safe Abstention Active (Rule 6):</strong> When reliable statutory evidence is absent or claims are insufficient, the system safely abstains rather than generating speculative answers.
              </span>
            </div>

            <div className="flex items-start gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
              <span>
                <strong>India-First Jurisdiction (Rule 13):</strong> The current 5-day MVP exclusively evaluates Indian legal authorities. International patent systems (USPTO, EPO) and foreign regulations are intentionally separated.
              </span>
            </div>

            <div className="flex items-start gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
              <span>
                <strong>Human Escalation (Rule 9 &amp; 23):</strong> The system generates a structured case summary for human review. It does not provide instant live communication with an attorney.
              </span>
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-end border-t border-stone-200 pt-4 dark:border-stone-800">
          <button
            onClick={onClose}
            className="rounded-xl bg-stone-900 px-5 py-2 text-xs font-semibold text-white hover:bg-stone-800 dark:bg-stone-100 dark:text-stone-900 dark:hover:bg-stone-200 transition"
          >
            I Understand &amp; Agree
          </button>
        </div>
      </div>
    </div>
  );
}


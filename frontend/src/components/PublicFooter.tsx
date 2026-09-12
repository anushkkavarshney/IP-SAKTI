"use client";

import { useState } from "react";
import Link from "next/link";
import { Scale, ShieldCheck, ArrowRight } from "lucide-react";
import DisclaimerModal from "./DisclaimerModal";

export default function PublicFooter() {
  const [disclaimerOpen, setDisclaimerOpen] = useState(false);

  return (
    <footer className="border-t border-stone-200 bg-white dark:border-stone-800 dark:bg-stone-950 print:hidden">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div className="sm:col-span-2 lg:col-span-1">
            <div className="flex items-center gap-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-amber-600 to-emerald-700 text-white shadow-xs">
                <Scale className="h-5 w-5" />
              </div>
              <span className="text-sm font-bold text-stone-900 dark:text-white">
                IP-SAKTI <span className="text-amber-600 dark:text-amber-500">Navigator</span>
              </span>
            </div>
            <p className="mt-3 text-xs leading-relaxed text-stone-500 dark:text-stone-400">
              Evidence-first decision support for Ayurvedic innovators. India-only
              jurisdiction, independent claim verification, and safe abstention
              when the sources aren&apos;t conclusive.
            </p>
          </div>

          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-stone-500 dark:text-stone-400">
              Product
            </h3>
            <ul className="mt-3 space-y-2 text-sm">
              <li>
                <Link
                  href="/how-it-works"
                  className="text-stone-600 transition hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-200"
                >
                  How It Works
                </Link>
              </li>
              <li>
                <Link
                  href="/login"
                  className="text-stone-600 transition hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-200"
                >
                  Log in
                </Link>
              </li>
              <li>
                <Link
                  href="/login"
                  className="inline-flex items-center gap-1 text-stone-600 transition hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-200"
                >
                  <span>Start an assessment</span>
                  <ArrowRight className="h-3 w-3" />
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-stone-500 dark:text-stone-400">
              Product detail
            </h3>
            <ul className="mt-3 space-y-2 text-sm">
              <li>
                <Link
                  href="/#about"
                  className="text-stone-600 transition hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-200"
                >
                  What it does / doesn&apos;t do
                </Link>
              </li>
              <li>
                <Link
                  href="/how-it-works#safety"
                  className="text-stone-600 transition hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-200"
                >
                  Safety &amp; abstention
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-stone-500 dark:text-stone-400">
              Legal
            </h3>
            <ul className="mt-3 space-y-2 text-sm">
              <li>
                <button
                  type="button"
                  onClick={() => setDisclaimerOpen(true)}
                  className="inline-flex items-center gap-1.5 text-stone-600 transition hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-200"
                >
                  <ShieldCheck className="h-3.5 w-3.5 text-amber-600" />
                  <span>Disclaimer</span>
                </button>
              </li>
              <li>
                <Link
                  href="/privacy"
                  className="text-stone-600 transition hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-200"
                >
                  Privacy
                </Link>
              </li>
              <li>
                <Link
                  href="/terms"
                  className="text-stone-600 transition hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-200"
                >
                  Terms
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-10 flex flex-col items-center justify-between gap-3 border-t border-stone-200 pt-6 text-[11px] text-stone-400 dark:border-stone-800 dark:text-stone-500 sm:flex-row">
          <span>© 2026 IP-SAKTI Navigator · Smart India Hackathon 2026 (PS SIH26045)</span>
          <span>Not legal advice · Decision support only</span>
        </div>
      </div>

      <DisclaimerModal
        isOpen={disclaimerOpen}
        onClose={() => setDisclaimerOpen(false)}
      />
    </footer>
  );
}
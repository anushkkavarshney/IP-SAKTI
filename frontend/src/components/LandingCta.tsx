"use client";

import Link from "next/link";
import { ArrowRight, LogIn } from "lucide-react";

export default function LandingCta() {
  return (
    <section className="border-b border-stone-200 bg-gradient-to-b from-amber-50/70 to-white py-20 dark:border-stone-800 dark:from-stone-900/80 dark:to-stone-950">
      <div className="mx-auto max-w-3xl px-4 text-center sm:px-6">
        <h2 className="text-3xl font-extrabold tracking-tight text-stone-900 dark:text-white">
          Ready to map your formulation?
        </h2>
        <p className="mx-auto mt-3 max-w-xl text-sm leading-relaxed text-stone-600 dark:text-stone-400">
          Log in and start a new assessment. You can describe a proprietary
          extract, a classical formulation, or test how the system abstains on
          a deliberately vague claim.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Link
            href="/login"
            className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-amber-600 to-emerald-700 px-6 py-3 text-sm font-semibold text-white shadow-md transition hover:from-amber-700 hover:to-emerald-800"
          >
            <LogIn className="h-4 w-4" />
            <span>Log in to start</span>
          </Link>
          <Link
            href="/how-it-works"
            className="inline-flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-6 py-3 text-sm font-semibold text-stone-700 transition hover:bg-stone-50 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-300 dark:hover:bg-stone-800"
          >
            <span>Read the pipeline</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
        <p className="mt-6 text-[11px] text-stone-400 dark:text-stone-500">
          Demo login — any non-empty email and password will let you explore
          the full flow.
        </p>
      </div>
    </section>
  );
}
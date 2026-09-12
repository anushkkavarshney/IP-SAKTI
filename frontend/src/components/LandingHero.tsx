"use client";

import Link from "next/link";
import { Scale, ArrowRight, ShieldCheck } from "lucide-react";

export default function LandingHero() {
  return (
    <div className="relative overflow-hidden border-b border-stone-200 bg-gradient-to-b from-amber-50/60 via-white to-stone-50 dark:border-stone-800 dark:from-stone-950 dark:via-stone-900/60 dark:to-stone-950">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-72 bg-gradient-to-r from-amber-200/25 via-emerald-200/10 to-amber-200/25 blur-3xl" />

      <div className="relative mx-auto max-w-7xl px-4 py-20 sm:px-6 sm:py-28 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-stone-200 bg-white/80 px-3.5 py-1 text-xs font-semibold text-stone-600 shadow-xs dark:border-stone-700 dark:bg-stone-900/80 dark:text-stone-300">
            <Scale className="h-3.5 w-3.5 text-amber-600" />
            Smart India Hackathon 2026 · Problem Statement SIH26045
          </div>

          <h1 className="mt-6 text-4xl font-extrabold tracking-tight text-stone-900 dark:text-white sm:text-5xl">
            Turn an Ayurvedic innovation into an{" "}
            <span className="bg-gradient-to-r from-amber-600 to-emerald-700 bg-clip-text text-transparent">
              evidence-backed
            </span>{" "}
            IP and regulatory roadmap.
          </h1>

          <p className="mx-auto mt-5 max-w-2xl text-base leading-relaxed text-stone-600 dark:text-stone-300 sm:text-lg">
            IP-SAKTI Navigator reads a plain-language description of your
            formulation, asks a few targeted questions, then checks every claim
            against authoritative Indian statutes — The Patents Act 1970, the
            Biological Diversity Act 2002, and AYUSH/FSSAI rules — before it
            says anything.
          </p>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/login"
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-amber-600 to-emerald-700 px-6 py-3 text-sm font-semibold text-white shadow-md transition hover:from-amber-700 hover:to-emerald-800 focus:outline-hidden focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-2"
            >
              <span>Start an assessment</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/how-it-works"
              className="inline-flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-6 py-3 text-sm font-semibold text-stone-700 transition hover:bg-stone-50 focus:outline-hidden focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-2 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-300 dark:hover:bg-stone-800"
            >
              <span>How it works</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          <div className="mt-7 flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-xs text-stone-500 dark:text-stone-400">
            <span className="inline-flex items-center gap-1.5">
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
              India-first jurisdiction
            </span>
            <span className="inline-flex items-center gap-1.5">
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
              Evidence-first conclusions
            </span>
            <span className="inline-flex items-center gap-1.5">
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
              Abstains when the evidence is thin
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
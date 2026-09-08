"use client";

import React from "react";
import {
  Scale,
  Sparkles,
  ShieldAlert,
  Leaf,
  FileCheck2,
  Cpu,
  ArrowRight,
  BookOpen,
} from "lucide-react";

interface LandingHeroProps {
  onStartAnalysis: () => void;
}

export default function LandingHero({ onStartAnalysis }: LandingHeroProps) {
  return (
    <div className="relative overflow-hidden bg-gradient-to-b from-amber-50/50 via-white to-stone-50 dark:from-stone-950 dark:via-stone-900 dark:to-stone-950 border-b border-stone-200 dark:border-stone-800 py-12 sm:py-16">
      {/* Subtle Background Glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-64 bg-gradient-to-r from-amber-200/30 via-emerald-200/20 to-amber-200/30 blur-3xl pointer-events-none -z-10" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto">
          {/* Tag Pill */}
          <div className="inline-flex items-center gap-2 rounded-full border border-amber-300 bg-amber-100/70 px-3.5 py-1 text-xs font-semibold text-amber-900 dark:border-amber-800 dark:bg-amber-950/60 dark:text-amber-300 mb-5 shadow-xs">
            <Sparkles className="h-3.5 w-3.5 text-amber-600" />
            <span>SIH 2026 Problem Statement SIH26045</span>
            <span className="text-amber-400">•</span>
            <span className="font-normal">Evidence-First Legal AI</span>
          </div>

          {/* Main Headline */}
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-stone-900 dark:text-white">
            Ayurvedic Innovation to{" "}
            <span className="bg-gradient-to-r from-amber-600 to-emerald-700 bg-clip-text text-transparent">
              Evidence-Backed Roadmap
            </span>
          </h1>

          {/* Subtitle / Value Proposition */}
          <p className="mt-4 text-base sm:text-lg text-stone-600 dark:text-stone-300 leading-relaxed">
            Convert plain-language Ayurvedic formulations into a verified roadmap across{" "}
            <strong className="text-stone-900 dark:text-white font-semibold">
              Intellectual Property
            </strong>
            ,{" "}
            <strong className="text-stone-900 dark:text-white font-semibold">
              Biodiversity / ABS (NBA)
            </strong>
            , and{" "}
            <strong className="text-stone-900 dark:text-white font-semibold">
              AYUSH &amp; Drug Regulations
            </strong>
            —powered by independent claim verification and safe abstention.
          </p>

          {/* CTA & Demo Preset Trigger */}
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <button
              onClick={onStartAnalysis}
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-amber-600 to-emerald-700 px-6 py-3 text-sm font-semibold text-white shadow-md hover:from-amber-700 hover:to-emerald-800 focus:outline-hidden focus:ring-2 focus:ring-amber-500 focus:ring-offset-2 transition-all transform hover:-translate-y-0.5"
            >
              <span>Analyze Your Ayurvedic Innovation</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* 4 Architectural Pillars Grid */}
        <div className="mt-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="rounded-2xl border border-stone-200/80 bg-white/80 p-5 shadow-xs backdrop-blur-xs dark:border-stone-800 dark:bg-stone-900/80">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 mb-3">
              <BookOpen className="h-5 w-5" />
            </div>
            <h3 className="text-sm font-bold text-stone-900 dark:text-white">
              6-Category Classification
            </h3>
            <p className="mt-1.5 text-xs text-stone-600 dark:text-stone-400 leading-normal">
              Differentiates Classical vs Proprietary ASU Drugs, Phytopharmaceuticals, Nutraceuticals (FSSAI), and Cosmetics.
            </p>
          </div>

          <div className="rounded-2xl border border-stone-200/80 bg-white/80 p-5 shadow-xs backdrop-blur-xs dark:border-stone-800 dark:bg-stone-900/80">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 mb-3">
              <Scale className="h-5 w-5" />
            </div>
            <h3 className="text-sm font-bold text-stone-900 dark:text-white">
              IP &amp; Section 3(p) Scrutiny
            </h3>
            <p className="mt-1.5 text-xs text-stone-600 dark:text-stone-400 leading-normal">
              Identifies potential extraction process claims vs traditional knowledge exclusions and mere admixture bars.
            </p>
          </div>

          <div className="rounded-2xl border border-stone-200/80 bg-white/80 p-5 shadow-xs backdrop-blur-xs dark:border-stone-800 dark:bg-stone-900/80">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-100 text-teal-800 dark:bg-teal-950 dark:text-teal-300 mb-3">
              <Leaf className="h-5 w-5" />
            </div>
            <h3 className="text-sm font-bold text-stone-900 dark:text-white">
              Biodiversity &amp; ABS (NBA)
            </h3>
            <p className="mt-1.5 text-xs text-stone-600 dark:text-stone-400 leading-normal">
              Evaluates Biological Diversity Act compliance, Section 6 NBA approval obligations, and State Biodiversity Board intimations.
            </p>
          </div>

          <div className="rounded-2xl border border-stone-200/80 bg-white/80 p-5 shadow-xs backdrop-blur-xs dark:border-stone-800 dark:bg-stone-900/80">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300 mb-3">
              <FileCheck2 className="h-5 w-5" />
            </div>
            <h3 className="text-sm font-bold text-stone-900 dark:text-white">
              Claim Verification &amp; Abstention
            </h3>
            <p className="mt-1.5 text-xs text-stone-600 dark:text-stone-400 leading-normal">
              Every statement is verified against authoritative statutes. Weak evidence triggers safe abstention instead of hallucinations.
            </p>
          </div>
        </div>

        {/* Authoritative Corpus Source Badges */}
        <div className="mt-10 border-t border-stone-200/60 pt-6 dark:border-stone-800 text-center">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-stone-500 dark:text-stone-400 mb-3">
            Authoritative Legal Knowledge Base (India Corpus)
          </p>
          <div className="flex flex-wrap items-center justify-center gap-2 sm:gap-3 text-xs text-stone-600 dark:text-stone-400">
            <span className="rounded-lg bg-stone-100 dark:bg-stone-800/80 px-3 py-1 font-medium border border-stone-200/60 dark:border-stone-700">
              Indian Patent Office (IPO) · The Patents Act, 1970
            </span>
            <span className="rounded-lg bg-stone-100 dark:bg-stone-800/80 px-3 py-1 font-medium border border-stone-200/60 dark:border-stone-700">
              National Biodiversity Authority (NBA) · BDA 2002
            </span>
            <span className="rounded-lg bg-stone-100 dark:bg-stone-800/80 px-3 py-1 font-medium border border-stone-200/60 dark:border-stone-700">
              Ministry of AYUSH &amp; CDSCO · D&amp;C Act 1940 &amp; Rules 1945
            </span>
            <span className="rounded-lg bg-stone-100 dark:bg-stone-800/80 px-3 py-1 font-medium border border-stone-200/60 dark:border-stone-700">
              FSSAI · Nutraceutical Regulations 2016
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}


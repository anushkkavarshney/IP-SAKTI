"use client";

import React from "react";
import Link from "next/link";
import {
  MessageSquareText,
  HelpCircle,
  Layers,
  Route,
  Search,
  ShieldCheck,
  Cpu,
  ShieldAlert,
  Map,
  ArrowRight,
} from "lucide-react";

const STEPS = [
  {
    icon: MessageSquareText,
    title: "Describe your innovation",
    body: "Write the formulation in plain language — what it is, what it does, and how it's made. No legal knowledge required.",
  },
  {
    icon: HelpCircle,
    title: "Answer a few targeted questions",
    body: "Up to five statutory clarifiers covering intended use, classical heritage, extraction method, biological resources, and target jurisdiction.",
  },
  {
    icon: Layers,
    title: "Classify the formulation",
    body: "Routed into one of six categories — Classical ASU, Proprietary ASU, Phytopharmaceutical, Nutraceutical, Cosmetic, or Unknown.",
  },
  {
    icon: Route,
    title: "Identify the applicable pathways",
    body: "Routes the innovation to the IP (Patents Act, 1970), Biodiversity/ABS (BDA, 2002), and Regulatory (AYUSH/FSSAI) tracks that actually apply.",
  },
  {
    icon: Search,
    title: "Retrieve Indian legal evidence",
    body: "Pulls grounded statutory sections from a curated Indian corpus. Findings are anchored to retrieved statute text, not model memory.",
  },
  {
    icon: ShieldCheck,
    title: "Verify each claim",
    body: "Every generated assertion is cross-checked against the retrieved evidence and marked Supported, Partially Supported, or Unsupported.",
  },
  {
    icon: Cpu,
    title: "Calculate confidence",
    body: "A transparent 30/25/25/20 formula scores retrieval quality, source authority, claim support, and jurisdiction match on a 0–100 scale.",
  },
  {
    icon: ShieldAlert,
    title: "Abstain when evidence is insufficient",
    body: "If the sources don't support a confident answer, the system says so and refuses to speculate — it never fabricates legal conclusions.",
  },
  {
    icon: Map,
    title: "Generate a structured roadmap",
    body: "You get a clear next-steps roadmap plus an escalation brief with questions to put to a registered patent attorney or regulatory expert.",
  },
];

export function HowItWorksFlow() {
  return (
    <ol className="relative mx-auto max-w-3xl space-y-6" id="flow">
      {STEPS.map((step, index) => {
        const Icon = step.icon;
        return (
          <li
            key={step.title}
            className="relative flex gap-4 rounded-2xl border border-stone-200 bg-white p-5 shadow-2xs dark:border-stone-800 dark:bg-stone-900"
          >
            <div className="relative shrink-0">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">
                <Icon className="h-5 w-5" />
              </div>
              <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-stone-900 text-[10px] font-bold text-white dark:bg-stone-100 dark:text-stone-900">
                {index + 1}
              </span>
            </div>
            <div>
              <h3 className="text-sm font-bold text-stone-900 dark:text-stone-100">
                {step.title}
              </h3>
              <p className="mt-1 text-xs leading-relaxed text-stone-600 dark:text-stone-400">
                {step.body}
              </p>
            </div>
          </li>
        );
      })}
    </ol>
  );
}

const PHASES = [
  {
    icon: MessageSquareText,
    title: "Describe & clarify",
    steps: ["Describe in plain language", "Answer up to 5 questions"],
  },
  {
    icon: Search,
    title: "Evidence & analysis",
    steps: [
      "Classify the formulation",
      "Route IP / ABS / regulatory pathways",
      "Retrieve statute text",
      "Verify claims · score confidence",
    ],
  },
  {
    icon: Map,
    title: "Roadmap & review",
    steps: [
      "Abstain when evidence is thin",
      "Deliver a structured roadmap",
      "Escalation brief for counsel",
    ],
  },
];

export function HowItWorksSection() {
  return (
    <section id="how-it-works" className="border-b border-stone-200 bg-white py-20 dark:border-stone-800 dark:bg-stone-950">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <span className="text-xs font-bold uppercase tracking-wider text-amber-600 dark:text-amber-400">
            How it works
          </span>
          <h2 className="mt-2 text-3xl font-extrabold tracking-tight text-stone-900 dark:text-white">
            A description in. A grounded roadmap out.
          </h2>
          <p className="mt-3 text-sm leading-relaxed text-stone-600 dark:text-stone-400">
            Three phases. Ten minutes. Every conclusion traceable to a
            retrieved Indian statute.
          </p>
        </div>

        <div className="mt-12 grid gap-5 md:grid-cols-3">
          {PHASES.map((phase, idx) => {
            const Icon = phase.icon;
            return (
              <div
                key={phase.title}
                className="flex flex-col rounded-2xl border border-stone-200 bg-stone-50/60 p-6 dark:border-stone-800 dark:bg-stone-900/60"
              >
                <div className="flex items-center justify-between">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white text-amber-700 shadow-xs dark:bg-stone-800 dark:text-amber-400">
                    <Icon className="h-5 w-5" />
                  </div>
                  <span className="text-2xl font-black text-stone-200 dark:text-stone-800">
                    0{idx + 1}
                  </span>
                </div>
                <h3 className="mt-4 text-sm font-bold text-stone-900 dark:text-stone-100">
                  {phase.title}
                </h3>
                <ul className="mt-3 space-y-1.5">
                  {phase.steps.map((step) => (
                    <li
                      key={step}
                      className="flex items-start gap-2 text-xs text-stone-600 dark:text-stone-400"
                    >
                      <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                      {step}
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>

        <div className="mt-10 text-center">
          <Link
            href="/how-it-works"
            className="inline-flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-5 py-2.5 text-xs font-semibold text-stone-700 transition hover:bg-stone-50 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-300 dark:hover:bg-stone-800"
          >
            <span>See the full step-by-step pipeline</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </div>
    </section>
  );
}
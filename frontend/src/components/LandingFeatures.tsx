"use client";

import { Layers, Scale, Leaf, ShieldCheck } from "lucide-react";

const FEATURES = [
  {
    icon: Layers,
    title: "Six-way formulation classification",
    body: "Distinguishes Classical ASU medicines from Proprietary ASU drugs, phytopharmaceuticals, nutraceuticals (FSSAI), cosmetics, and unknown inputs — each governed by a different statute.",
  },
  {
    icon: Scale,
    title: "IP & traditional-knowledge scrutiny",
    body: "Flags Section 3(p) and Section 3(e) exclusions under the Patents Act. Identifies whether the extraction process might be claimed — and never promises a patent grant.",
  },
  {
    icon: Leaf,
    title: "Biodiversity & ABS checkpoints",
    body: "Surfaces NBA Form III and State Biodiversity Board obligations under the Biological Diversity Act, 2002 when the innovation uses Indian biological resources.",
  },
  {
    icon: ShieldCheck,
    title: "Claim verification & safe abstention",
    body: "Each assertion is checked against retrieved statutory text. When evidence is insufficient, the system abstains instead of guessing.",
  },
];

const SOURCES = [
  "Indian Patent Office · The Patents Act, 1970",
  "National Biodiversity Authority · BDA, 2002",
  "Ministry of AYUSH & CDSCO · D&C Act 1940 & Rules 1945",
  "FSSAI · Nutraceutical Regulations 2016",
];

export default function LandingFeatures() {
  return (
    <section className="border-b border-stone-200 bg-stone-50 py-20 dark:border-stone-800 dark:bg-stone-900/40">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <span className="text-xs font-bold uppercase tracking-wider text-amber-600 dark:text-amber-400">
            What it analyzes
          </span>
          <h2 className="mt-2 text-3xl font-extrabold tracking-tight text-stone-900 dark:text-white">
            Four checks before any recommendation
          </h2>
          <p className="mt-3 text-sm leading-relaxed text-stone-600 dark:text-stone-400">
            Scoped to Indian statutes, evidence-first, and deliberately
            conservative about what it claims.
          </p>
        </div>

        <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((feature) => {
            const Icon = feature.icon;
            return (
              <div
                key={feature.title}
                className="rounded-2xl border border-stone-200 bg-white p-6 shadow-2xs dark:border-stone-800 dark:bg-stone-900"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="mt-4 text-sm font-bold text-stone-900 dark:text-stone-100">
                  {feature.title}
                </h3>
                <p className="mt-2 text-xs leading-relaxed text-stone-600 dark:text-stone-400">
                  {feature.body}
                </p>
              </div>
            );
          })}
        </div>

        <div className="mt-10 flex flex-wrap items-center justify-center gap-2 text-[11px] text-stone-500 dark:text-stone-400">
          <span className="font-semibold uppercase tracking-wider">
            Knowledge base:
          </span>
          {SOURCES.map((source) => (
            <span
              key={source}
              className="rounded-lg border border-stone-200 bg-white px-3 py-1 font-medium dark:border-stone-800 dark:bg-stone-900"
            >
              {source}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
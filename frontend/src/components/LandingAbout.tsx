"use client";

import { CheckCircle2, XCircle } from "lucide-react";

const DOES = [
  {
    title: "India-first interpretation",
    body: "Evaluates the innovation strictly under Indian law — Patents Act 1970, Biological Diversity Act 2002, Drugs & Cosmetics Act/Rules, and FSSAI regulations.",
  },
  {
    title: "Evidence-grounded conclusions",
    body: "Every statement is tied to retrieved statute text with the document, section, and authority shown so you can check the source yourself.",
  },
  {
    title: "Conservative claims",
    body: "Uses cautious language — “may”, “potentially”, “based on the available evidence” — and recommends expert review where it matters.",
  },
  {
    title: "Safe abstention",
    body: "When the sources can't support a confident answer, the system says so openly instead of inventing a legal outcome.",
  },
];

const DOES_NOT = [
  "Provide legal advice. It's decision support, not a substitute for a registered patent attorney or regulatory consultant.",
  "Guarantee outcomes. A patent grant or AYUSH approval is never promised by this tool.",
  "Cover jurisdictions beyond India. International filings are intentionally out of scope for the MVP.",
  "Tell you a claim is legally true or false. Unsupported simply means the retrieved evidence couldn't verify it.",
];

export default function LandingAbout() {
  return (
    <section
      id="about"
      className="border-b border-stone-200 bg-white py-20 dark:border-stone-800 dark:bg-stone-950"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <span className="text-xs font-bold uppercase tracking-wider text-amber-600 dark:text-amber-400">
            About / product
          </span>
          <h2 className="mt-2 text-3xl font-extrabold tracking-tight text-stone-900 dark:text-white">
            What IP-SAKTI does — and what it doesn&apos;t
          </h2>
          <p className="mt-3 text-sm leading-relaxed text-stone-600 dark:text-stone-400">
            The point of this project is to keep an Ayurvedic innovator honest
            before they spend money on filings: here are the boundaries we
            respect.
          </p>
        </div>

        <div className="mx-auto mt-12 grid max-w-5xl gap-6 md:grid-cols-2">
          <div className="rounded-2xl border border-stone-200 bg-stone-50/60 p-6 dark:border-stone-800 dark:bg-stone-900/60">
            <h3 className="text-sm font-bold text-stone-900 dark:text-stone-100">
              Yes, it does this
            </h3>
            <ul className="mt-4 space-y-4">
              {DOES.map((item) => (
                <li key={item.title} className="flex items-start gap-3">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />
                  <div>
                    <span className="block text-xs font-bold text-stone-800 dark:text-stone-200">
                      {item.title}
                    </span>
                    <span className="mt-0.5 block text-xs leading-relaxed text-stone-600 dark:text-stone-400">
                      {item.body}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          <div className="rounded-2xl border border-stone-200 bg-stone-50/60 p-6 dark:border-stone-800 dark:bg-stone-900/60">
            <h3 className="text-sm font-bold text-stone-900 dark:text-stone-100">
              No, it won&apos;t do this
            </h3>
            <ul className="mt-4 space-y-4">
              {DOES_NOT.map((item) => (
                <li key={item} className="flex items-start gap-3">
                  <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-500" />
                  <span className="text-xs leading-relaxed text-stone-600 dark:text-stone-400">
                    {item}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
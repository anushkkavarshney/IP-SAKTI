import { Scale, FileText, AlertTriangle } from "lucide-react";

const SECTIONS = [
  {
    title: "Decision support only",
    body: "IP-SAKTI Navigator provides decision-support output for educational and demonstration purposes. It is not legal advice, does not create an attorney-client relationship, and must not be relied upon solely for patent, biodiversity, or regulatory filings.",
  },
  {
    title: "No guarantee of outcomes",
    body: "References to patent eligibility, AYUSH registration, or FSSAI compliance are indicative interpretive outputs based on retrieved statutory text. They are neither official determinations nor promises that any grant, approval, or registration will be issued.",
  },
  {
    title: "Evidence limitations",
    body: "The knowledge base covers Indian statutes only and may be incomplete or out of date. An \"unsupported\" or \"abstained\" result means the available evidence could not verify the claim — it does not mean the claim is false or unlawful.",
  },
  {
    title: "No confidential information",
    body: "The demo accepts any non-empty credentials and stores data locally in your browser only. Do not enter confidential, sensitive, or personal information. This project is a Smart India Hackathon 2026 prototype (PS SIH26045) by a student team.",
  },
];

export default function TermsPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-14 sm:px-6 sm:py-20">
      <div className="flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">
          <Scale className="h-5 w-5" />
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight text-stone-900 dark:text-white">
          Terms of Use
        </h1>
      </div>
      <p className="mt-4 text-sm leading-relaxed text-stone-600 dark:text-stone-400">
        Short, honest terms for a short, honest prototype. Last updated with
        IP-SAKTI Navigator.
      </p>

      <div className="mt-10 space-y-5">
        {SECTIONS.map((section, idx) => (
          <div
            key={section.title}
            className="rounded-2xl border border-stone-200 bg-white p-6 dark:border-stone-800 dark:bg-stone-900"
          >
            <div className="flex items-center gap-3">
              {idx === 0 ? (
                <FileText className="h-4 w-4 text-amber-600" />
              ) : (
                <AlertTriangle className="h-4 w-4 text-amber-600" />
              )}
              <h2 className="text-sm font-bold text-stone-900 dark:text-stone-100">
                {section.title}
              </h2>
            </div>
            <p className="mt-3 text-xs leading-relaxed text-stone-600 dark:text-stone-400">
              {section.body}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
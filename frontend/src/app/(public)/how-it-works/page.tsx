import { HowItWorksFlow } from "@/components/HowItWorksFlow";
import { Scale, ShieldAlert, GitBranch, ClipboardList } from "lucide-react";

const SAFETY_POINTS = [
  {
    icon: ShieldAlert,
    title: "Abstention over speculation",
    body: "The system can reach an abstained result (no confidence score) when retrieval or classification is too weak to justify an answer. This is a feature: it prevents confident-sounding but unsupported conclusions.",
  },
  {
    icon: GitBranch,
    title: "Branching, not guessing",
    body: "Each category routes to a different legal surface — Patents Act vs. BDA vs. AYUSH/FSSAI. The tool explains which pathway it followed and why.",
  },
  {
    icon: ClipboardList,
    title: "Escalation brief",
    body: "Every roadmap ends with concrete questions to take to a registered patent attorney or regulatory consultant. The tool lowers the cost of professional review; it doesn't replace it.",
  },
];

export default function HowItWorksPage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6 sm:py-20 lg:px-8">
      <div className="mx-auto max-w-2xl text-center">
        <div className="inline-flex items-center gap-2 rounded-full border border-stone-200 bg-white px-3.5 py-1 text-xs font-semibold text-stone-600 shadow-xs dark:border-stone-700 dark:bg-stone-900 dark:text-stone-300">
          <Scale className="h-3.5 w-3.5 text-amber-600" />
          The full pipeline
        </div>
        <h1 className="mt-5 text-4xl font-extrabold tracking-tight text-stone-900 dark:text-white">
          From description to roadmap
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-sm leading-relaxed text-stone-600 dark:text-stone-400">
          Nine steps turn a plain-language description into a grounded IP,
          biodiversity, and regulatory roadmap. Steps 5–8 are what make the
          result trustworthy — every claim is verified against retrieved
          Indian statute text.
        </p>
      </div>

      <div className="mt-14">
        <HowItWorksFlow />
      </div>

      <section id="safety" className="mx-auto mt-20 max-w-5xl">
        <div className="mx-auto max-w-2xl text-center">
          <span className="text-xs font-bold uppercase tracking-wider text-amber-600 dark:text-amber-400">
            Safety by design
          </span>
          <h2 className="mt-2 text-2xl font-extrabold tracking-tight text-stone-900 dark:text-white">
            How we handle uncertainty
          </h2>
        </div>
        <div className="mt-8 grid gap-5 md:grid-cols-3">
          {SAFETY_POINTS.map((point) => {
            const Icon = point.icon;
            return (
              <div
                key={point.title}
                className="rounded-2xl border border-stone-200 bg-white p-6 dark:border-stone-800 dark:bg-stone-900"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="mt-4 text-sm font-bold text-stone-900 dark:text-stone-100">
                  {point.title}
                </h3>
                <p className="mt-2 text-xs leading-relaxed text-stone-600 dark:text-stone-400">
                  {point.body}
                </p>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
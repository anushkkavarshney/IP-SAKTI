import { Scale, Info, Database, ShieldCheck } from "lucide-react";

const SECTIONS = [
  {
    icon: Info,
    title: "What we collect",
    body: "IP-SAKTI Navigator is a demonstration build. Please do not enter confidential business information or personal data into the system. Data you enter (your innovation description, assessment answers) is stored only in your own browser's local storage for this session and is not sent to any analytics or tracking service.",
  },
  {
    icon: Database,
    title: "Local storage",
    body: "Assessment reports are kept in your browser's local storage (key: IPSAKTI_REPORTS) so your history survives a page refresh on the same device. Clearing your browser data or using a different device removes this history. Your login is also local-only (fictional and never verified against any real account).",
  },
  {
    icon: ShieldCheck,
    title: "No personal data required",
    body: "The demo login accepts any non-empty email and does not verify it, request verification, or store the password. Do not use a real personal email or password. Delete your browser data for this site thoroughly if you entered anything you'd prefer not to keep.",
  },
];

export default function PrivacyPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-14 sm:px-6 sm:py-20">
      <div className="flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">
          <Scale className="h-5 w-5" />
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight text-stone-900 dark:text-white">
          Privacy
        </h1>
      </div>
      <p className="mt-4 text-sm leading-relaxed text-stone-600 dark:text-stone-400">
        Privacy is deliberately simple for this demonstration build. Updated
        with the IP-SAKTI Navigator app.
      </p>

      <div className="mt-10 space-y-5">
        {SECTIONS.map((section) => {
          const Icon = section.icon;
          return (
            <div
              key={section.title}
              className="rounded-2xl border border-stone-200 bg-white p-6 dark:border-stone-800 dark:bg-stone-900"
            >
              <div className="flex items-center gap-3">
                <Icon className="h-4 w-4 text-amber-600" />
                <h2 className="text-sm font-bold text-stone-900 dark:text-stone-100">
                  {section.title}
                </h2>
              </div>
              <p className="mt-3 text-xs leading-relaxed text-stone-600 dark:text-stone-400">
                {section.body}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
"use client";

import { useMemo } from "react";
import Link from "next/link";
import {
  Sparkles,
  FileText,
  Settings,
  ClipboardList,
  TrendingUp,
  ShieldAlert,
  CheckCircle2,
  ArrowRight,
  Scale,
} from "lucide-react";
import { useAuth } from "@/lib/auth";
import { readReports } from "@/lib/storage";
import { formatConfidenceLevel, formatDate, timeGreeting } from "@/lib/utils";

export default function HomePage() {
  const { user } = useAuth();
  const reports = useMemo(() => readReports(), []);

  const nonAbstained = reports.filter((r) => !r.abstained);
  const avgConfidence = nonAbstained.length
    ? Math.round(
        nonAbstained.reduce((acc, r) => acc + r.confidence, 0) / nonAbstained.length
      )
    : 0;
  const abstainedCount = reports.filter((r) => r.abstained).length;
  const supportedClaims = reports.reduce(
    (acc, r) => acc + r.verification.supported,
    0
  );

  const fullName = user?.name ?? "there";

  const stats = [
    {
      icon: ClipboardList,
      label: "Total assessments",
      value: reports.length,
      color: "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300",
    },
    {
      icon: TrendingUp,
      label: "Avg confidence",
      value: reports.length ? `${avgConfidence}%` : "—",
      color: "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300",
    },
    {
      icon: CheckCircle2,
      label: "Supported claims",
      value: supportedClaims,
      color: "bg-teal-100 text-teal-800 dark:bg-teal-950 dark:text-teal-300",
    },
    {
      icon: ShieldAlert,
      label: "Abstained reports",
      value: abstainedCount,
      color: "bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300",
    },
  ];

  const recent = reports.slice(0, 3);

  return (
    <div className="space-y-8">
      <section>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-amber-600 dark:text-amber-400">
              {timeGreeting()}
            </p>
            <h1 className="mt-1 text-3xl font-extrabold tracking-tight text-stone-900 dark:text-white">
              {fullName}
            </h1>
            <p className="mt-1.5 max-w-xl text-sm leading-relaxed text-stone-500 dark:text-stone-400">
              Here&apos;s what IP-SAKTI has mapped so far. Start a new
              assessment to explore another formulation.
            </p>
          </div>
          <Link
            href="/assessment"
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-600 to-emerald-700 px-5 py-2.5 text-xs font-semibold text-white shadow-md transition hover:from-amber-700 hover:to-emerald-800"
          >
            <Sparkles className="h-4 w-4" />
            <span>Start a new assessment</span>
          </Link>
        </div>
      </section>

      {reports.length === 0 ? (
        <section className="rounded-3xl border border-dashed border-stone-300 bg-white p-10 text-center dark:border-stone-700 dark:bg-stone-900">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">
            <Scale className="h-7 w-7" />
          </div>
          <h2 className="mt-4 text-lg font-bold text-stone-900 dark:text-stone-100">
            No assessments yet
          </h2>
          <p className="mx-auto mt-2 max-w-sm text-sm leading-relaxed text-stone-500 dark:text-stone-400">
            Describe an Ayurvedic formulation in plain language and IP-SAKTI
            will shape an IP, biodiversity, and regulatory roadmap around it.
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/assessment"
              className="inline-flex items-center gap-2 rounded-xl bg-stone-900 px-5 py-2.5 text-xs font-semibold text-white transition hover:bg-stone-800 dark:bg-stone-100 dark:text-stone-900 dark:hover:bg-stone-200"
            >
              <Sparkles className="h-3.5 w-3.5" />
              <span>Start your first assessment</span>
            </Link>
            <Link
              href="/how-it-works"
              className="inline-flex items-center gap-2 rounded-xl border border-stone-200 px-5 py-2.5 text-xs font-semibold text-stone-700 transition hover:bg-stone-50 dark:border-stone-700 dark:text-stone-300 dark:hover:bg-stone-800"
            >
              <span>How it works</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </section>
      ) : (
        <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <div
                key={stat.label}
                className="rounded-2xl border border-stone-200 bg-white p-5 dark:border-stone-800 dark:bg-stone-900"
              >
                <div className="flex items-center justify-between">
                  <div className={`flex h-9 w-9 items-center justify-center rounded-xl ${stat.color}`}>
                    <Icon className="h-4 w-4" />
                  </div>
                </div>
                <p className="mt-3 text-2xl font-extrabold text-stone-900 dark:text-white">
                  {stat.value}
                </p>
                <p className="mt-0.5 text-xs text-stone-500 dark:text-stone-400">
                  {stat.label}
                </p>
              </div>
            );
          })}
        </section>
      )}

      {reports.length > 0 && (
        <section>
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-stone-900 dark:text-stone-100">
              Recent assessments
            </h2>
            <Link
              href="/reports"
              className="inline-flex items-center gap-1 text-xs font-semibold text-amber-700 transition hover:text-amber-800 dark:text-amber-400 dark:hover:text-amber-300"
            >
              <span>View all</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>

          <div className="mt-4 space-y-3">
            {recent.map((report) => {
              const level = formatConfidenceLevel(report.confidenceLevel);
              return (
                <Link
                  key={report.id}
                  href="/reports"
                  className="group flex items-center gap-4 rounded-2xl border border-stone-200 bg-white p-4 transition hover:border-amber-300 hover:shadow-sm dark:border-stone-800 dark:bg-stone-900 dark:hover:border-amber-700"
                >
                  {report.abstained ? (
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300">
                      <ShieldAlert className="h-5 w-5" />
                    </div>
                  ) : (
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                      <FileText className="h-5 w-5" />
                    </div>
                  )}
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-bold text-stone-800 dark:text-stone-200">
                      {report.title}
                    </p>
                    <p className="mt-0.5 text-xs text-stone-500 dark:text-stone-400">
                      {formatDate(report.createdAt)} · {report.classification}
                      {report.isSampleData ? " · Sample" : ""}
                    </p>
                  </div>
                  <span
                    className={`hidden shrink-0 rounded-full border px-2.5 py-1 text-[10px] font-bold sm:inline ${level.bg}`}
                  >
                    {level.label}
                  </span>
                  <ArrowRight className="h-4 w-4 shrink-0 text-stone-300 transition group-hover:text-amber-500 dark:text-stone-600" />
                </Link>
              );
            })}
          </div>
        </section>
      )}

      <section className="grid gap-4 md:grid-cols-3">
        {[
          {
            icon: Sparkles,
            title: "New assessment",
            body: "Describe a formulation and run the evidence pipeline.",
            href: "/assessment",
            accent: "from-amber-600 to-emerald-700",
          },
          {
            icon: FileText,
            title: "My assessments",
            body: "Review saved roadmaps and verification tables.",
            href: "/reports",
            accent: "from-stone-700 to-stone-900",
          },
          {
            icon: Settings,
            title: "Settings",
            body: "Profile, display name, theme, and notifications.",
            href: "/settings",
            accent: "from-teal-700 to-emerald-900",
          },
        ].map((card) => {
          const Icon = card.icon;
          return (
            <Link
              key={card.title}
              href={card.href}
              className="group rounded-2xl border border-stone-200 bg-white p-5 transition hover:border-amber-300 hover:shadow-sm dark:border-stone-800 dark:bg-stone-900 dark:hover:border-amber-700"
            >
              <div
                className={`flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr text-white ${card.accent}`}
              >
                <Icon className="h-5 w-5" />
              </div>
              <h3 className="mt-4 text-sm font-bold text-stone-900 dark:text-stone-100">
                {card.title}
              </h3>
              <p className="mt-1 text-xs leading-relaxed text-stone-500 dark:text-stone-400">
                {card.body}
              </p>
            </Link>
          );
        })}
      </section>
    </div>
  );
}
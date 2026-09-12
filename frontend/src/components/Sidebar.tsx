"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Scale,
  Home,
  Sparkles,
  FileText,
  Settings,
  Info,
  ShieldCheck,
  LogOut,
  X,
  ChevronRight,
  Cpu,
  Leaf,
  Building2,
  FileCheck2,
  UserCheck,
  CircleUser,
} from "lucide-react";
import { useAuth } from "../lib/auth";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenDisclaimer: () => void;
}

const JUMP_LINKS = [
  { id: "section-classification", label: "Classification & Reason", icon: Sparkles, color: "text-amber-600" },
  { id: "section-confidence", label: "Confidence Gauge (30/25/25/20)", icon: Cpu, color: "text-emerald-600" },
  { id: "section-ip", label: "IP & Section 3(p) TK", icon: Scale, color: "text-amber-600" },
  { id: "section-abs", label: "Biodiversity / ABS (NBA)", icon: Leaf, color: "text-teal-600" },
  { id: "section-regulatory", label: "AYUSH Regulatory Steps", icon: Building2, color: "text-indigo-600" },
  { id: "section-verification", label: "Claim Verification Table", icon: FileCheck2, color: "text-emerald-600" },
  { id: "section-escalation", label: "Counsel Escalation Brief", icon: UserCheck, color: "text-amber-600" },
];

export default function Sidebar({ isOpen, onClose, onOpenDisclaimer }: SidebarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [hasActiveRoadmap, setHasActiveRoadmap] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    const params = new URLSearchParams(window.location.search);
    const isDashboard =
      pathname === "/assessment" && params.get("step") === "dashboard";
    // eslint-disable-next-line react-hooks/set-state-in-effect -- reads window URL, must run client-side
    setHasActiveRoadmap(isDashboard);
  }, [isOpen, pathname]);

  const jumpToSection = (elementId: string) => {
    const el = document.getElementById(elementId);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
      onClose();
    }
  };

  const navLink = (active: boolean) =>
    `flex w-full items-center gap-2.5 rounded-xl px-3 py-2.5 text-xs font-semibold transition ${
      active
        ? "bg-amber-100/70 text-amber-950 dark:bg-amber-950/60 dark:text-amber-200"
        : "text-stone-700 hover:bg-stone-100 dark:text-stone-300 dark:hover:bg-stone-800"
    }`;

  const isAssessment = pathname === "/assessment";

  return (
    <>
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-xs lg:hidden"
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed bottom-0 left-0 top-0 z-40 flex w-72 flex-col border-r border-stone-200 bg-white transition-transform duration-300 ease-in-out dark:border-stone-800 dark:bg-stone-900 ${
          isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        }`}
      >
        <div className="flex h-16 items-center justify-between border-b border-stone-200 px-5 dark:border-stone-800">
          <Link href="/home" onClick={onClose} className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-amber-600 to-emerald-700 text-white shadow-xs">
              <Scale className="h-5 w-5" />
            </div>
            <div>
              <span className="block text-sm font-bold text-stone-900 dark:text-white">
                IP-SAKTI <span className="text-amber-600 dark:text-amber-500">Navigator</span>
              </span>
              <p className="text-[10px] text-stone-500 dark:text-stone-400">
                SIH 2026 · PS SIH26045
              </p>
            </div>
          </Link>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-stone-400 hover:bg-stone-100 hover:text-stone-700 dark:hover:bg-stone-800 dark:hover:text-stone-200 lg:hidden"
            aria-label="Close navigation"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="flex-1 space-y-5 overflow-y-auto p-4">
          <nav className="space-y-1">
            <Link href="/home" onClick={onClose} className={navLink(pathname === "/home")}>
              <Home className="h-4 w-4 shrink-0" />
              <span>Home</span>
            </Link>
            <Link href="/assessment" onClick={onClose} className={navLink(isAssessment)}>
              <Sparkles className="h-4 w-4 shrink-0" />
              <span>New Assessment</span>
            </Link>
            <Link href="/reports" onClick={onClose} className={navLink(pathname === "/reports")}>
              <FileText className="h-4 w-4 shrink-0" />
              <span>My Assessments</span>
            </Link>
            <Link href="/settings" onClick={onClose} className={navLink(pathname === "/settings")}>
              <Settings className="h-4 w-4 shrink-0" />
              <span>Settings</span>
            </Link>
          </nav>

          <div className="border-t border-stone-200/70 pt-4 dark:border-stone-800">
            <span className="mb-2 block px-1 text-[11px] font-bold uppercase tracking-wider text-stone-400 dark:text-stone-500">
              Learn
            </span>
            <Link
              href="/how-it-works"
              onClick={onClose}
              className={navLink(pathname === "/how-it-works")}
            >
              <Info className="h-4 w-4 shrink-0" />
              <span>How It Works</span>
            </Link>
          </div>

          {hasActiveRoadmap && (
            <div className="border-t border-stone-200/70 pt-4 dark:border-stone-800">
              <span className="mb-2 block px-1 text-[11px] font-bold uppercase tracking-wider text-stone-400 dark:text-stone-500">
                Roadmap Navigation
              </span>
              <nav className="space-y-1 text-xs">
                {JUMP_LINKS.map((link) => {
                  const Icon = link.icon;
                  return (
                    <button
                      key={link.id}
                      onClick={() => jumpToSection(link.id)}
                      className="flex w-full items-center gap-2 rounded-lg px-2.5 py-1.5 text-left text-stone-600 transition hover:bg-stone-100 dark:text-stone-400 dark:hover:bg-stone-800"
                    >
                      <Icon className={`h-3.5 w-3.5 ${link.color}`} />
                      <span>{link.label}</span>
                    </button>
                  );
                })}
              </nav>
            </div>
          )}

          <div className="border-t border-stone-200/70 pt-4 dark:border-stone-800">
            <span className="mb-2 block px-1 text-[11px] font-bold uppercase tracking-wider text-stone-400 dark:text-stone-500">
              Indian Corpus Ingestion
            </span>
            <div className="space-y-1 rounded-xl border border-stone-200/60 bg-stone-50 p-3 text-[10px] text-stone-600 dark:border-stone-700/60 dark:bg-stone-800/50 dark:text-stone-400">
              <p>• The Patents Act, 1970 (IPO)</p>
              <p>• Biological Diversity Act, 2002 (NBA)</p>
              <p>• Drugs &amp; Cosmetics Rules, 1945 (AYUSH)</p>
              <p>• FSSAI Regulations, 2016</p>
            </div>
          </div>
        </div>

        <div className="space-y-2 border-t border-stone-200 p-4 dark:border-stone-800">
          <button
            onClick={() => {
              onOpenDisclaimer();
              onClose();
            }}
            className="flex w-full items-center gap-2 rounded-xl border border-stone-200 bg-stone-50/80 px-3 py-2 text-xs font-semibold text-stone-700 transition hover:bg-stone-100 dark:border-stone-700 dark:bg-stone-800/60 dark:text-stone-300"
          >
            <ShieldCheck className="h-4 w-4 text-amber-600" />
            <span>Legal Safety Notice</span>
            <ChevronRight className="ml-auto h-3.5 w-3.5 opacity-40" />
          </button>

          <div className="flex w-full items-center gap-2.5 rounded-xl border border-stone-200 bg-white px-3 py-2.5 dark:border-stone-700 dark:bg-stone-800/60">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-stone-100 text-stone-500 dark:bg-stone-700 dark:text-stone-300">
              <CircleUser className="h-5 w-5" />
            </div>
            <div className="min-w-0 flex-1">
              <span className="block truncate text-xs font-bold text-stone-800 dark:text-stone-200">
                {user?.name ?? "Demo User"}
              </span>
              <span className="block truncate text-[10px] text-stone-500 dark:text-stone-400">
                {user?.email ?? "demo@ip-sakti.in"}
              </span>
            </div>
            <button
              onClick={() => {
                logout();
                onClose();
              }}
              className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-stone-500 transition hover:bg-rose-50 hover:text-rose-600 dark:hover:bg-rose-950/50 dark:hover:text-rose-400"
              aria-label="Log out"
              title="Log out"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
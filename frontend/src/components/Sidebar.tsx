"use client";

import React from "react";
import {
  Scale,
  Sparkles,
  BookOpen,
  ShieldAlert,
  Leaf,
  Building2,
  FileCheck2,
  Cpu,
  UserCheck,
  RotateCcw,
  ExternalLink,
  ShieldCheck,
  X,
  Layers,
  ChevronRight,
} from "lucide-react";
import { PresetScenarioId } from "../types/roadmap";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  currentStep: "input" | "clarifying" | "loading" | "dashboard";
  activePreset?: PresetScenarioId;
  onSelectPreset: (presetId: PresetScenarioId) => void;
  onNewAnalysis: () => void;
  onOpenDisclaimer: () => void;
  hasActiveRoadmap: boolean;
}

export default function Sidebar({
  isOpen,
  onClose,
  currentStep,
  activePreset = "ashwagandha",
  onSelectPreset,
  onNewAnalysis,
  onOpenDisclaimer,
  hasActiveRoadmap,
}: SidebarProps) {
  const jumpToSection = (elementId: string) => {
    const el = document.getElementById(elementId);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
      onClose();
    }
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-xs lg:hidden"
          aria-hidden="true"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-40 w-72 bg-white border-r border-stone-200 dark:bg-stone-900 dark:border-stone-800 flex flex-col transition-transform duration-300 ease-in-out ${
          isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        }`}
      >
        {/* Sidebar Header */}
        <div className="flex h-16 items-center justify-between px-5 border-b border-stone-200 dark:border-stone-800">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-amber-600 to-emerald-700 text-white shadow-xs">
              <Scale className="h-5 w-5" />
            </div>
            <div>
              <span className="text-sm font-bold text-stone-900 dark:text-white">
                IP-SAKTI <span className="text-amber-600">Navigator</span>
              </span>
              <p className="text-[10px] text-stone-500 dark:text-stone-400">
                SIH 2026 · PS SIH26045
              </p>
            </div>
          </div>

          {/* Close button on mobile */}
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-stone-400 hover:text-stone-700 hover:bg-stone-100 dark:hover:bg-stone-800 dark:hover:text-stone-200 lg:hidden"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Demo Mode / Sample Data Pill */}
        <div className="p-3 bg-stone-50/80 dark:bg-stone-950/60 border-b border-stone-200/80 dark:border-stone-800">
          <div className="flex items-center justify-between text-[11px]">
            <span className="flex items-center gap-1.5 font-semibold text-stone-700 dark:text-stone-300">
              <span className="h-2 w-2 rounded-full bg-amber-500 animate-pulse" />
              Standalone Mode
            </span>
            <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[9px] font-bold text-amber-900 dark:bg-amber-950 dark:text-amber-300">
              Sample Data
            </span>
          </div>
        </div>

        {/* Scrollable Nav Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {/* Main Action: New Analysis */}
          <div>
            <button
              onClick={() => {
                onNewAnalysis();
                onClose();
              }}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-stone-900 px-4 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-stone-800 dark:bg-stone-100 dark:text-stone-900 dark:hover:bg-stone-200 transition"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              <span>Start New Analysis</span>
            </button>
          </div>

          {/* 3 Quick Demo Preset Scenarios */}
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-stone-400 dark:text-stone-500 block mb-2 px-1">
              Verified Demo Presets
            </span>
            <div className="space-y-1.5">
              <button
                onClick={() => {
                  onSelectPreset("ashwagandha");
                  onClose();
                }}
                className={`w-full text-left rounded-xl px-3 py-2 text-xs transition flex items-center justify-between ${
                  activePreset === "ashwagandha" && currentStep === "dashboard"
                    ? "bg-amber-100/70 text-amber-950 font-bold dark:bg-amber-950/60 dark:text-amber-200"
                    : "text-stone-700 hover:bg-stone-100 dark:text-stone-300 dark:hover:bg-stone-800"
                }`}
              >
                <div className="flex items-center gap-2 truncate">
                  <Sparkles className="h-3.5 w-3.5 text-amber-600 shrink-0" />
                  <span className="truncate">Ashwagandha Extract</span>
                </div>
                <ChevronRight className="h-3 w-3 opacity-40 shrink-0" />
              </button>

              <button
                onClick={() => {
                  onSelectPreset("triphala");
                  onClose();
                }}
                className={`w-full text-left rounded-xl px-3 py-2 text-xs transition flex items-center justify-between ${
                  activePreset === "triphala" && currentStep === "dashboard"
                    ? "bg-emerald-100/70 text-emerald-950 font-bold dark:bg-emerald-950/60 dark:text-emerald-200"
                    : "text-stone-700 hover:bg-stone-100 dark:text-stone-300 dark:hover:bg-stone-800"
                }`}
              >
                <div className="flex items-center gap-2 truncate">
                  <BookOpen className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
                  <span className="truncate">Classical Triphala Churna</span>
                </div>
                <ChevronRight className="h-3 w-3 opacity-40 shrink-0" />
              </button>

              <button
                onClick={() => {
                  onSelectPreset("abstention");
                  onClose();
                }}
                className={`w-full text-left rounded-xl px-3 py-2 text-xs transition flex items-center justify-between ${
                  activePreset === "abstention" && currentStep === "dashboard"
                    ? "bg-rose-100/70 text-rose-950 font-bold dark:bg-rose-950/60 dark:text-rose-200"
                    : "text-stone-700 hover:bg-stone-100 dark:text-stone-300 dark:hover:bg-stone-800"
                }`}
              >
                <div className="flex items-center gap-2 truncate">
                  <ShieldAlert className="h-3.5 w-3.5 text-rose-600 shrink-0" />
                  <span className="truncate">Safe Abstention Test</span>
                </div>
                <ChevronRight className="h-3 w-3 opacity-40 shrink-0" />
              </button>
            </div>
          </div>

          {/* Active Roadmap Section Jump Links (When viewing report) */}
          {hasActiveRoadmap && (
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-stone-400 dark:text-stone-500 block mb-2 px-1">
                Roadmap Navigation
              </span>
              <nav className="space-y-1 text-xs">
                <button
                  onClick={() => jumpToSection("section-classification")}
                  className="w-full text-left rounded-lg px-2.5 py-1.5 text-stone-600 hover:bg-stone-100 dark:text-stone-400 dark:hover:bg-stone-800 flex items-center gap-2"
                >
                  <Sparkles className="h-3.5 w-3.5 text-amber-600" />
                  <span>Classification &amp; Reason</span>
                </button>
                <button
                  onClick={() => jumpToSection("section-confidence")}
                  className="w-full text-left rounded-lg px-2.5 py-1.5 text-stone-600 hover:bg-stone-100 dark:text-stone-400 dark:hover:bg-stone-800 flex items-center gap-2"
                >
                  <Cpu className="h-3.5 w-3.5 text-emerald-600" />
                  <span>Confidence Gauge (30/25/25/20)</span>
                </button>
                <button
                  onClick={() => jumpToSection("section-ip")}
                  className="w-full text-left rounded-lg px-2.5 py-1.5 text-stone-600 hover:bg-stone-100 dark:text-stone-400 dark:hover:bg-stone-800 flex items-center gap-2"
                >
                  <Scale className="h-3.5 w-3.5 text-amber-600" />
                  <span>IP &amp; Section 3(p) TK</span>
                </button>
                <button
                  onClick={() => jumpToSection("section-abs")}
                  className="w-full text-left rounded-lg px-2.5 py-1.5 text-stone-600 hover:bg-stone-100 dark:text-stone-400 dark:hover:bg-stone-800 flex items-center gap-2"
                >
                  <Leaf className="h-3.5 w-3.5 text-teal-600" />
                  <span>Biodiversity / ABS (NBA)</span>
                </button>
                <button
                  onClick={() => jumpToSection("section-regulatory")}
                  className="w-full text-left rounded-lg px-2.5 py-1.5 text-stone-600 hover:bg-stone-100 dark:text-stone-400 dark:hover:bg-stone-800 flex items-center gap-2"
                >
                  <Building2 className="h-3.5 w-3.5 text-indigo-600" />
                  <span>AYUSH Regulatory Steps</span>
                </button>
                <button
                  onClick={() => jumpToSection("section-verification")}
                  className="w-full text-left rounded-lg px-2.5 py-1.5 text-stone-600 hover:bg-stone-100 dark:text-stone-400 dark:hover:bg-stone-800 flex items-center gap-2"
                >
                  <FileCheck2 className="h-3.5 w-3.5 text-emerald-600" />
                  <span>Claim Verification Table</span>
                </button>
                <button
                  onClick={() => jumpToSection("section-escalation")}
                  className="w-full text-left rounded-lg px-2.5 py-1.5 text-stone-600 hover:bg-stone-100 dark:text-stone-400 dark:hover:bg-stone-800 flex items-center gap-2"
                >
                  <UserCheck className="h-3.5 w-3.5 text-amber-600" />
                  <span>Counsel Escalation Brief</span>
                </button>
              </nav>
            </div>
          )}

          {/* Authoritative Knowledge Base Info */}
          <div className="pt-2 border-t border-stone-200/60 dark:border-stone-800">
            <span className="text-[11px] font-bold uppercase tracking-wider text-stone-400 dark:text-stone-500 block mb-2 px-1">
              Indian Corpus Ingestion
            </span>
            <div className="rounded-xl bg-stone-50 p-3 text-[10px] text-stone-600 dark:bg-stone-800/50 dark:text-stone-400 space-y-1 border border-stone-200/60 dark:border-stone-700/60">
              <p>• The Patents Act, 1970 (IPO)</p>
              <p>• Biological Diversity Act, 2002 (NBA)</p>
              <p>• Drugs &amp; Cosmetics Rules, 1945 (AYUSH)</p>
              <p>• FSSAI Regulations, 2016</p>
            </div>
          </div>
        </div>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-stone-200 dark:border-stone-800 space-y-2">
          <button
            onClick={() => {
              onOpenDisclaimer();
              onClose();
            }}
            className="w-full flex items-center justify-between rounded-xl border border-stone-200 bg-stone-50/80 px-3 py-2 text-xs font-semibold text-stone-700 hover:bg-stone-100 dark:border-stone-700 dark:bg-stone-800/60 dark:text-stone-300"
          >
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-amber-600" />
              <span>Legal Safety Notice</span>
            </div>
            <span className="text-[10px] text-stone-400">10 Rules</span>
          </button>
        </div>
      </aside>
    </>
  );
}


"use client";

import React from "react";
import {
  ShieldCheck,
  Scale,
  Menu,
  Sparkles,
  Info,
} from "lucide-react";

interface NavbarProps {
  isLiveBackend?: boolean;
  onToggleSidebar: () => void;
  onOpenDisclaimer: () => void;
  activeScenarioName?: string;
}

export default function Navbar({
  isLiveBackend = false,
  onToggleSidebar,
  onOpenDisclaimer,
  activeScenarioName,
}: NavbarProps) {
  return (
    <header className="sticky top-0 z-30 w-full border-b border-stone-200 bg-white/95 backdrop-blur-md dark:border-stone-800 dark:bg-stone-950/95">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Left: Hamburger Menu & Brand */}
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleSidebar}
            className="flex h-10 w-10 items-center justify-center rounded-xl border border-stone-200 text-stone-600 hover:bg-stone-100 hover:text-stone-900 dark:border-stone-700 dark:text-stone-300 dark:hover:bg-stone-800 transition"
            aria-label="Toggle Sidebar Navigation"
          >
            <Menu className="h-5 w-5" />
          </button>

          <div className="flex items-center gap-2.5">
            <div className="hidden sm:flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-amber-600 to-emerald-700 text-white shadow-xs">
              <Scale className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-base sm:text-lg font-bold tracking-tight text-stone-900 dark:text-white">
                  IP-SAKTI <span className="text-amber-600 dark:text-amber-500">Navigator</span>
                </span>
                <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-bold text-amber-800 dark:bg-amber-950 dark:text-amber-300 border border-amber-300/60">
                  SIH 2026
                </span>
              </div>
              <p className="hidden md:block text-[11px] text-stone-500 dark:text-stone-400">
                Ayurvedic IP, ABS &amp; Regulatory Commercialization Roadmap
              </p>
            </div>
          </div>
        </div>

        {/* Right Status Badges & Disclaimers */}
        <div className="flex items-center gap-2.5">
          {/* Active Scenario Indicator if selected */}
          {activeScenarioName && (
            <div className="hidden xl:flex items-center gap-1.5 rounded-full bg-stone-100 px-3 py-1 text-xs font-semibold text-stone-700 dark:bg-stone-800 dark:text-stone-300 border border-stone-200 dark:border-stone-700">
              <Sparkles className="h-3 w-3 text-amber-600" />
              <span>Scenario: <strong className="text-stone-900 dark:text-stone-100">{activeScenarioName}</strong></span>
            </div>
          )}

          {/* Sample Data Notice Badge (Requested by user) */}
          <div className="flex items-center gap-1.5 rounded-full bg-amber-50 dark:bg-amber-950/40 px-2.5 py-1 text-[11px] font-bold text-amber-900 dark:text-amber-200 border border-amber-200 dark:border-amber-800/60">
            <span className="h-2 w-2 rounded-full bg-amber-500 animate-pulse" />
            <span className="hidden sm:inline">Illustrative Output —</span>
            <span>Sample Data</span>
          </div>

          {/* Legal Notice Modal Trigger */}
          <button
            onClick={onOpenDisclaimer}
            className="flex items-center gap-1 rounded-xl border border-stone-200 bg-white px-3 py-1.5 text-xs font-medium text-stone-700 hover:bg-stone-50 hover:text-stone-900 dark:border-stone-700 dark:bg-stone-800 dark:text-stone-300 dark:hover:bg-stone-700 transition"
            title="Legal Safety Notice"
          >
            <ShieldCheck className="h-3.5 w-3.5 text-amber-600" />
            <span className="hidden sm:inline">Safety Rules</span>
          </button>
        </div>
      </div>
    </header>
  );
}

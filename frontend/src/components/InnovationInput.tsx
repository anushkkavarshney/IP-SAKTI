"use client";

import React, { useState } from "react";
import {
  Sparkles,
  ArrowRight,
  HelpCircle,
  AlertCircle,
  Info,
  CheckCircle2,
  Lock,
} from "lucide-react";
import { PresetScenarioId } from "../types/roadmap";

interface InnovationInputProps {
  initialValue?: string;
  initialPreset?: PresetScenarioId;
  onSubmit: (description: string, presetId: PresetScenarioId) => void;
}

export default function InnovationInput({
  initialValue = "",
  initialPreset = "ashwagandha",
  onSubmit,
}: InnovationInputProps) {
  const [selectedPreset, setSelectedPreset] = useState<PresetScenarioId>(initialPreset);
  const [description, setDescription] = useState(initialValue);
  const [error, setError] = useState<string | null>(null);

  const presets: {
    id: PresetScenarioId;
    title: string;
    desc: string;
    tag: string;
    badge: string;
    details: string;
  }[] = [
    {
      id: "ashwagandha",
      title: "Canonical Demo — Ashwagandha Extraction",
      desc: "I developed a modified Ashwagandha formulation using a new extraction process for stress relief.",
      tag: "Proprietary ASU Drug · Rule 158B",
      badge: "Section 49 Canonical Scenario",
      details: "Novel solvent extraction yield, Section 3(p) TK scrutiny, NBA Form III approval required.",
    },
    {
      id: "triphala",
      title: "Classical Formulation — Triphala Churna",
      desc: "A classical Triphala Churna prepared strictly according to Sharangadhara Samhita textual references for digestive balance.",
      tag: "Classical Ayurvedic · Form 25D",
      badge: "Classical Treaty Adherence",
      details: "Absolute Section 3(p) patent bar, Section 40 NTAC commodity list, Rule 158B trial exemption.",
    },
    {
      id: "abstention",
      title: "Safe Abstention Test — Vague / Miracle Claim",
      desc: "A miracle herbal powder 100% guaranteed to cure all stress and chronic ailments in 3 days with fast-track patent grant without clinical trials.",
      tag: "Anti-Hallucination · Rule 6",
      badge: "Safe Abstention Guard",
      details: "Demonstrates how the system quarantines unsupported claims and abstains rather than hallucinating.",
    },
  ];

  // Initialize description from preset if empty
  React.useEffect(() => {
    if (!description) {
      const match = presets.find((p) => p.id === selectedPreset);
      if (match) setDescription(match.desc);
    }
  }, []);

  const handlePresetSelect = (preset: typeof presets[0]) => {
    setSelectedPreset(preset.id);
    setDescription(preset.desc);
    setError(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim() || description.trim().length < 15) {
      setError(
        "Please describe your innovation in at least 15 characters so the system can evaluate it accurately."
      );
      return;
    }
    setError(null);
    onSubmit(description.trim(), selectedPreset);
  };

  return (
    <div className="mx-auto max-w-4xl px-4 sm:px-6 py-8">
      <div className="rounded-3xl border border-stone-200 bg-white p-6 sm:p-8 shadow-sm dark:border-stone-800 dark:bg-stone-900">
        {/* Card Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-stone-100 pb-5 dark:border-stone-800">
          <div>
            <div className="flex items-center gap-2">
              <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-bold text-amber-800 dark:bg-amber-950 dark:text-amber-300">
                Step 1: Innovation Selection
              </span>
              <span className="text-xs text-stone-500 dark:text-stone-400">
                Decision-Support Input
              </span>
            </div>
            <h2 className="text-xl font-bold text-stone-900 dark:text-stone-100 mt-1">
              Select or Describe Your Ayurvedic Innovation
            </h2>
          </div>

          <div className="flex items-center gap-1.5 rounded-full bg-stone-100 px-3 py-1 text-xs font-medium text-stone-600 dark:bg-stone-800 dark:text-stone-300">
            <HelpCircle className="h-3.5 w-3.5 text-amber-600" />
            <span>Statutory Jurisdiction: India First</span>
          </div>
        </div>

        {/* Informative Standalone Mode / Custom Input Notice */}
        <div className="mt-5 rounded-2xl border border-sky-200 bg-sky-50/80 p-4 dark:border-sky-900/60 dark:bg-sky-950/40 text-xs text-sky-950 dark:text-sky-200 flex items-start gap-3">
          <Info className="h-4 w-4 text-sky-600 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-semibold block">
              Demo Environment Notice:
            </span>
            <p className="text-[11px] text-sky-900 dark:text-sky-300 leading-relaxed">
              Custom open-ended free text analysis will be fully dynamically reasoned once Member 2&apos;s FastAPI backend is connected. In current <strong>Standalone / Demo Mode</strong>, please select one of the three verified test scenarios below to see full statutory citations and claim verification in action.
            </p>
          </div>
        </div>

        {/* 3 Preset Scenarios Grid */}
        <div className="mt-6 space-y-3">
          <label className="text-xs font-bold uppercase tracking-wider text-stone-600 dark:text-stone-400 block">
            Select a verified demo scenario:
          </label>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
            {presets.map((p) => {
              const isSelected = selectedPreset === p.id;
              return (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => handlePresetSelect(p)}
                  className={`text-left rounded-2xl border p-4 transition flex flex-col justify-between relative ${
                    isSelected
                      ? "border-amber-500 bg-amber-50/70 dark:bg-amber-950/40 dark:border-amber-600 shadow-sm ring-2 ring-amber-500/20"
                      : "border-stone-200 bg-stone-50/60 hover:bg-stone-100 hover:border-stone-300 dark:border-stone-800 dark:bg-stone-800/40 dark:hover:bg-stone-800"
                  }`}
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between gap-1">
                      <span className="rounded-full bg-white px-2 py-0.5 text-[9px] font-bold text-stone-700 border border-stone-200 dark:bg-stone-900 dark:text-stone-300 dark:border-stone-700">
                        {p.badge}
                      </span>
                      {isSelected && (
                        <CheckCircle2 className="h-4 w-4 text-amber-600 shrink-0" />
                      )}
                    </div>

                    <h4 className="text-xs font-bold text-stone-900 dark:text-stone-100">
                      {p.title}
                    </h4>

                    <p className="text-[11px] text-stone-500 dark:text-stone-400 leading-snug">
                      {p.details}
                    </p>
                  </div>

                  <div className="mt-3 pt-2 border-t border-stone-200/60 dark:border-stone-700/60 text-[10px] font-semibold text-amber-800 dark:text-amber-300">
                    {p.tag}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Selected Innovation Text View / Edit Form */}
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <div className="flex items-center justify-between text-xs font-semibold text-stone-700 dark:text-stone-300 mb-1.5">
              <span>Selected Innovation Description:</span>
              <span className="text-stone-400 text-[11px]">{description.length} chars</span>
            </div>
            <textarea
              value={description}
              onChange={(e) => {
                setDescription(e.target.value);
                setSelectedPreset("custom");
                if (error) setError(null);
              }}
              rows={3}
              placeholder="e.g. I developed a modified Ashwagandha formulation using a new extraction process for stress relief..."
              className="w-full rounded-2xl border border-stone-300 bg-stone-50/50 p-4 text-xs sm:text-sm text-stone-900 placeholder:text-stone-400 focus:border-amber-500 focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20 dark:border-stone-700 dark:bg-stone-800/50 dark:text-stone-100 dark:placeholder:text-stone-500 dark:focus:bg-stone-900 transition"
            />
          </div>

          {error && (
            <div className="flex items-center gap-2 rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800 dark:border-rose-900/50 dark:bg-rose-950/40 dark:text-rose-200">
              <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
              <span>{error}</span>
            </div>
          )}

          {/* Action Row */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
            <span className="text-[11px] text-stone-500 dark:text-stone-400">
              Active Profile: <strong className="text-stone-800 dark:text-stone-200 capitalize">{selectedPreset}</strong>
            </span>

            <button
              type="submit"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-600 to-emerald-700 px-6 py-2.5 text-xs font-semibold text-white shadow-sm hover:from-amber-700 hover:to-emerald-800 focus:outline-hidden focus:ring-2 focus:ring-amber-500 focus:ring-offset-2 transition transform hover:-translate-y-0.5"
            >
              <span>Continue to Clarification (4–5 Questions)</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

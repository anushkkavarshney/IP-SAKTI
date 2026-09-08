"use client";

import React, { useState } from "react";
import { FinalRoadmapResponse } from "../types/roadmap";
import ConfidenceCard from "./ConfidenceCard";
import ClaimVerificationTable from "./ClaimVerificationTable";
import EvidenceDrawer from "./EvidenceDrawer";
import {
  Sparkles,
  Scale,
  Leaf,
  FileCheck2,
  AlertTriangle,
  ArrowRight,
  Download,
  RotateCcw,
  CheckCircle2,
  Building2,
  BookOpen,
  UserCheck,
  Share2,
  Printer,
  ShieldCheck,
  Info,
} from "lucide-react";

interface RoadmapDashboardProps {
  roadmap: FinalRoadmapResponse;
  innovationDescription: string;
  isSampleData?: boolean;
  onReset: () => void;
}

export default function RoadmapDashboard({
  roadmap,
  innovationDescription,
  isSampleData = true,
  onReset,
}: RoadmapDashboardProps) {
  const {
    classification,
    ip,
    abs,
    regulatory,
    verification,
    confidence,
    abstain,
    abstain_reason,
    expert_escalation,
  } = roadmap;

  const [activeTab, setActiveTab] = useState<
    "all" | "ip" | "abs" | "regulatory" | "verification"
  >("all");

  const handleExportJSON = () => {
    const dataStr =
      "data:text/json;charset=utf-8," +
      encodeURIComponent(JSON.stringify(roadmap, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute(
      "download",
      `IP_SAKTI_Roadmap_${classification.category.replace(/\s+/g, "_")}_${Date.now()}.json`
    );
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const handleDownloadPDF = () => {
    window.print();
  };

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6 space-y-8 print:p-0 print:space-y-4">
      {/* Top Notice Banner: Explicit Sample Data & Demo Environment Indicator */}
      {isSampleData && (
        <div className="rounded-2xl border border-amber-200 bg-amber-50/90 p-3.5 sm:px-5 dark:border-amber-900/60 dark:bg-amber-950/40 text-xs text-amber-950 dark:text-amber-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2 shadow-2xs print:hidden">
          <div className="flex items-center gap-2">
            <Info className="h-4 w-4 text-amber-600 shrink-0" />
            <span>
              <strong>Illustrative Output — Sample Data (Standalone Demo Mode):</strong> Results below illustrate the exact output contract for this scenario. Full end-to-end live model generation activates upon connecting Member 2&apos;s FastAPI backend.
            </span>
          </div>
          <span className="rounded-md bg-amber-200/80 px-2 py-0.5 text-[10px] font-bold text-amber-900 dark:bg-amber-900 dark:text-amber-200 shrink-0 self-start sm:self-auto">
            Section 33 Contract
          </span>
        </div>
      )}

      {/* Top Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-stone-200 pb-5 dark:border-stone-800 print:border-none">
        <div>
          <div className="flex items-center gap-2">
            <span className="rounded-full bg-emerald-100 px-3 py-0.5 text-xs font-bold text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300/60">
              Roadmap Synthesized
            </span>
            <span className="text-xs text-stone-500 dark:text-stone-400">
              Statutory Territory: <strong>India First</strong>
            </span>
          </div>
          <h1 className="mt-1 text-2xl sm:text-3xl font-black text-stone-900 dark:text-white tracking-tight">
            Commercialization &amp; Regulatory Roadmap
          </h1>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-2 print:hidden">
          <button
            onClick={handleDownloadPDF}
            className="inline-flex items-center gap-1.5 rounded-xl border border-stone-200 bg-white px-3.5 py-2 text-xs font-semibold text-stone-700 hover:bg-stone-50 shadow-2xs dark:border-stone-700 dark:bg-stone-800 dark:text-stone-200 dark:hover:bg-stone-700 transition"
            title="Download formatted print / PDF report"
          >
            <Printer className="h-3.5 w-3.5 text-indigo-600" />
            <span>Download PDF / Print</span>
          </button>

          <button
            onClick={handleExportJSON}
            className="inline-flex items-center gap-1.5 rounded-xl border border-stone-200 bg-white px-3.5 py-2 text-xs font-semibold text-stone-700 hover:bg-stone-50 shadow-2xs dark:border-stone-700 dark:bg-stone-800 dark:text-stone-200 dark:hover:bg-stone-700 transition"
            title="Download JSON Contract conforming to Section 33"
          >
            <Download className="h-3.5 w-3.5 text-amber-600" />
            <span>Export JSON</span>
          </button>

          <button
            onClick={onReset}
            className="inline-flex items-center gap-1.5 rounded-xl bg-stone-900 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-stone-800 dark:bg-stone-100 dark:text-stone-900 dark:hover:bg-stone-200 transition"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>New Analysis</span>
          </button>
        </div>
      </div>

      {/* Safe Abstention Callout (Section 22 of Roadmap) */}
      {abstain && (
        <div className="rounded-3xl border-2 border-rose-300 bg-rose-50/90 p-6 shadow-sm dark:border-rose-800 dark:bg-rose-950/50">
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-rose-100 text-rose-800 dark:bg-rose-900 dark:text-rose-200 ring-4 ring-rose-50 dark:ring-rose-900/30">
              <AlertTriangle className="h-6 w-6" />
            </div>
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-rose-950 dark:text-rose-100">
                  Safe Abstention Activated (Rule 6 Anti-Hallucination Guard)
                </h3>
                <span className="rounded-full bg-rose-200 px-2.5 py-0.5 text-[10px] font-extrabold text-rose-900 dark:bg-rose-900 dark:text-rose-200">
                  Refused Speculative Output
                </span>
              </div>
              <p className="text-xs sm:text-sm text-rose-900 dark:text-rose-200 leading-relaxed">
                {abstain_reason ||
                  "The available authoritative sources do not provide sufficient statutory evidence to confidently determine a commercialization pathway. In accordance with Rule 6, the system safely abstains to prevent fabricated legal outcomes."}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 1. Formulation Classification Card (Section 6) */}
      <section
        id="section-classification"
        className="rounded-3xl border border-stone-200 bg-white p-6 sm:p-8 shadow-sm dark:border-stone-800 dark:bg-stone-900 transition"
      >
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-stone-100 pb-6 dark:border-stone-800">
          <div className="space-y-1">
            <span className="text-[11px] font-bold uppercase tracking-wider text-amber-600 dark:text-amber-400">
              Formulation Classification (Section 6)
            </span>
            <h2 className="text-2xl sm:text-3xl font-black text-stone-900 dark:text-white flex flex-wrap items-center gap-3">
              <span>{classification.category}</span>
              <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-800 border border-emerald-200 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800">
                Confidence: {(classification.confidence * 100).toFixed(0)}%
              </span>
            </h2>
          </div>

          <div className="rounded-2xl bg-stone-50 p-3.5 dark:bg-stone-800/60 border border-stone-200/70 dark:border-stone-700/60 max-w-lg">
            <div className="text-[11px] font-semibold text-stone-500 dark:text-stone-400">
              Evaluated Innovation Input:
            </div>
            <p className="mt-0.5 text-xs text-stone-800 dark:text-stone-200 italic line-clamp-3">
              &quot;{innovationDescription}&quot;
            </p>
          </div>
        </div>

        <div className="mt-5">
          <h4 className="text-xs font-bold uppercase tracking-wider text-stone-500 dark:text-stone-400 mb-1.5">
            Classification Rationale &amp; Legal Context
          </h4>
          <p className="text-xs sm:text-sm text-stone-700 dark:text-stone-300 leading-relaxed">
            {classification.reason}
          </p>
        </div>
      </section>

      {/* 2. Confidence Engine Section (Section 21) */}
      <section id="section-confidence">
        <ConfidenceCard confidence={confidence} abstain={abstain} />
      </section>

      {/* Navigation Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-stone-200 pb-3 dark:border-stone-800 print:hidden">
        <button
          onClick={() => setActiveTab("all")}
          className={`rounded-xl px-4 py-2 text-xs font-bold transition ${
            activeTab === "all"
              ? "bg-amber-600 text-white shadow-xs"
              : "bg-stone-100 text-stone-700 hover:bg-stone-200 dark:bg-stone-800 dark:text-stone-300"
          }`}
        >
          All Pathways Overview
        </button>
        <button
          onClick={() => setActiveTab("ip")}
          className={`rounded-xl px-4 py-2 text-xs font-bold transition ${
            activeTab === "ip"
              ? "bg-amber-600 text-white shadow-xs"
              : "bg-stone-100 text-stone-700 hover:bg-stone-200 dark:bg-stone-800 dark:text-stone-300"
          }`}
        >
          IP &amp; Patentability
        </button>
        <button
          onClick={() => setActiveTab("abs")}
          className={`rounded-xl px-4 py-2 text-xs font-bold transition ${
            activeTab === "abs"
              ? "bg-amber-600 text-white shadow-xs"
              : "bg-stone-100 text-stone-700 hover:bg-stone-200 dark:bg-stone-800 dark:text-stone-300"
          }`}
        >
          Biodiversity &amp; ABS (NBA)
        </button>
        <button
          onClick={() => setActiveTab("regulatory")}
          className={`rounded-xl px-4 py-2 text-xs font-bold transition ${
            activeTab === "regulatory"
              ? "bg-amber-600 text-white shadow-xs"
              : "bg-stone-100 text-stone-700 hover:bg-stone-200 dark:bg-stone-800 dark:text-stone-300"
          }`}
        >
          AYUSH Regulatory Roadmap
        </button>
        <button
          onClick={() => setActiveTab("verification")}
          className={`rounded-xl px-4 py-2 text-xs font-bold transition ${
            activeTab === "verification"
              ? "bg-amber-600 text-white shadow-xs"
              : "bg-stone-100 text-stone-700 hover:bg-stone-200 dark:bg-stone-800 dark:text-stone-300"
          }`}
        >
          Claim Verification
        </button>
      </div>

      {/* 3. IP & Patentability Module (Section 9 & 10) */}
      {(activeTab === "all" || activeTab === "ip") && (
        <section
          id="section-ip"
          className="rounded-3xl border border-stone-200 bg-white p-6 sm:p-8 shadow-sm dark:border-stone-800 dark:bg-stone-900 space-y-6"
        >
          <div className="flex items-center gap-3 border-b border-stone-100 pb-4 dark:border-stone-800">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">
              <Scale className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-stone-900 dark:text-white">
                Intellectual Property &amp; Patentability Analysis
              </h3>
              <p className="text-xs text-stone-500 dark:text-stone-400">
                Evaluation under The Patents Act, 1970 (IPO) · Section 3(p) TK &amp; Section 3(e) Exclusions
              </p>
            </div>
          </div>

          <div className="rounded-2xl bg-stone-50 p-4 dark:bg-stone-800/40 border border-stone-200/70 dark:border-stone-700/60">
            <h4 className="text-xs font-bold text-stone-700 dark:text-stone-300 uppercase tracking-wider mb-1">
              Assessment Summary
            </h4>
            <p className="text-xs sm:text-sm text-stone-600 dark:text-stone-300 leading-relaxed">
              {ip.analysis}
            </p>
          </div>

          {/* Active Flags */}
          {ip.flags && ip.flags.length > 0 && (
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-stone-500 dark:text-stone-400 mb-2">
                Active IP &amp; Prior-Art Flags
              </h4>
              <div className="flex flex-wrap gap-2">
                {ip.flags.map((flag, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center gap-1.5 rounded-xl border border-amber-300 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-900 dark:border-amber-800 dark:bg-amber-950/50 dark:text-amber-200"
                  >
                    <AlertTriangle className="h-3.5 w-3.5 text-amber-600" />
                    <span>{flag}</span>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Patentability Guidelines */}
          {ip.patentability_considerations && ip.patentability_considerations.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-stone-500 dark:text-stone-400">
                Patentability Strategic Guidelines
              </h4>
              <ul className="space-y-2 text-xs text-stone-600 dark:text-stone-300">
                {ip.patentability_considerations.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Traditional Knowledge Alert */}
          {ip.traditional_knowledge_flags && ip.traditional_knowledge_flags.length > 0 && (
            <div className="rounded-2xl border border-amber-200 bg-amber-50/60 p-4 dark:border-amber-900/60 dark:bg-amber-950/30">
              <h4 className="text-xs font-bold text-amber-950 dark:text-amber-200 flex items-center gap-1.5 mb-1.5">
                <BookOpen className="h-4 w-4 text-amber-600" />
                <span>Traditional Knowledge / TKDL Prior-Art Alert (Section 10)</span>
              </h4>
              <ul className="space-y-1 text-xs text-amber-900 dark:text-amber-300">
                {ip.traditional_knowledge_flags.map((tk, idx) => (
                  <li key={idx} className="flex items-start gap-1.5">
                    <span>•</span>
                    <span>{tk}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <EvidenceDrawer
            evidenceList={ip.evidence}
            title="IP Statutory Citations (The Patents Act, 1970)"
          />
        </section>
      )}

      {/* 4. Biodiversity & ABS Module (Section 11) */}
      {(activeTab === "all" || activeTab === "abs") && (
        <section
          id="section-abs"
          className="rounded-3xl border border-stone-200 bg-white p-6 sm:p-8 shadow-sm dark:border-stone-800 dark:bg-stone-900 space-y-6"
        >
          <div className="flex items-center justify-between gap-4 border-b border-stone-100 pb-4 dark:border-stone-800">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-100 text-teal-800 dark:bg-teal-950 dark:text-teal-300">
                <Leaf className="h-5 w-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-bold text-stone-900 dark:text-white">
                    Access &amp; Benefit Sharing (ABS) &amp; Biodiversity
                  </h3>
                  <span
                    className={`rounded-full px-2.5 py-0.5 text-xs font-bold border ${
                      abs.applicable
                        ? "bg-teal-100 text-teal-800 border-teal-300 dark:bg-teal-950 dark:text-teal-300"
                        : "bg-stone-100 text-stone-600 border-stone-200 dark:bg-stone-800 dark:text-stone-400"
                    }`}
                  >
                    {abs.applicable ? "ABS Applicable" : "ABS Exemption Noted"}
                  </span>
                </div>
                <p className="text-xs text-stone-500 dark:text-stone-400">
                  The Biological Diversity Act, 2002 · National Biodiversity Authority (NBA)
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-2xl bg-stone-50 p-4 dark:bg-stone-800/40 border border-stone-200/70 dark:border-stone-700/60">
            <h4 className="text-xs font-bold text-stone-700 dark:text-stone-300 uppercase tracking-wider mb-1">
              Biodiversity Applicability Analysis
            </h4>
            <p className="text-xs sm:text-sm text-stone-600 dark:text-stone-300 leading-relaxed">
              {abs.analysis}
            </p>
          </div>

          {abs.biological_resource_identified && (
            <div className="flex items-center gap-2 rounded-xl bg-teal-50/80 p-3 text-xs text-teal-900 dark:bg-teal-950/40 dark:text-teal-200 border border-teal-200/80 dark:border-teal-800">
              <Leaf className="h-4 w-4 text-teal-600 shrink-0" />
              <span>
                <strong>Identified Biological Material:</strong> {abs.biological_resource_identified}
              </span>
            </div>
          )}

          {abs.nba_action_items && abs.nba_action_items.length > 0 && (
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-stone-500 dark:text-stone-400 mb-2">
                Mandatory National Biodiversity Authority (NBA) Checkpoints
              </h4>
              <div className="space-y-2">
                {abs.nba_action_items.map((action, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-2.5 rounded-xl border border-stone-200/80 p-3 text-xs text-stone-700 dark:border-stone-800 dark:text-stone-300"
                  >
                    <CheckCircle2 className="h-4 w-4 text-teal-600 shrink-0 mt-0.5" />
                    <span>{action}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <EvidenceDrawer
            evidenceList={abs.evidence}
            title="Biodiversity Statutory Citations (Biological Diversity Act, 2002)"
          />
        </section>
      )}

      {/* 5. Regulatory Pathway Module (Section 12) */}
      {(activeTab === "all" || activeTab === "regulatory") && (
        <section
          id="section-regulatory"
          className="rounded-3xl border border-stone-200 bg-white p-6 sm:p-8 shadow-sm dark:border-stone-800 dark:bg-stone-900 space-y-6"
        >
          <div className="flex items-center gap-3 border-b border-stone-100 pb-4 dark:border-stone-800">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300">
              <Building2 className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold text-stone-900 dark:text-white">
                  Regulatory Pathway: {regulatory.pathway}
                </h3>
                <span className="rounded-full bg-indigo-100 px-2.5 py-0.5 text-xs font-bold text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300">
                  {regulatory.jurisdiction}
                </span>
              </div>
              <p className="text-xs text-stone-500 dark:text-stone-400">
                The Drugs and Cosmetics Act, 1940 &amp; Rules, 1945 · Ministry of AYUSH &amp; CDSCO
              </p>
            </div>
          </div>

          {/* Sequential Step-by-Step Pathway */}
          {regulatory.steps && regulatory.steps.length > 0 && (
            <div className="space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-stone-500 dark:text-stone-400">
                Recommended Step-by-Step Approval Protocol
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {regulatory.steps.map((step) => (
                  <div
                    key={step.step_number}
                    className="rounded-2xl border border-stone-200/80 bg-stone-50/50 p-4 dark:border-stone-800 dark:bg-stone-800/40 space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-indigo-600 text-white text-xs font-bold">
                        {step.step_number}
                      </span>
                      <span className="rounded-md bg-stone-200/70 px-2 py-0.5 text-[10px] font-semibold text-stone-700 dark:bg-stone-700 dark:text-stone-300">
                        {step.authority}
                      </span>
                    </div>

                    <h5 className="text-xs sm:text-sm font-bold text-stone-900 dark:text-stone-100">
                      {step.title}
                    </h5>

                    <p className="text-xs text-stone-600 dark:text-stone-400 leading-relaxed">
                      {step.description}
                    </p>

                    {step.requirements && (
                      <div className="border-t border-stone-200/60 pt-2 dark:border-stone-700/60 text-[11px] text-stone-500 dark:text-stone-400">
                        <strong>Prerequisites: </strong>
                        {step.requirements.join(", ")}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          <EvidenceDrawer
            evidenceList={regulatory.evidence}
            title="Regulatory Statutory Citations (D&C Rules, 1945)"
          />
        </section>
      )}

      {/* 6. Independent Claim Verification Table (Section 19 & 47) */}
      {(activeTab === "all" || activeTab === "verification") && (
        <section id="section-verification">
          <ClaimVerificationTable verification={verification} />
        </section>
      )}

      {/* 7. Human Expert Escalation Section (Section 23) */}
      {expert_escalation && (
        <section
          id="section-escalation"
          className="rounded-3xl border border-stone-200 bg-white p-6 sm:p-8 shadow-sm dark:border-stone-800 dark:bg-stone-900 space-y-4"
        >
          <div className="flex items-center gap-3 border-b border-stone-100 pb-4 dark:border-stone-800">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">
              <UserCheck className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold text-stone-900 dark:text-white">
                  Human Expert Escalation Dossier
                </h3>
                <span className="rounded-full bg-stone-100 px-2.5 py-0.5 text-xs font-semibold text-stone-700 dark:bg-stone-800 dark:text-stone-300">
                  Section 23
                </span>
              </div>
              <p className="text-xs text-stone-500 dark:text-stone-400">
                Structured legal briefing for consultation with a registered Indian Patent Attorney or Regulatory Specialist
              </p>
            </div>
          </div>

          <div className="rounded-2xl bg-amber-50/50 p-4 border border-amber-200/80 dark:bg-amber-950/20 dark:border-amber-900/40 text-xs text-stone-700 dark:text-stone-300">
            <strong>Escalation Evaluation: </strong>
            <span>{expert_escalation.reason}</span>
          </div>

          {expert_escalation.key_questions_for_counsel && (
            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-stone-500 dark:text-stone-400">
                Statutory Questions to Pose to Your Legal Counsel:
              </h4>
              <ul className="space-y-2 text-xs text-stone-700 dark:text-stone-300">
                {expert_escalation.key_questions_for_counsel.map((q, idx) => (
                  <li
                    key={idx}
                    className="flex items-start gap-2.5 rounded-xl border border-stone-100 p-3 dark:border-stone-800"
                  >
                    <span className="font-bold text-amber-600">Q{idx + 1}:</span>
                    <span>{q}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}

      {/* 8. Persistent In-Page Disclaimer Banner (Requested by user) */}
      <footer className="rounded-3xl border border-stone-200 bg-stone-50/80 p-6 dark:border-stone-800 dark:bg-stone-900/60 text-xs text-stone-600 dark:text-stone-400 space-y-3">
        <div className="flex items-center gap-2 font-bold text-stone-800 dark:text-stone-200">
          <ShieldCheck className="h-4 w-4 text-amber-600 shrink-0" />
          <span>Statutory Decision-Support Notice &amp; Compliance Safeguards</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-[11px] leading-relaxed">
          <div className="p-3 bg-white dark:bg-stone-800/60 rounded-xl border border-stone-200/60 dark:border-stone-700/60">
            <strong className="text-stone-800 dark:text-stone-200 block mb-0.5">Rule 10: Decision Support Only</strong>
            This platform is an automated decision-support engine. It does not provide binding legal counsel or substitute registered patent attorneys.
          </div>
          <div className="p-3 bg-white dark:bg-stone-800/60 rounded-xl border border-stone-200/60 dark:border-stone-700/60">
            <strong className="text-stone-800 dark:text-stone-200 block mb-0.5">Rule 2: No Guaranteed Outcomes</strong>
            All evaluations use cautious terminology (&quot;may&quot;, &quot;potentially&quot;). Patent grant or AYUSH approval is never promised.
          </div>
          <div className="p-3 bg-white dark:bg-stone-800/60 rounded-xl border border-stone-200/60 dark:border-stone-700/60">
            <strong className="text-stone-800 dark:text-stone-200 block mb-0.5">Rule 6: Safe Abstention</strong>
            If statutory evidence is insufficient, the system safely abstains rather than producing hallucinated legal provisions.
          </div>
          <div className="p-3 bg-white dark:bg-stone-800/60 rounded-xl border border-stone-200/60 dark:border-stone-700/60">
            <strong className="text-stone-800 dark:text-stone-200 block mb-0.5">Rule 13: India First</strong>
            All current findings are strictly evaluated under sovereign Indian statutes (The Patents Act 1970, BDA 2002, D&amp;C Act 1940, FSSAI).
          </div>
        </div>
      </footer>
    </div>
  );
}

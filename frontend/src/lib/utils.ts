import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatConfidenceLevel(level: "HIGH" | "MEDIUM" | "LOW") {
  switch (level) {
    case "HIGH":
      return {
        label: "High Confidence",
        bg: "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800",
        dot: "bg-emerald-500",
      };
    case "MEDIUM":
      return {
        label: "Medium Confidence",
        bg: "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800",
        dot: "bg-amber-500",
      };
    case "LOW":
      return {
        label: "Low Confidence (Caution)",
        bg: "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800",
        dot: "bg-rose-500",
      };
  }
}

export function formatVerificationStatus(status: "supported" | "partially_supported" | "unsupported") {
  switch (status) {
    case "supported":
      return {
        label: "Supported by Evidence",
        badge: "bg-emerald-100 text-emerald-800 border-emerald-300 dark:bg-emerald-900/50 dark:text-emerald-200 dark:border-emerald-700",
        icon: "CheckCircle2",
      };
    case "partially_supported":
      return {
        label: "Partially Supported / Caution",
        badge: "bg-amber-100 text-amber-800 border-amber-300 dark:bg-amber-900/50 dark:text-amber-200 dark:border-amber-700",
        icon: "AlertTriangle",
      };
    case "unsupported":
      return {
        label: "Unsupported / Flagged",
        badge: "bg-rose-100 text-rose-800 border-rose-300 dark:bg-rose-900/50 dark:text-rose-200 dark:border-rose-700",
        icon: "XCircle",
      };
  }
}


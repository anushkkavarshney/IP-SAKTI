import { AssessmentRecord, ProfileSettings } from "../types/assessment";

export const STORAGE_KEYS = {
  AUTH: "IPSAKTI_AUTH",
  USER: "IPSAKTI_USER",
  REPORTS: "IPSAKTI_REPORTS",
  PROFILE: "IPSAKTI_PROFILE",
  THEME: "IPSAKTI_THEME",
} as const;

export function safeRead<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  try {
    const raw = window.localStorage.getItem(key);
    if (raw == null) return fallback;
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

export function safeWrite(key: string, value: unknown): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // storage unavailable (private mode / quota) — degrade silently
  }
}

export function readReports(): AssessmentRecord[] {
  const parsed = safeRead<unknown>(STORAGE_KEYS.REPORTS, []);
  if (!Array.isArray(parsed)) return [];
  return parsed.filter(
    (r): r is AssessmentRecord =>
      !!r &&
      typeof r === "object" &&
      typeof (r as AssessmentRecord).id === "string" &&
      typeof (r as AssessmentRecord).title === "string" &&
      typeof (r as AssessmentRecord).createdAt === "string"
  );
}

export function saveReport(record: AssessmentRecord): AssessmentRecord[] {
  const reports = readReports();
  const next = [record, ...reports.filter((r) => r.id !== record.id)].slice(0, 50);
  safeWrite(STORAGE_KEYS.REPORTS, next);
  return next;
}

export function readProfile(): ProfileSettings {
  const parsed = safeRead<Partial<ProfileSettings>>(STORAGE_KEYS.PROFILE, {});
  return {
    displayName:
      typeof parsed.displayName === "string" ? parsed.displayName : undefined,
    role: typeof parsed.role === "string" ? parsed.role : undefined,
    prefersNotifications:
      typeof parsed.prefersNotifications === "boolean"
        ? parsed.prefersNotifications
        : true,
  };
}

export function saveProfile(profile: ProfileSettings): void {
  safeWrite(STORAGE_KEYS.PROFILE, profile);
}
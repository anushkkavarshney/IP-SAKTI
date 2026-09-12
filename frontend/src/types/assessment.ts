export interface AssessmentRecord {
  id: string;
  title: string;
  createdAt: string;
  classification: string;
  confidence: number;
  confidenceLevel: "HIGH" | "MEDIUM" | "LOW";
  abstained: boolean;
  abstainReason?: string;
  summary?: string;
  isSampleData: boolean;
  verification: {
    total: number;
    supported: number;
    partial: number;
    unsupported: number;
  };
}

export interface ProfileSettings {
  displayName?: string;
  role?: string;
  prefersNotifications: boolean;
}

export type ThemePreference = "light" | "dark" | "system";
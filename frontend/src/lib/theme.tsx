"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { ThemePreference } from "../types/assessment";
import { STORAGE_KEYS } from "./storage";

interface ThemeContextValue {
  theme: ThemePreference;
  setTheme: (theme: ThemePreference) => void;
  resolvedDark: boolean;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

function systemPrefersDark(): boolean {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

function applyTheme(theme: ThemePreference): boolean {
  const dark =
    theme === "dark" || (theme === "system" && systemPrefersDark());
  document.documentElement.classList.toggle("dark", dark);
  return dark;
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<ThemePreference>("system");
  const [resolvedDark, setResolvedDark] = useState(false);

  useEffect(() => {
    let stored: ThemePreference = "system";
    try {
      const value = window.localStorage.getItem(STORAGE_KEYS.THEME);
      if (value === "light" || value === "dark" || value === "system") {
        stored = value;
      }
    } catch {
      // ignore storage errors
    }
    // eslint-disable-next-line react-hooks/set-state-in-effect -- hydration: apply persisted theme after mount
    setThemeState(stored);
    setResolvedDark(applyTheme(stored));
  }, []);

  const setTheme = useCallback((next: ThemePreference) => {
    setThemeState(next);
    try {
      window.localStorage.setItem(STORAGE_KEYS.THEME, next);
    } catch {
      // ignore storage errors
    }
    setResolvedDark(applyTheme(next));
  }, []);

  useEffect(() => {
    if (theme !== "system") return;
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => setResolvedDark(applyTheme("system"));
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme, resolvedDark }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used within ThemeProvider");
  return ctx;
}

/** Inline script injected into the server-rendered <body> to avoid a dark-mode flash. */
export const themeInitScript = `try{var t=localStorage.getItem('IPSAKTI_THEME')||'system';if(t==='dark'||(t==='system'&&window.matchMedia('(prefers-color-scheme: dark)').matches)){document.documentElement.classList.add('dark');}}catch(e){}`;
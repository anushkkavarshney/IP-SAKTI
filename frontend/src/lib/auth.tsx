"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { STORAGE_KEYS } from "./storage";

export interface AuthUser {
  name: string;
  email: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isHydrated: boolean;
  login: (email: string, displayName?: string) => void;
  logout: () => void;
  updateUser: (patch: Partial<Pick<AuthUser, "name">>) => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function defaultNameFromEmail(email: string): string {
  const local = (email.split("@")[0] || "Inventor").replace(/[._-]+/g, " ");
  if (!local.trim()) return "Inventor";
  return local
    .split(" ")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function readUser(): AuthUser | null {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEYS.USER);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as { name?: unknown; email?: unknown };
    if (!parsed || typeof parsed.email !== "string") return null;
    return {
      name: typeof parsed.name === "string" ? parsed.name : "",
      email: parsed.email,
    };
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isHydrated, setIsHydrated] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    let authed = false;
    try {
      authed = window.localStorage.getItem(STORAGE_KEYS.AUTH) === "true";
    } catch {
      // ignore storage errors
    }
    const storedUser = readUser();
    // eslint-disable-next-line react-hooks/set-state-in-effect -- hydration: read persistence only after client mount
    setIsAuthenticated(authed);
    setUser(authed && storedUser ? storedUser : null);
    setIsHydrated(true);
  }, []);

  const login = useCallback((email: string, displayName?: string) => {
    const nextUser: AuthUser = {
      name: (displayName && displayName.trim()) || defaultNameFromEmail(email),
      email: email.trim(),
    };
    try {
      window.localStorage.setItem(STORAGE_KEYS.AUTH, "true");
      window.localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(nextUser));
    } catch {
      // ignore storage errors
    }
    setUser(nextUser);
    setIsAuthenticated(true);
  }, []);

  const logout = useCallback(() => {
    try {
      window.localStorage.removeItem(STORAGE_KEYS.AUTH);
      window.localStorage.removeItem(STORAGE_KEYS.USER);
    } catch {
      // ignore storage errors
    }
    setUser(null);
    setIsAuthenticated(false);
  }, []);

  const updateUser = useCallback(
    (patch: Partial<Pick<AuthUser, "name">>) => {
      setUser((prev) => {
        if (!prev) return prev;
        const next: AuthUser = { ...prev, ...patch };
        try {
          window.localStorage.setItem(
            STORAGE_KEYS.USER,
            JSON.stringify(next)
          );
        } catch {
          // ignore storage errors
        }
        return next;
      });
    },
    []
  );

  return (
    <AuthContext.Provider
      value={{ user, isAuthenticated, isHydrated, login, logout, updateUser }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
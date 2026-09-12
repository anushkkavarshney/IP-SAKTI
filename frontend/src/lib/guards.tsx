"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "./auth";

export function AuthLoadingScreen({ label }: { label?: string }) {
  return (
    <div
      className="flex min-h-[60vh] flex-col items-center justify-center gap-3"
      role="status"
      aria-label={label || "Loading"}
    >
      <span className="h-8 w-8 animate-spin rounded-full border-2 border-stone-300 border-t-amber-600 dark:border-stone-700 dark:border-t-amber-500" />
      <span className="text-xs text-stone-500 dark:text-stone-400">
        {label || "Loading…"}
      </span>
    </div>
  );
}

export function RequireAuth({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isHydrated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isHydrated && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isHydrated, isAuthenticated, router]);

  if (!isHydrated || !isAuthenticated) {
    return <AuthLoadingScreen label="Checking session…" />;
  }

  return <>{children}</>;
}

export function RedirectIfAuthed({
  to = "/home",
  children,
}: {
  to?: string;
  children: React.ReactNode;
}) {
  const { isAuthenticated, isHydrated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isHydrated && isAuthenticated) {
      router.replace(to);
    }
  }, [isHydrated, isAuthenticated, router, to]);

  if (isHydrated && isAuthenticated) {
    return <AuthLoadingScreen label="Redirecting…" />;
  }

  return <>{children}</>;
}
"use client";

import React from "react";
import { AuthProvider } from "./auth";
import { ThemeProvider } from "./theme";

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider>
      <AuthProvider>{children}</AuthProvider>
    </ThemeProvider>
  );
}
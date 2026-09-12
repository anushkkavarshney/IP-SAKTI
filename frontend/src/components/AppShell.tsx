"use client";

import { useState } from "react";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
import DisclaimerModal from "./DisclaimerModal";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [disclaimerOpen, setDisclaimerOpen] = useState(false);

  return (
    <div className="min-h-screen bg-stone-50 text-stone-900 dark:bg-stone-950 dark:text-stone-100">
      <Navbar
        onToggleSidebar={() => setSidebarOpen(true)}
        onOpenDisclaimer={() => setDisclaimerOpen(true)}
      />
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onOpenDisclaimer={() => setDisclaimerOpen(true)}
      />
      <main className="px-4 py-8 sm:px-6 lg:ml-72 lg:px-8">
        <div className="mx-auto max-w-5xl">{children}</div>
      </main>
      <DisclaimerModal
        isOpen={disclaimerOpen}
        onClose={() => setDisclaimerOpen(false)}
      />
    </div>
  );
}
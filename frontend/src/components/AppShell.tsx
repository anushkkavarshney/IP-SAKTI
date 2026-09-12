"use client";

import { useEffect, useState } from "react";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
import DisclaimerModal from "./DisclaimerModal";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [disclaimerOpen, setDisclaimerOpen] = useState(false);

  // Default the sidebar to open on desktop (matchMedia is client-side only).
  useEffect(() => {
    if (typeof window === "undefined") return;
    const mq = window.matchMedia("(min-width: 1024px)");
    // eslint-disable-next-line react-hooks/set-state-in-effect -- reads window width, must run client-side
    setSidebarOpen(mq.matches);
    const onChange = (e: MediaQueryListEvent) => setSidebarOpen(e.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);

  return (
    <div className="min-h-screen bg-stone-50 text-stone-900 dark:bg-stone-950 dark:text-stone-100">
      <Navbar
        isSidebarOpen={sidebarOpen}
        onToggleSidebar={() => setSidebarOpen((o) => !o)}
        onOpenDisclaimer={() => setDisclaimerOpen(true)}
      />
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onOpenDisclaimer={() => setDisclaimerOpen(true)}
      />
      <main
        className={`px-4 py-8 sm:px-6 transition-[margin] duration-300 lg:px-8 ${
          sidebarOpen ? "lg:ml-72" : ""
        }`}
      >
        <div className="mx-auto max-w-5xl">{children}</div>
      </main>
      <DisclaimerModal
        isOpen={disclaimerOpen}
        onClose={() => setDisclaimerOpen(false)}
      />
    </div>
  );
}
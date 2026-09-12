"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname, useRouter } from "next/navigation";
import { ShieldCheck, Menu, LogOut } from "lucide-react";
import { useAuth } from "../lib/auth";

interface NavbarProps {
  isSidebarOpen?: boolean;
  onToggleSidebar: () => void;
  onOpenDisclaimer: () => void;
}

const PAGE_TITLES: Record<string, string> = {
  "/home": "Home",
  "/assessment": "Assessment",
  "/reports": "My Assessments",
  "/settings": "Settings",
  "/how-it-works": "How It Works",
};

export default function Navbar({
  isSidebarOpen = true,
  onToggleSidebar,
  onOpenDisclaimer,
}: NavbarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { logout } = useAuth();

  const pageTitle = PAGE_TITLES[pathname] ?? "IP-SAKTI Navigator";

  const handleLogout = () => {
    logout();
    router.replace("/");
  };

  return (
    <header className="sticky top-0 z-30 w-full border-b border-stone-200 bg-white/95 backdrop-blur-md dark:border-stone-800 dark:bg-stone-950/95 print:hidden">
      <div
        className={`mx-auto flex h-16 max-w-7xl items-center justify-between px-4 transition-[padding] duration-300 sm:px-6 lg:px-8 ${
          isSidebarOpen ? "lg:pl-72" : ""
        }`}
      >
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleSidebar}
            className="flex h-10 w-10 items-center justify-center rounded-xl border border-stone-200 text-stone-600 transition hover:bg-stone-100 hover:text-stone-900 dark:border-stone-700 dark:text-stone-300 dark:hover:bg-stone-800"
            aria-label="Toggle sidebar navigation"
          >
            <Menu className="h-5 w-5" />
          </button>

          <div className="flex items-center gap-2.5">
            <Link
              href="/home"
              className="relative hidden h-9 w-9 items-center justify-center overflow-hidden rounded-xl bg-gradient-to-tr from-amber-600 to-emerald-700 shadow-xs sm:flex"
              aria-label="Go to home"
            >
              <Image src="/favicon.jpeg" alt="" fill sizes="36px" className="object-cover" />
            </Link>
            <div>
              <h1 className="text-base font-bold tracking-tight text-stone-900 dark:text-white">
                {pageTitle}
              </h1>
              <p className="hidden text-[11px] text-stone-500 dark:text-stone-400 md:block">
                Ayurvedic IP, ABS &amp; Regulatory Commercialization Roadmap
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={onOpenDisclaimer}
            className="flex items-center gap-1 rounded-xl border border-stone-200 bg-white px-3 py-1.5 text-xs font-medium text-stone-700 transition hover:bg-stone-50 hover:text-stone-900 dark:border-stone-700 dark:bg-stone-800 dark:text-stone-300 dark:hover:bg-stone-700"
            title="Legal Safety Notice"
          >
            <ShieldCheck className="h-3.5 w-3.5 text-amber-600" />
            <span className="hidden sm:inline">Safety Rules</span>
          </button>

          <button
            onClick={handleLogout}
            className="inline-flex items-center gap-1.5 rounded-xl border border-stone-200 bg-white px-3 py-1.5 text-xs font-semibold text-stone-700 transition hover:bg-rose-50 hover:text-rose-700 hover:border-rose-200 dark:border-stone-700 dark:bg-stone-800 dark:text-stone-300 dark:hover:bg-rose-950/40 dark:hover:text-rose-300"
            title="Log out"
          >
            <LogOut className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Log out</span>
          </button>
        </div>
      </div>
    </header>
  );
}
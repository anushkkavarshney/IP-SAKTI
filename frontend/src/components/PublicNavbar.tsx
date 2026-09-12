"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Scale, Menu, X, LogIn, Sparkles } from "lucide-react";
import { useAuth } from "../lib/auth";

const NAV_LINKS = [
  { href: "/how-it-works", label: "How It Works" },
  { href: "/#about", label: "About" },
];

export default function PublicNavbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const pathname = usePathname();
  const { isAuthenticated, isHydrated } = useAuth();

  const isActive = (href: string) =>
    href === "/#about"
      ? pathname === "/"
      : href.split("?")[0] === pathname;

  return (
    <header className="sticky top-0 z-30 w-full border-b border-stone-200 bg-white/95 backdrop-blur-md dark:border-stone-800 dark:bg-stone-950/95 print:hidden">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-4">
          <Link
            href="/"
            className="flex items-center gap-2.5 rounded-lg focus:outline-hidden focus-visible:ring-2 focus-visible:ring-amber-500"
            aria-label="IP-SAKTI Navigator home"
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-amber-600 to-emerald-700 text-white shadow-xs">
              <Scale className="h-5 w-5" />
            </div>
            <div className="hidden sm:block">
              <span className="block text-sm font-bold tracking-tight text-stone-900 dark:text-white">
                IP-SAKTI <span className="text-amber-600 dark:text-amber-500">Navigator</span>
              </span>
              <span className="block text-[11px] text-stone-500 dark:text-stone-400">
                Ayurvedic IP, ABS &amp; Regulatory Roadmaps
              </span>
            </div>
          </Link>

          <nav className="hidden items-center gap-1 md:flex">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.label}
                href={link.href}
                className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
                  isActive(link.href)
                    ? "text-stone-900 dark:text-white"
                    : "text-stone-600 hover:bg-stone-100 hover:text-stone-900 dark:text-stone-400 dark:hover:bg-stone-800 dark:hover:text-stone-200"
                }`}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>

        <div className="flex items-center gap-2">
          {isAuthenticated && isHydrated ? (
            <Link
              href="/home"
              className="inline-flex items-center gap-2 rounded-xl bg-stone-900 px-4 py-2 text-xs font-semibold text-white transition hover:bg-stone-800 dark:bg-stone-100 dark:text-stone-900 dark:hover:bg-stone-200"
            >
              <Sparkles className="h-3.5 w-3.5" />
              <span>Open App</span>
            </Link>
          ) : (
            <Link
              href="/login"
              className="inline-flex items-center gap-2 rounded-xl bg-stone-900 px-4 py-2 text-xs font-semibold text-white transition hover:bg-stone-800 dark:bg-stone-100 dark:text-stone-900 dark:hover:bg-stone-200"
            >
              <LogIn className="h-3.5 w-3.5" />
              <span>Log in</span>
            </Link>
          )}

          <button
            type="button"
            onClick={() => setMenuOpen((o) => !o)}
            aria-expanded={menuOpen}
            aria-label="Toggle navigation menu"
            className="flex h-10 w-10 items-center justify-center rounded-xl border border-stone-200 text-stone-600 transition hover:bg-stone-100 dark:border-stone-700 dark:text-stone-300 dark:hover:bg-stone-800 md:hidden"
          >
            {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {menuOpen && (
        <nav className="border-t border-stone-200 bg-white px-4 py-3 dark:border-stone-800 dark:bg-stone-950 md:hidden">
          <div className="flex flex-col gap-1">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.label}
                href={link.href}
                onClick={() => setMenuOpen(false)}
                className="rounded-lg px-3 py-2 text-sm font-medium text-stone-700 hover:bg-stone-100 dark:text-stone-300 dark:hover:bg-stone-800"
              >
                {link.label}
              </Link>
            ))}
          </div>
        </nav>
      )}
    </header>
  );
}
"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import {
  ArrowRight,
  ArrowLeft,
  Mail,
  Lock,
  Eye,
  EyeOff,
  AlertCircle,
  Info,
} from "lucide-react";
import { useAuth } from "@/lib/auth";
import { RedirectIfAuthed } from "@/lib/guards";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedEmail = email.trim();
    const trimmedPassword = password.trim();

    if (!trimmedEmail) {
      setError("Enter an email address to continue.");
      return;
    }
    if (!trimmedPassword) {
      setError("Enter a password to continue.");
      return;
    }

    setError(null);
    // Demo-only authentication: any non-empty credentials succeed.
    login(trimmedEmail);
    router.replace("/home");
  };

  return (
    <RedirectIfAuthed to="/home">
      <div className="mx-auto flex max-w-md flex-col px-4 py-14 sm:px-6">
        <div className="rounded-3xl border border-stone-200 bg-white p-8 shadow-sm dark:border-stone-800 dark:bg-stone-900">
          <div className="flex flex-col items-center text-center">
            <div className="relative flex h-12 w-12 items-center justify-center overflow-hidden rounded-2xl bg-gradient-to-tr from-amber-600 to-emerald-700 shadow-md">
              <Image src="/favicon.jpeg" alt="" fill sizes="48px" className="object-cover" />
            </div>
            <h1 className="mt-4 text-xl font-bold tracking-tight text-stone-900 dark:text-white">
              Welcome to IP-SAKTI Navigator
            </h1>
            <p className="mt-1.5 text-sm leading-relaxed text-stone-500 dark:text-stone-400">
              Log in to turn your Ayurvedic innovation into an evidence-backed
              IP and regulatory roadmap.
            </p>
          </div>

          <div className="mt-6 inline-flex items-center gap-1.5 rounded-full border border-stone-200 bg-stone-50 px-2.5 py-1 text-[11px] text-stone-500 dark:border-stone-700 dark:bg-stone-800 dark:text-stone-400">
            <Info className="h-3 w-3 text-amber-600" />
            Demo login — any email and password will work.
          </div>

          <form onSubmit={handleSubmit} className="mt-5 space-y-4">
            <div>
              <label
                htmlFor="login-email"
                className="mb-1.5 block text-xs font-semibold text-stone-700 dark:text-stone-300"
              >
                Email address
              </label>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400" />
                <input
                  id="login-email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full rounded-xl border border-stone-300 bg-stone-50/50 py-2.5 pl-10 pr-3 text-sm text-stone-900 placeholder:text-stone-400 focus:border-amber-500 focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20 dark:border-stone-700 dark:bg-stone-800/50 dark:text-stone-100 dark:placeholder:text-stone-500 dark:focus:bg-stone-900"
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="login-password"
                className="mb-1.5 block text-xs font-semibold text-stone-700 dark:text-stone-300"
              >
                Password
              </label>
              <div className="relative">
                <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400" />
                <input
                  id="login-password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter a password"
                  className="w-full rounded-xl border border-stone-300 bg-stone-50/50 py-2.5 pl-10 pr-10 text-sm text-stone-900 placeholder:text-stone-400 focus:border-amber-500 focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20 dark:border-stone-700 dark:bg-stone-800/50 dark:text-stone-100 dark:placeholder:text-stone-500 dark:focus:bg-stone-900"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((s) => !s)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  className="absolute right-2 top-1/2 -translate-y-1/2 rounded-lg p-1.5 text-stone-400 transition hover:text-stone-600 dark:hover:text-stone-300"
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            {error && (
              <div
                role="alert"
                className="flex items-center gap-2 rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800 dark:border-rose-900/50 dark:bg-rose-950/40 dark:text-rose-200"
              >
                <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
                <span>{error}</span>
              </div>
            )}

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 text-xs text-stone-600 dark:text-stone-400">
                <input
                  type="checkbox"
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                  className="h-3.5 w-3.5 rounded border-stone-300 text-amber-600 focus:ring-amber-500"
                />
                Remember me
              </label>
              <span className="cursor-not-allowed text-xs text-stone-400 dark:text-stone-500">
                Forgot password?
              </span>
            </div>

            <button
              type="submit"
              className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-600 to-emerald-700 px-6 py-3 text-sm font-semibold text-white shadow-md transition hover:from-amber-700 hover:to-emerald-800 focus:outline-hidden focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-2"
            >
              <span>Log in</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </form>
        </div>

        <div className="mt-6 text-center">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-xs font-medium text-stone-500 transition hover:text-stone-800 dark:text-stone-400 dark:hover:text-stone-200"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Back to landing page
          </Link>
        </div>
      </div>
    </RedirectIfAuthed>
  );
}
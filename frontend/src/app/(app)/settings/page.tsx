"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  UserRound,
  Palette,
  Bell,
  LogOut,
  Trash2,
  Save,
  CheckCircle2,
  Moon,
  Sun,
  Monitor,
  CircleUser,
} from "lucide-react";
import { useAuth } from "../../../lib/auth";
import { useTheme } from "../../../lib/theme";
import {
  readProfile,
  saveProfile,
  STORAGE_KEYS,
} from "../../../lib/storage";
import { ProfileSettings } from "../../../types/assessment";

const THEME_OPTIONS: {
  value: "light" | "dark" | "system";
  label: string;
  icon: typeof Sun;
  description: string;
}[] = [
  { value: "light", label: "Light", icon: Sun, description: "Always light" },
  { value: "dark", label: "Dark", icon: Moon, description: "Always dark" },
  {
    value: "system",
    label: "System",
    icon: Monitor,
    description: "Follow device",
  },
];

export default function SettingsPage() {
  const router = useRouter();
  const { user, updateUser, logout } = useAuth();
  const { theme, setTheme, resolvedDark } = useTheme();

  const [displayName, setDisplayName] = useState(user?.name ?? "");
  const [role, setRole] = useState<string | undefined>(undefined);
  const [prefersNotifications, setPrefersNotifications] = useState(true);
  const [savedFlash, setSavedFlash] = useState(false);

  useEffect(() => {
    const profile = readProfile();
    // eslint-disable-next-line react-hooks/set-state-in-effect -- load persisted profile after mount
    setRole(profile.role);
    setPrefersNotifications(profile.prefersNotifications);
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- sync form field with auth user
    if (user?.name) setDisplayName(user.name);
  }, [user?.name]);

  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault();
    const nextName = displayName.trim() || user?.name || "Demo User";
    updateUser({ name: nextName });
    const nextProfile: ProfileSettings = {
      displayName: nextName,
      role: role?.trim() ? role.trim() : undefined,
      prefersNotifications,
    };
    saveProfile(nextProfile);
    setSavedFlash(true);
    window.setTimeout(() => setSavedFlash(false), 2000);
  };

  const handleResetData = () => {
    try {
      window.localStorage.removeItem(STORAGE_KEYS.REPORTS);
    } catch {
      // ignore storage errors
    }
    router.replace("/home");
  };

  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-2xl font-extrabold tracking-tight text-stone-900 dark:text-white">
          Settings
        </h1>
        <p className="mt-1 text-sm text-stone-500 dark:text-stone-400">
          Profile, appearance, and app preferences.
        </p>
      </section>

      <form
        onSubmit={handleSaveProfile}
        className="rounded-3xl border border-stone-200 bg-white p-6 dark:border-stone-800 dark:bg-stone-900"
      >
        <div className="flex items-center gap-3 border-b border-stone-100 pb-4 dark:border-stone-800">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">
            <UserRound className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-stone-900 dark:text-stone-100">
              Profile
            </h2>
            <p className="text-xs text-stone-500 dark:text-stone-400">
              How you appear across the app
            </p>
          </div>
        </div>

        <div className="mt-5 grid gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="settings-name" className="mb-1.5 block text-xs font-semibold text-stone-700 dark:text-stone-300">
              Display name
            </label>
            <input
              id="settings-name"
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="Your name"
              className="w-full rounded-xl border border-stone-300 bg-stone-50/50 px-3 py-2.5 text-sm text-stone-900 placeholder:text-stone-400 focus:border-amber-500 focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20 dark:border-stone-700 dark:bg-stone-800/50 dark:text-stone-100 dark:placeholder:text-stone-500 dark:focus:bg-stone-900"
            />
          </div>
          <div>
            <label htmlFor="settings-email" className="mb-1.5 block text-xs font-semibold text-stone-700 dark:text-stone-300">
              Email (read-only)
            </label>
            <div className="relative">
              <input
                id="settings-email"
                type="email"
                value={user?.email ?? ""}
                readOnly
                className="w-full cursor-not-allowed rounded-xl border border-stone-200 bg-stone-100 px-3 py-2.5 pr-9 text-sm text-stone-500 dark:border-stone-700 dark:bg-stone-800/60 dark:text-stone-400"
              />
              <CircleUser className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400" />
            </div>
          </div>
          <div className="sm:col-span-2">
            <label htmlFor="settings-role" className="mb-1.5 block text-xs font-semibold text-stone-700 dark:text-stone-300">
              Role (optional)
            </label>
            <select
              id="settings-role"
              value={role ?? ""}
              onChange={(e) => setRole(e.target.value || undefined)}
              className="w-full rounded-xl border border-stone-300 bg-stone-50/50 px-3 py-2.5 text-sm text-stone-900 focus:border-amber-500 focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20 dark:border-stone-700 dark:bg-stone-800/50 dark:text-stone-100 dark:focus:bg-stone-900"
            >
              <option value="">Select a role…</option>
              <option value="Founder / Innovator">Founder / Innovator</option>
              <option value="R&D Scientist">R&D Scientist</option>
              <option value="IP Attorney">IP Attorney</option>
              <option value="Regulatory Consultant">Regulatory Consultant</option>
              <option value="Student / Researcher">Student / Researcher</option>
            </select>
          </div>
        </div>

        <div className="mt-5 flex items-center justify-between border-t border-stone-100 pt-4 dark:border-stone-800">
          <span className="text-xs text-stone-500 dark:text-stone-400">
            {savedFlash ? "Saved to this browser." : "Changes are stored locally."}
          </span>
          <button
            type="submit"
            className="inline-flex items-center gap-2 rounded-xl bg-stone-900 px-5 py-2.5 text-xs font-semibold text-white transition hover:bg-stone-800 dark:bg-stone-100 dark:text-stone-900 dark:hover:bg-stone-200"
          >
            {savedFlash ? (
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 dark:text-emerald-600" />
            ) : (
              <Save className="h-3.5 w-3.5" />
            )}
            <span>Save profile</span>
          </button>
        </div>
      </form>

      <section className="rounded-3xl border border-stone-200 bg-white p-6 dark:border-stone-800 dark:bg-stone-900">
        <div className="flex items-center gap-3 border-b border-stone-100 pb-4 dark:border-stone-800">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">
            <Palette className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-stone-900 dark:text-stone-100">
              Appearance
            </h2>
            <p className="text-xs text-stone-500 dark:text-stone-400">
              Choose a theme. Stored on this device.
            </p>
          </div>
        </div>

        <div className="mt-5 grid gap-3 sm:grid-cols-3">
          {THEME_OPTIONS.map((option) => {
            const Icon = option.icon;
            const selected = theme === option.value;
            return (
              <button
                key={option.value}
                type="button"
                onClick={() => setTheme(option.value)}
                aria-pressed={selected}
                className={`flex flex-col items-start gap-3 rounded-2xl border p-4 text-left transition ${
                  selected
                    ? "border-amber-400 bg-amber-50 ring-2 ring-amber-500/20 dark:border-amber-600 dark:bg-amber-950/40"
                    : "border-stone-200 bg-stone-50/60 hover:border-stone-300 dark:border-stone-700 dark:bg-stone-800/40 dark:hover:border-stone-600"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span
                    className={`flex h-8 w-8 items-center justify-center rounded-lg ${
                      selected
                        ? "bg-amber-600 text-white"
                        : "bg-white text-stone-500 shadow-xs dark:bg-stone-700 dark:text-stone-300"
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                  </span>
                  <span className="text-xs font-bold text-stone-800 dark:text-stone-200">
                    {option.label}
                  </span>
                </div>
                <span className="text-[11px] text-stone-500 dark:text-stone-400">
                  {option.description}
                </span>
              </button>
            );
          })}
        </div>
        <p className="mt-4 text-[11px] text-stone-400 dark:text-stone-500">
          {resolvedDark
            ? "Dark mode is active right now."
            : "Light mode is active right now."}
        </p>
      </section>

      <section className="rounded-3xl border border-stone-200 bg-white p-6 dark:border-stone-800 dark:bg-stone-900">
        <div className="flex items-center gap-3 border-b border-stone-100 pb-4 dark:border-stone-800">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">
            <Bell className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-stone-900 dark:text-stone-100">
              Notifications
            </h2>
            <p className="text-xs text-stone-500 dark:text-stone-400">
              This demo is offline-only; toggles are stored locally.
            </p>
          </div>
        </div>

        <div className="mt-4 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-stone-700 dark:text-stone-300">
              Assessment reminders
            </p>
            <p className="text-[11px] text-stone-500 dark:text-stone-400">
              Prefer to be nudged about in-progress assessments (visual only).
            </p>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={prefersNotifications}
            onClick={() => setPrefersNotifications((v) => !v)}
            className={`relative h-6 w-11 shrink-0 rounded-full transition ${
              prefersNotifications ? "bg-amber-600" : "bg-stone-300 dark:bg-stone-700"
            }`}
          >
            <span
              className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow-xs transition-all ${
                prefersNotifications ? "left-[22px]" : "left-0.5"
              }`}
            />
          </button>
        </div>
      </section>

      <section className="rounded-3xl border border-rose-200 bg-rose-50/50 p-6 dark:border-rose-900/60 dark:bg-rose-950/20">
        <h2 className="text-sm font-bold text-rose-900 dark:text-rose-300">
          Session & data
        </h2>
        <p className="mt-1 text-xs text-rose-800/80 dark:text-rose-300/70">
          These actions affect only this browser. Nothing is stored on a server.
        </p>
        <div className="mt-4 flex flex-col gap-3 sm:flex-row">
          <button
            type="button"
            onClick={() => {
              logout();
              router.replace("/");
            }}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-stone-300 bg-white px-4 py-2.5 text-xs font-semibold text-stone-700 transition hover:bg-stone-100 dark:border-stone-600 dark:bg-stone-800 dark:text-stone-300 dark:hover:bg-stone-700"
          >
            <LogOut className="h-3.5 w-3.5" />
            <span>Log out</span>
          </button>
          <button
            type="button"
            onClick={handleResetData}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-rose-300 bg-rose-100/70 px-4 py-2.5 text-xs font-semibold text-rose-800 transition hover:bg-rose-200/70 dark:border-rose-800 dark:bg-rose-950/50 dark:text-rose-300 dark:hover:bg-rose-950"
          >
            <Trash2 className="h-3.5 w-3.5" />
            <span>Clear assessment history</span>
          </button>
        </div>
      </section>
    </div>
  );
}
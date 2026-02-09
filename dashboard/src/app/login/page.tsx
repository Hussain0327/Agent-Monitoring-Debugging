"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { login, register } from "@/lib/auth";
import { Activity, ArrowRight } from "lucide-react";

type Mode = "login" | "register";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (mode === "register") {
        await register(email, password);
      } else {
        await login(email, password);
      }
      router.push("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : `${mode === "register" ? "Registration" : "Login"} failed`);
    } finally {
      setLoading(false);
    }
  }

  const isRegister = mode === "register";

  return (
    <div className="w-full max-w-sm space-y-8">
      {/* Logo */}
      <div className="flex flex-col items-center gap-4">
        <div className="relative flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--accent-dim)] glow-accent">
          <Activity size={28} className="text-[var(--accent)]" />
          <div className="absolute -right-1 -top-1 h-3 w-3 rounded-full bg-[var(--accent)] animate-pulse-dot" />
        </div>
        <div className="text-center">
          <h1 className="text-2xl font-semibold tracking-tight">Vigil</h1>
          <p className="mt-1 text-sm text-[var(--muted-foreground)]">AI Agent Observability</p>
        </div>
      </div>

      {/* Form */}
      <form
        onSubmit={handleSubmit}
        className="space-y-5 rounded-2xl border border-[var(--border)] bg-[var(--background-raised)] p-6"
      >
        <div>
          <h2 className="text-base font-semibold">{isRegister ? "Create account" : "Sign in"}</h2>
          <p className="mt-0.5 text-sm text-[var(--muted-foreground)]">
            {isRegister ? "Set up your first account to get started" : "Enter your credentials to continue"}
          </p>
        </div>

        {error && (
          <div className="rounded-lg border border-[var(--danger)]/20 bg-[var(--danger-dim)] px-4 py-3 text-sm text-[var(--danger)]">
            {error}
          </div>
        )}

        <div className="space-y-1.5">
          <label htmlFor="email" className="block font-mono text-[11px] font-medium uppercase tracking-wider text-[var(--muted-foreground)]">
            Email
          </label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-4 py-2.5 text-sm transition-colors placeholder:text-[var(--muted-foreground)]/50 focus:border-[var(--accent)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]"
          />
        </div>

        <div className="space-y-1.5">
          <label htmlFor="password" className="block font-mono text-[11px] font-medium uppercase tracking-wider text-[var(--muted-foreground)]">
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            minLength={4}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-4 py-2.5 text-sm transition-colors placeholder:text-[var(--muted-foreground)]/50 focus:border-[var(--accent)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="group flex w-full items-center justify-center gap-2 rounded-lg bg-[var(--accent)] px-4 py-2.5 text-sm font-semibold text-[var(--background)] transition-all hover:brightness-110 disabled:opacity-50"
        >
          {loading ? (
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
          ) : (
            <>
              {isRegister ? "Create account" : "Sign in"}
              <ArrowRight size={14} className="transition-transform group-hover:translate-x-0.5" />
            </>
          )}
        </button>

        <div className="text-center text-sm text-[var(--muted-foreground)]">
          {isRegister ? (
            <>
              Already have an account?{" "}
              <button type="button" onClick={() => { setMode("login"); setError(""); }} className="text-[var(--accent-text)] hover:text-[var(--accent)]">
                Sign in
              </button>
            </>
          ) : (
            <>
              No account yet?{" "}
              <button type="button" onClick={() => { setMode("register"); setError(""); }} className="text-[var(--accent-text)] hover:text-[var(--accent)]">
                Create one
              </button>
            </>
          )}
        </div>
      </form>
    </div>
  );
}

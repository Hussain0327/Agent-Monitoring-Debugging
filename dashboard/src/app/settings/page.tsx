"use client";

import { useState } from "react";
import { logout } from "@/lib/auth";

export default function SettingsPage() {
  const [copied, setCopied] = useState(false);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  function copyApiUrl() {
    navigator.clipboard.writeText(apiUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Settings</h1>
        <p className="text-[var(--muted-foreground)]">Manage your account and configuration</p>
      </div>

      <div className="space-y-4 rounded-lg border border-[var(--border)] p-6">
        <h2 className="text-lg font-medium">API Configuration</h2>

        <div>
          <label className="mb-1 block text-sm font-medium text-[var(--muted-foreground)]">
            API URL
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              readOnly
              value={apiUrl}
              className="flex-1 rounded-md border border-[var(--border)] bg-[var(--muted)] px-3 py-2 text-sm"
            />
            <button
              onClick={copyApiUrl}
              className="rounded-md border border-[var(--border)] px-4 py-2 text-sm hover:bg-[var(--muted)]"
            >
              {copied ? "Copied" : "Copy"}
            </button>
          </div>
        </div>
      </div>

      <div className="space-y-4 rounded-lg border border-[var(--border)] p-6">
        <h2 className="text-lg font-medium">Account</h2>
        <button
          onClick={logout}
          className="rounded-md border border-red-300 px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:border-red-800 dark:text-red-400 dark:hover:bg-red-900/20"
        >
          Sign out
        </button>
      </div>
    </div>
  );
}

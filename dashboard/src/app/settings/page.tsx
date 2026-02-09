"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { logout } from "@/lib/auth";
import { Settings, Key, Shield, Copy, Check, LogOut, Loader2, AlertTriangle } from "lucide-react";

const PROJECT_ID = "default";

export default function SettingsPage() {
  const [copied, setCopied] = useState(false);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const queryClient = useQueryClient();

  const { data: settings } = useQuery({
    queryKey: ["project-settings", PROJECT_ID],
    queryFn: () => api.projects.getSettings(PROJECT_ID),
  });

  const [openaiKey, setOpenaiKey] = useState("");
  const [anthropicKey, setAnthropicKey] = useState("");
  const [openaiModel, setOpenaiModel] = useState("");
  const [anthropicModel, setAnthropicModel] = useState("");
  const [driftEnabled, setDriftEnabled] = useState(false);
  const [driftInterval, setDriftInterval] = useState(60);
  const [saveMsg, setSaveMsg] = useState("");

  useEffect(() => {
    if (settings) {
      setOpenaiModel(settings.default_openai_model);
      setAnthropicModel(settings.default_anthropic_model);
      setDriftEnabled(settings.drift_check_enabled);
      setDriftInterval(settings.drift_check_interval_minutes);
    }
  }, [settings]);

  const updateSettings = useMutation({
    mutationFn: (data: Parameters<typeof api.projects.updateSettings>[1]) =>
      api.projects.updateSettings(PROJECT_ID, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["project-settings", PROJECT_ID] });
      setSaveMsg("Settings saved");
      setTimeout(() => setSaveMsg(""), 3000);
    },
  });

  function handleSave() {
    const data: Record<string, unknown> = {
      default_openai_model: openaiModel,
      default_anthropic_model: anthropicModel,
      drift_check_enabled: driftEnabled,
      drift_check_interval_minutes: driftInterval,
    };
    if (openaiKey) data.openai_api_key = openaiKey;
    if (anthropicKey) data.anthropic_api_key = anthropicKey;
    updateSettings.mutate(data as Parameters<typeof api.projects.updateSettings>[1]);
    setOpenaiKey("");
    setAnthropicKey("");
  }

  function copyApiUrl() {
    navigator.clipboard.writeText(apiUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="animate-fade-up flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--accent-dim)]">
          <Settings size={20} className="text-[var(--accent)]" />
        </div>
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
          <p className="text-sm text-[var(--muted-foreground)]">
            Manage your account and project configuration
          </p>
        </div>
      </div>

      {/* API Configuration */}
      <div className="animate-fade-up space-y-4 rounded-xl border border-[var(--border)] bg-[var(--background-raised)] p-6" style={{ animationDelay: "0.05s" }}>
        <h2 className="flex items-center gap-2 text-sm font-semibold">
          <Settings size={14} className="text-[var(--accent)]" />
          API Configuration
        </h2>

        <div>
          <label className="mb-1.5 block font-mono text-[10px] uppercase tracking-wider text-[var(--muted-foreground)]">
            API URL
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              readOnly
              value={apiUrl}
              className="flex-1 rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 font-mono text-sm text-[var(--foreground)]"
            />
            <button
              onClick={copyApiUrl}
              className="flex items-center gap-1.5 rounded-lg border border-[var(--border)] px-3 py-2 text-sm text-[var(--muted-foreground)] transition-colors hover:bg-[var(--background-elevated)] hover:text-[var(--foreground)]"
            >
              {copied ? <Check size={14} className="text-[var(--success)]" /> : <Copy size={14} />}
              {copied ? "Copied" : "Copy"}
            </button>
          </div>
        </div>
      </div>

      {/* LLM API Keys */}
      <div className="animate-fade-up space-y-4 rounded-xl border border-[var(--border)] bg-[var(--background-raised)] p-6" style={{ animationDelay: "0.1s" }}>
        <h2 className="flex items-center gap-2 text-sm font-semibold">
          <Key size={14} className="text-[var(--accent)]" />
          LLM API Keys
        </h2>
        <p className="font-mono text-[11px] text-[var(--muted-foreground)]">
          Keys are encrypted at rest and never returned in plaintext.
        </p>

        <div>
          <label className="mb-1.5 block font-mono text-[10px] uppercase tracking-wider text-[var(--muted-foreground)]">
            OpenAI API Key
          </label>
          <input
            type="password"
            value={openaiKey}
            onChange={(e) => setOpenaiKey(e.target.value)}
            placeholder={settings?.openai_api_key_set ? `Current: ${settings.openai_api_key_masked}` : "sk-..."}
            className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 font-mono text-sm transition-colors focus:border-[var(--accent)] focus:outline-none"
          />
        </div>

        <div>
          <label className="mb-1.5 block font-mono text-[10px] uppercase tracking-wider text-[var(--muted-foreground)]">
            Anthropic API Key
          </label>
          <input
            type="password"
            value={anthropicKey}
            onChange={(e) => setAnthropicKey(e.target.value)}
            placeholder={settings?.anthropic_api_key_set ? `Current: ${settings.anthropic_api_key_masked}` : "sk-ant-..."}
            className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 font-mono text-sm transition-colors focus:border-[var(--accent)] focus:outline-none"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1.5 block font-mono text-[10px] uppercase tracking-wider text-[var(--muted-foreground)]">
              Default OpenAI Model
            </label>
            <input
              type="text"
              value={openaiModel}
              onChange={(e) => setOpenaiModel(e.target.value)}
              className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 font-mono text-sm transition-colors focus:border-[var(--accent)] focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-1.5 block font-mono text-[10px] uppercase tracking-wider text-[var(--muted-foreground)]">
              Default Anthropic Model
            </label>
            <input
              type="text"
              value={anthropicModel}
              onChange={(e) => setAnthropicModel(e.target.value)}
              className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 font-mono text-sm transition-colors focus:border-[var(--accent)] focus:outline-none"
            />
          </div>
        </div>
      </div>

      {/* Drift Detection */}
      <div className="animate-fade-up space-y-4 rounded-xl border border-[var(--border)] bg-[var(--background-raised)] p-6" style={{ animationDelay: "0.15s" }}>
        <h2 className="flex items-center gap-2 text-sm font-semibold">
          <Shield size={14} className="text-[var(--accent)]" />
          Drift Detection
        </h2>

        <label className="flex items-center gap-2.5 cursor-pointer">
          <input
            type="checkbox"
            checked={driftEnabled}
            onChange={(e) => setDriftEnabled(e.target.checked)}
            className="rounded border-[var(--border)] accent-[var(--accent)]"
          />
          <span className="text-sm">Enable automatic drift detection</span>
        </label>

        {driftEnabled && (
          <div>
            <label className="mb-1.5 block font-mono text-[10px] uppercase tracking-wider text-[var(--muted-foreground)]">
              Check Interval
            </label>
            <select
              value={driftInterval}
              onChange={(e) => setDriftInterval(Number(e.target.value))}
              className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-sm transition-colors focus:border-[var(--accent)] focus:outline-none"
            >
              <option value={5}>Every 5 minutes</option>
              <option value={15}>Every 15 minutes</option>
              <option value={30}>Every 30 minutes</option>
              <option value={60}>Every hour</option>
              <option value={360}>Every 6 hours</option>
              <option value={1440}>Daily</option>
            </select>
          </div>
        )}
      </div>

      {/* Save */}
      <div className="animate-fade-up flex items-center gap-3" style={{ animationDelay: "0.2s" }}>
        <button
          onClick={handleSave}
          disabled={updateSettings.isPending}
          className="flex items-center gap-2 rounded-lg bg-[var(--accent)] px-4 py-2 text-sm font-medium text-[var(--background)] transition-colors hover:opacity-90 disabled:opacity-50"
        >
          {updateSettings.isPending && <Loader2 size={14} className="animate-spin" />}
          {updateSettings.isPending ? "Saving..." : "Save Settings"}
        </button>
        {saveMsg && (
          <span className="flex items-center gap-1.5 text-sm text-[var(--success)]">
            <Check size={14} />
            {saveMsg}
          </span>
        )}
        {updateSettings.isError && (
          <span className="flex items-center gap-1.5 text-sm text-[var(--danger)]">
            <AlertTriangle size={14} />
            Failed to save
          </span>
        )}
      </div>

      {/* Account */}
      <div className="animate-fade-up space-y-4 rounded-xl border border-[var(--border)] bg-[var(--background-raised)] p-6" style={{ animationDelay: "0.25s" }}>
        <h2 className="text-sm font-semibold">Account</h2>
        <button
          onClick={logout}
          className="flex items-center gap-2 rounded-lg border border-[var(--danger)]/30 px-4 py-2 text-sm text-[var(--danger)] transition-colors hover:bg-[var(--danger-dim)]"
        >
          <LogOut size={14} />
          Sign out
        </button>
      </div>
    </div>
  );
}

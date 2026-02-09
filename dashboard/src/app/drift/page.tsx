"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { DriftAlertCard } from "@/components/drift-alert-card";
import { AlertTriangle, Shield, Flame } from "lucide-react";

export default function DriftPage() {
  const [showResolved, setShowResolved] = useState(false);

  const { data: alerts, isLoading } = useQuery({
    queryKey: ["drift-alerts", showResolved],
    queryFn: () => api.drift.alerts(showResolved),
  });

  const { data: summary } = useQuery({
    queryKey: ["drift-summary"],
    queryFn: () => api.drift.summary(),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="animate-fade-up flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--warning-dim)]">
            <AlertTriangle size={20} className="text-[var(--warning)]" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">Drift Detection</h1>
            <p className="text-sm text-[var(--muted-foreground)]">
              Monitor distribution shifts in your agent outputs
            </p>
          </div>
        </div>
        <label className="flex items-center gap-2 rounded-lg border border-[var(--border)] px-3 py-1.5 text-sm transition-colors hover:bg-[var(--background-elevated)]">
          <input
            type="checkbox"
            checked={showResolved}
            onChange={(e) => setShowResolved(e.target.checked)}
            className="rounded border-[var(--border)] accent-[var(--accent)]"
          />
          <span className="text-[var(--muted-foreground)]">Show resolved</span>
        </label>
      </div>

      {/* Stats */}
      {summary && (
        <div className="animate-fade-up grid grid-cols-3 gap-4" style={{ animationDelay: "0.05s" }}>
          <div className="rounded-xl border border-[var(--border)] bg-[var(--background-raised)] p-5">
            <div className="flex items-center gap-2 text-[var(--muted-foreground)]">
              <AlertTriangle size={14} />
              <span className="font-mono text-[11px] uppercase tracking-wider">Total</span>
            </div>
            <div className="mt-2 font-mono text-2xl font-light">{summary.total_alerts}</div>
          </div>
          <div className="rounded-xl border border-[var(--border)] bg-[var(--background-raised)] p-5">
            <div className="flex items-center gap-2 text-[var(--warning)]">
              <Shield size={14} />
              <span className="font-mono text-[11px] uppercase tracking-wider">Unresolved</span>
            </div>
            <div className="mt-2 font-mono text-2xl font-light text-[var(--warning)]">{summary.unresolved}</div>
          </div>
          <div className="rounded-xl border border-[var(--border)] bg-[var(--background-raised)] p-5">
            <div className="flex items-center gap-2 text-[var(--danger)]">
              <Flame size={14} />
              <span className="font-mono text-[11px] uppercase tracking-wider">High Severity</span>
            </div>
            <div className="mt-2 font-mono text-2xl font-light text-[var(--danger)]">
              {summary.by_severity["high"] || 0}
            </div>
          </div>
        </div>
      )}

      {/* Alert List */}
      <div className="animate-fade-up space-y-3" style={{ animationDelay: "0.1s" }}>
        {isLoading && (
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-24 animate-pulse rounded-xl border border-[var(--border)] bg-[var(--background-raised)]" />
            ))}
          </div>
        )}
        {alerts?.length === 0 && (
          <div className="rounded-xl border border-dashed border-[var(--border-bright)] p-10 text-center font-mono text-sm text-[var(--muted-foreground)]">
            {showResolved ? "No drift alerts" : "No unresolved drift alerts"}
          </div>
        )}
        {alerts?.map((alert) => <DriftAlertCard key={alert.id} alert={alert} />)}
      </div>
    </div>
  );
}

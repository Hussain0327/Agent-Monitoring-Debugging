"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { DriftAlertCard } from "@/components/drift-alert-card";

export default function DriftPage() {
  const { data: alerts, isLoading } = useQuery({
    queryKey: ["drift-alerts"],
    queryFn: () => api.drift.alerts(),
  });

  const { data: summary } = useQuery({
    queryKey: ["drift-summary"],
    queryFn: () => api.drift.summary(),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Drift Detection</h1>
        <p className="text-[var(--muted-foreground)]">
          Monitor distribution shifts in your agent outputs
        </p>
      </div>

      {summary && (
        <div className="grid grid-cols-3 gap-4">
          <div className="rounded-lg border border-[var(--border)] p-4">
            <div className="text-sm text-[var(--muted-foreground)]">Total Alerts</div>
            <div className="text-2xl font-semibold">{summary.total_alerts}</div>
          </div>
          <div className="rounded-lg border border-[var(--border)] p-4">
            <div className="text-sm text-[var(--muted-foreground)]">Unresolved</div>
            <div className="text-2xl font-semibold text-amber-500">{summary.unresolved}</div>
          </div>
          <div className="rounded-lg border border-[var(--border)] p-4">
            <div className="text-sm text-[var(--muted-foreground)]">High Severity</div>
            <div className="text-2xl font-semibold text-red-500">
              {summary.by_severity["high"] || 0}
            </div>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {isLoading && <p className="text-[var(--muted-foreground)]">Loading alerts...</p>}
        {alerts?.length === 0 && (
          <p className="text-[var(--muted-foreground)]">No drift alerts detected</p>
        )}
        {alerts?.map((alert) => <DriftAlertCard key={alert.id} alert={alert} />)}
      </div>
    </div>
  );
}

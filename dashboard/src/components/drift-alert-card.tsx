"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { DriftAlert } from "@/lib/types";
import { cn } from "@/lib/utils";
import { formatDate } from "@/lib/utils";
import { AlertTriangle, CheckCircle, TrendingUp } from "lucide-react";
import { api } from "@/lib/api";

interface DriftAlertCardProps {
  alert: DriftAlert;
}

const severityConfig: Record<string, { border: string; icon: string; label: string }> = {
  low: {
    border: "border-[var(--warning)]/20",
    icon: "text-[var(--warning)]",
    label: "bg-[var(--warning-dim)] text-[var(--warning)]",
  },
  medium: {
    border: "border-orange-500/20",
    icon: "text-orange-400",
    label: "bg-orange-500/10 text-orange-400",
  },
  high: {
    border: "border-[var(--danger)]/20",
    icon: "text-[var(--danger)]",
    label: "bg-[var(--danger-dim)] text-[var(--danger)]",
  },
};

export function DriftAlertCard({ alert }: DriftAlertCardProps) {
  const queryClient = useQueryClient();
  const change = alert.current_value - alert.baseline_value;
  const changePercent = alert.baseline_value !== 0 ? (change / alert.baseline_value) * 100 : 0;
  const config = severityConfig[alert.severity] || severityConfig.low;

  const resolveMutation = useMutation({
    mutationFn: () => api.drift.resolve(alert.id),
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: ["drift-alerts"] });
      const prev = queryClient.getQueryData<DriftAlert[]>(["drift-alerts"]);
      if (prev) {
        queryClient.setQueryData(
          ["drift-alerts"],
          prev.map((a) => (a.id === alert.id ? { ...a, resolved: true } : a)),
        );
      }
      return { prev };
    },
    onError: (_err, _vars, ctx) => {
      if (ctx?.prev) queryClient.setQueryData(["drift-alerts"], ctx.prev);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["drift-alerts"] });
      queryClient.invalidateQueries({ queryKey: ["drift-summary"] });
    },
  });

  return (
    <div
      role={alert.severity === "high" ? "alert" : undefined}
      className={cn(
        "rounded-xl border bg-[var(--background-raised)] p-4 transition-colors",
        alert.resolved
          ? "border-[var(--success)]/20 opacity-60"
          : "border-[var(--border)]",
      )}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className={cn(
            "mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg",
            alert.resolved ? "bg-[var(--success-dim)]" : config.label.split(" ")[0],
          )}>
            <AlertTriangle
              size={14}
              className={alert.resolved ? "text-[var(--success)]" : config.icon}
            />
          </div>
          <div className="min-w-0">
            <div className="text-sm font-medium">
              {alert.metric_name} drift in{" "}
              <span className="font-mono text-[var(--accent-text)]">{alert.span_kind}</span>{" "}
              spans
            </div>
            <div className="mt-1 flex items-center gap-2">
              <span className="font-mono text-xs text-[var(--muted-foreground)]">
                PSI {alert.psi_score.toFixed(3)}
              </span>
              <span className="text-[var(--border-bright)]">&middot;</span>
              <span className={cn(
                "rounded-md px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wider",
                config.label,
              )}>
                {alert.severity}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <div className="text-right">
            <div className="flex items-center justify-end gap-1">
              <TrendingUp size={12} className="text-[var(--muted-foreground)]" />
              <span className={cn(
                "font-mono text-sm",
                change > 0 ? "text-[var(--danger)]" : "text-[var(--success)]",
              )}>
                {changePercent > 0 ? "+" : ""}
                {changePercent.toFixed(1)}%
              </span>
            </div>
            <div className="mt-0.5 font-mono text-[10px] text-[var(--muted-foreground)]">
              {alert.baseline_value.toFixed(2)} → {alert.current_value.toFixed(2)}
            </div>
          </div>

          {!alert.resolved && (
            <button
              onClick={() => resolveMutation.mutate()}
              disabled={resolveMutation.isPending}
              className="flex items-center gap-1.5 rounded-lg border border-[var(--success)]/30 px-2.5 py-1 text-xs text-[var(--success)] transition-colors hover:bg-[var(--success-dim)] disabled:opacity-50"
            >
              <CheckCircle size={12} />
              {resolveMutation.isPending ? "..." : "Resolve"}
            </button>
          )}
        </div>
      </div>

      <div className="mt-3 flex items-center gap-2 font-mono text-[10px] text-[var(--muted-foreground)]">
        {formatDate(alert.created_at)}
        {alert.resolved && (
          <span className="rounded-md bg-[var(--success-dim)] px-1.5 py-0.5 text-[var(--success)]">
            Resolved
          </span>
        )}
      </div>
    </div>
  );
}

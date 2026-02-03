import type { DriftAlert } from "@/lib/types";
import { cn } from "@/lib/utils";
import { formatDate } from "@/lib/utils";
import { AlertTriangle, TrendingUp } from "lucide-react";

interface DriftAlertCardProps {
  alert: DriftAlert;
}

const severityColors: Record<string, string> = {
  low: "border-yellow-200 bg-yellow-50 dark:border-yellow-900 dark:bg-yellow-950/30",
  medium: "border-orange-200 bg-orange-50 dark:border-orange-900 dark:bg-orange-950/30",
  high: "border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950/30",
};

export function DriftAlertCard({ alert }: DriftAlertCardProps) {
  const change = alert.current_value - alert.baseline_value;
  const changePercent = alert.baseline_value !== 0 ? (change / alert.baseline_value) * 100 : 0;

  return (
    <div
      role={alert.severity === "high" ? "alert" : undefined}
      className={cn(
        "rounded-lg border p-4",
        severityColors[alert.severity] || severityColors.low,
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <AlertTriangle
            size={18}
            className={cn(
              alert.severity === "high"
                ? "text-red-500"
                : alert.severity === "medium"
                  ? "text-orange-500"
                  : "text-yellow-500",
            )}
          />
          <div>
            <div className="font-medium">
              {alert.metric_name} drift in <span className="font-mono">{alert.span_kind}</span>{" "}
              spans
            </div>
            <div className="text-sm text-[var(--muted-foreground)]">
              PSI: {alert.psi_score.toFixed(3)} | Severity: {alert.severity}
            </div>
          </div>
        </div>

        <div className="text-right text-sm">
          <div className="flex items-center gap-1">
            <TrendingUp size={14} />
            <span className={change > 0 ? "text-red-500" : "text-green-500"}>
              {changePercent > 0 ? "+" : ""}
              {changePercent.toFixed(1)}%
            </span>
          </div>
          <div className="text-xs text-[var(--muted-foreground)]">
            {alert.baseline_value.toFixed(2)} → {alert.current_value.toFixed(2)}
          </div>
        </div>
      </div>

      <div className="mt-2 text-xs text-[var(--muted-foreground)]">
        {formatDate(alert.created_at)}
        {alert.resolved && (
          <span className="ml-2 rounded bg-green-100 px-1.5 py-0.5 text-green-700 dark:bg-green-900/30 dark:text-green-400">
            Resolved
          </span>
        )}
      </div>
    </div>
  );
}

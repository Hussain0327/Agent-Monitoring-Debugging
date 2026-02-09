"use client";

import { useEffect } from "react";
import { AlertTriangle, RotateCcw } from "lucide-react";

export default function DriftError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Drift page error:", error);
  }, [error]);

  return (
    <div className="flex min-h-[300px] flex-col items-center justify-center gap-5 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--danger-dim)]">
        <AlertTriangle size={24} className="text-[var(--danger)]" />
      </div>
      <div>
        <h2 className="text-lg font-semibold">Failed to load drift data</h2>
        <p className="mt-1 max-w-md font-mono text-xs text-[var(--muted-foreground)]">
          {error.message || "Could not fetch drift alerts."}
        </p>
      </div>
      <button
        onClick={reset}
        className="flex items-center gap-2 rounded-lg bg-[var(--accent)] px-4 py-2 text-sm font-medium text-[var(--background)] transition-colors hover:opacity-90"
      >
        <RotateCcw size={14} />
        Retry
      </button>
    </div>
  );
}

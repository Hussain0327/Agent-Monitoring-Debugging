"use client";

import { useEffect } from "react";
import { AlertTriangle, RotateCcw, ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function TraceDetailError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Trace detail error:", error);
  }, [error]);

  return (
    <div className="flex min-h-[300px] flex-col items-center justify-center gap-5 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--danger-dim)]">
        <AlertTriangle size={24} className="text-[var(--danger)]" />
      </div>
      <div>
        <h2 className="text-lg font-semibold">Failed to load trace</h2>
        <p className="mt-1 max-w-md font-mono text-xs text-[var(--muted-foreground)]">
          {error.message || "Could not fetch trace details."}
        </p>
      </div>
      <div className="flex gap-2">
        <button
          onClick={reset}
          className="flex items-center gap-2 rounded-lg bg-[var(--accent)] px-4 py-2 text-sm font-medium text-[var(--background)] transition-colors hover:opacity-90"
        >
          <RotateCcw size={14} />
          Retry
        </button>
        <Link
          href="/"
          className="flex items-center gap-2 rounded-lg border border-[var(--border)] px-4 py-2 text-sm font-medium text-[var(--muted-foreground)] transition-colors hover:bg-[var(--background-elevated)] hover:text-[var(--foreground)]"
        >
          <ArrowLeft size={14} />
          Dashboard
        </Link>
      </div>
    </div>
  );
}

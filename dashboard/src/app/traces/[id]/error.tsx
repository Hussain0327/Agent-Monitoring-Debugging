"use client";

import { useEffect } from "react";
import { AlertTriangle } from "lucide-react";
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
    <div className="flex min-h-[300px] flex-col items-center justify-center gap-4 text-center">
      <AlertTriangle size={40} className="text-red-500" />
      <h2 className="text-lg font-semibold">Failed to load trace</h2>
      <p className="max-w-md text-sm text-[var(--muted-foreground)]">
        {error.message || "Could not fetch trace details."}
      </p>
      <div className="flex gap-2">
        <button
          onClick={reset}
          className="rounded-md bg-vigil-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-vigil-700"
        >
          Retry
        </button>
        <Link
          href="/"
          className="rounded-md border border-[var(--border)] px-4 py-2 text-sm font-medium transition-colors hover:bg-[var(--muted)]"
        >
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
}

"use client";

import { useEffect } from "react";
import { AlertTriangle } from "lucide-react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Global error:", error);
  }, [error]);

  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center gap-4 text-center">
      <AlertTriangle size={48} className="text-red-500" />
      <h2 className="text-lg font-semibold">Something went wrong</h2>
      <p className="max-w-md text-sm text-[var(--muted-foreground)]">
        {error.message || "An unexpected error occurred."}
      </p>
      <button
        onClick={reset}
        className="rounded-md bg-vigil-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-vigil-700"
      >
        Try again
      </button>
    </div>
  );
}

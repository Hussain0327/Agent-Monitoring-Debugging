"use client";

import { useState } from "react";
import Link from "next/link";
import { useTraces } from "@/hooks/use-traces";
import { StatusBadge } from "./status-badge";
import { formatDuration, formatDate } from "@/lib/utils";

const PAGE_SIZE = 20;

interface TraceListProps {
  filters?: {
    status?: string;
    startDate?: string;
    endDate?: string;
  };
}

export function TraceList({ filters }: TraceListProps = {}) {
  const [page, setPage] = useState(0);
  const { data, isLoading, error } = useTraces({
    offset: page * PAGE_SIZE,
    limit: PAGE_SIZE,
    ...filters,
  });

  if (isLoading) {
    return <div className="text-sm text-[var(--muted-foreground)]">Loading traces...</div>;
  }

  if (error) {
    return <div className="text-sm text-red-500">Failed to load traces</div>;
  }

  if (!data?.traces.length) {
    return (
      <div className="rounded-lg border border-[var(--border)] p-8 text-center text-sm text-[var(--muted-foreground)]">
        No traces yet. Instrument your code with the Vigil SDK to start capturing traces.
      </div>
    );
  }

  const totalPages = Math.ceil(data.total / PAGE_SIZE);

  return (
    <div>
      <div className="overflow-hidden rounded-lg border border-[var(--border)]">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[var(--border)] bg-[var(--muted)]">
              <th scope="col" className="px-4 py-2 text-left font-medium">Name</th>
              <th scope="col" className="px-4 py-2 text-left font-medium">Status</th>
              <th scope="col" className="px-4 py-2 text-left font-medium">Spans</th>
              <th scope="col" className="px-4 py-2 text-left font-medium">Duration</th>
              <th scope="col" className="px-4 py-2 text-left font-medium">Time</th>
            </tr>
          </thead>
          <tbody>
            {data.traces.map((trace) => (
              <tr
                key={trace.id}
                className="border-b border-[var(--border)] last:border-0 hover:bg-[var(--muted)]"
              >
                <td className="px-4 py-2">
                  <Link
                    href={`/traces/${trace.id}`}
                    className="font-medium text-vigil-600 hover:underline"
                  >
                    {trace.name || "Unnamed"}
                  </Link>
                </td>
                <td className="px-4 py-2">
                  <StatusBadge status={trace.status} />
                </td>
                <td className="px-4 py-2 text-[var(--muted-foreground)]">{trace.span_count}</td>
                <td className="px-4 py-2 text-[var(--muted-foreground)]">
                  {formatDuration(trace.start_time, trace.end_time)}
                </td>
                <td className="px-4 py-2 text-[var(--muted-foreground)]">
                  {formatDate(trace.created_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="mt-4 flex items-center justify-between">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            aria-label="Previous page"
            className="rounded-md border border-[var(--border)] px-3 py-1.5 text-sm font-medium transition-colors hover:bg-[var(--muted)] disabled:cursor-not-allowed disabled:opacity-50"
          >
            Previous
          </button>
          <span className="text-sm text-[var(--muted-foreground)]">
            Page {page + 1} of {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1}
            aria-label="Next page"
            className="rounded-md border border-[var(--border)] px-3 py-1.5 text-sm font-medium transition-colors hover:bg-[var(--muted)] disabled:cursor-not-allowed disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

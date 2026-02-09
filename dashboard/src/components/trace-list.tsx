"use client";

import { useState } from "react";
import Link from "next/link";
import { useTraces } from "@/hooks/use-traces";
import { StatusBadge } from "./status-badge";
import { formatDuration, formatDate } from "@/lib/utils";
import { ChevronLeft, ChevronRight } from "lucide-react";

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
    return (
      <div className="space-y-1">
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="flex items-center gap-4 rounded-lg border border-[var(--border)] bg-[var(--background-raised)] px-4 py-3"
            style={{ animationDelay: `${i * 0.05}s` }}
          >
            <div className="h-3 w-36 animate-pulse rounded bg-[var(--border)]" />
            <div className="h-3 w-14 animate-pulse rounded bg-[var(--border)]" />
            <div className="h-3 w-8 animate-pulse rounded bg-[var(--border)]" />
            <div className="ml-auto h-3 w-20 animate-pulse rounded bg-[var(--border)]" />
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-[var(--danger)]/20 bg-[var(--danger-dim)] p-4 text-sm text-[var(--danger)]">
        Failed to load traces
      </div>
    );
  }

  if (!data?.traces.length) {
    return (
      <div className="rounded-xl border border-dashed border-[var(--border-bright)] p-10 text-center">
        <div className="font-mono text-sm text-[var(--muted-foreground)]">
          No traces yet. Instrument your code with the Vigil SDK to start capturing traces.
        </div>
      </div>
    );
  }

  const totalPages = Math.ceil(data.total / PAGE_SIZE);

  return (
    <div>
      {/* Table */}
      <div className="overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--background-raised)]">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[var(--border)] bg-[var(--background-elevated)]">
              <th scope="col" className="px-4 py-2.5 text-left font-mono text-[11px] font-medium uppercase tracking-wider text-[var(--muted-foreground)]">Name</th>
              <th scope="col" className="px-4 py-2.5 text-left font-mono text-[11px] font-medium uppercase tracking-wider text-[var(--muted-foreground)]">Status</th>
              <th scope="col" className="px-4 py-2.5 text-left font-mono text-[11px] font-medium uppercase tracking-wider text-[var(--muted-foreground)]">Spans</th>
              <th scope="col" className="px-4 py-2.5 text-left font-mono text-[11px] font-medium uppercase tracking-wider text-[var(--muted-foreground)]">Duration</th>
              <th scope="col" className="px-4 py-2.5 text-right font-mono text-[11px] font-medium uppercase tracking-wider text-[var(--muted-foreground)]">Time</th>
            </tr>
          </thead>
          <tbody>
            {data.traces.map((trace) => (
              <tr
                key={trace.id}
                className="group border-b border-[var(--border)] last:border-0 transition-colors hover:bg-[var(--accent-dim)]"
              >
                <td className="px-4 py-2.5">
                  <Link
                    href={`/traces/${trace.id}`}
                    className="font-medium text-[var(--foreground)] transition-colors group-hover:text-[var(--accent)]"
                  >
                    {trace.name || "Unnamed"}
                  </Link>
                </td>
                <td className="px-4 py-2.5">
                  <StatusBadge status={trace.status} />
                </td>
                <td className="px-4 py-2.5">
                  <span className="font-mono text-xs text-[var(--muted-foreground)]">{trace.span_count}</span>
                </td>
                <td className="px-4 py-2.5">
                  <span className="font-mono text-xs text-[var(--muted-foreground)]">
                    {formatDuration(trace.start_time, trace.end_time)}
                  </span>
                </td>
                <td className="px-4 py-2.5 text-right text-xs text-[var(--muted-foreground)]">
                  {formatDate(trace.created_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-4 flex items-center justify-between">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            aria-label="Previous page"
            className="flex items-center gap-1.5 rounded-lg border border-[var(--border)] px-3 py-1.5 text-sm font-medium transition-colors hover:bg-[var(--background-elevated)] disabled:cursor-not-allowed disabled:opacity-30"
          >
            <ChevronLeft size={14} />
            Previous
          </button>
          <span className="font-mono text-xs text-[var(--muted-foreground)]">
            {page + 1} / {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1}
            aria-label="Next page"
            className="flex items-center gap-1.5 rounded-lg border border-[var(--border)] px-3 py-1.5 text-sm font-medium transition-colors hover:bg-[var(--background-elevated)] disabled:cursor-not-allowed disabled:opacity-30"
          >
            Next
            <ChevronRight size={14} />
          </button>
        </div>
      )}
    </div>
  );
}

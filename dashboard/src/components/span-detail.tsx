"use client";

import type { Span } from "@/lib/types";
import { StatusBadge } from "./status-badge";
import { formatDuration, formatDate } from "@/lib/utils";

interface SpanDetailProps {
  span: Span;
}

export function SpanDetail({ span }: SpanDetailProps) {
  return (
    <div className="space-y-5 text-sm">
      <div className="grid grid-cols-2 gap-3">
        {[
          { label: "Name", value: <span className="font-mono text-xs">{span.name}</span> },
          { label: "Kind", value: <span className="rounded-md bg-[var(--background-elevated)] px-1.5 py-0.5 font-mono text-xs">{span.kind}</span> },
          { label: "Status", value: <StatusBadge status={span.status} /> },
          { label: "Duration", value: <span className="font-mono text-xs">{formatDuration(span.start_time, span.end_time)}</span> },
          { label: "Started", value: <span className="font-mono text-xs">{span.start_time ? formatDate(span.start_time) : "—"}</span> },
          { label: "Span ID", value: <span className="truncate font-mono text-[10px] text-[var(--muted-foreground)]">{span.id}</span> },
        ].map((item) => (
          <div key={item.label}>
            <div className="mb-1 font-mono text-[10px] uppercase tracking-wider text-[var(--muted-foreground)]">
              {item.label}
            </div>
            <div>{item.value}</div>
          </div>
        ))}
      </div>

      {span.input && (
        <div>
          <div className="mb-2 font-mono text-[10px] uppercase tracking-wider text-[var(--muted-foreground)]">
            Input
          </div>
          <pre className="max-h-48 overflow-auto rounded-lg border border-[var(--border)] bg-[var(--background)] p-3 font-mono text-xs text-[var(--foreground)]">
            {JSON.stringify(span.input, null, 2)}
          </pre>
        </div>
      )}

      {span.output && (
        <div>
          <div className="mb-2 font-mono text-[10px] uppercase tracking-wider text-[var(--muted-foreground)]">
            Output
          </div>
          <pre className="max-h-48 overflow-auto rounded-lg border border-[var(--border)] bg-[var(--background)] p-3 font-mono text-xs text-[var(--foreground)]">
            {JSON.stringify(span.output, null, 2)}
          </pre>
        </div>
      )}

      {span.events.length > 0 && (
        <div>
          <div className="mb-2 font-mono text-[10px] uppercase tracking-wider text-[var(--muted-foreground)]">
            Events ({span.events.length})
          </div>
          <div className="space-y-1">
            {span.events.map((event, i) => (
              <div key={i} className="flex items-center gap-2 rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2">
                <span className="font-mono text-xs font-medium text-[var(--accent-text)]">{event.name}</span>
                {event.timestamp && (
                  <span className="ml-auto font-mono text-[10px] text-[var(--muted-foreground)]">
                    {formatDate(event.timestamp)}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

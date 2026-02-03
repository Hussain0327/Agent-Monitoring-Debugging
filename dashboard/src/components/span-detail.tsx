"use client";

import type { Span } from "@/lib/types";
import { StatusBadge } from "./status-badge";
import { formatDuration, formatDate } from "@/lib/utils";

interface SpanDetailProps {
  span: Span;
}

export function SpanDetail({ span }: SpanDetailProps) {
  return (
    <div className="space-y-4 text-sm">
      <div className="grid grid-cols-2 gap-2">
        <div>
          <div className="text-[var(--muted-foreground)]">Name</div>
          <div className="font-mono">{span.name}</div>
        </div>
        <div>
          <div className="text-[var(--muted-foreground)]">Kind</div>
          <div className="font-mono">{span.kind}</div>
        </div>
        <div>
          <div className="text-[var(--muted-foreground)]">Status</div>
          <StatusBadge status={span.status} />
        </div>
        <div>
          <div className="text-[var(--muted-foreground)]">Duration</div>
          <div>{formatDuration(span.start_time, span.end_time)}</div>
        </div>
        <div>
          <div className="text-[var(--muted-foreground)]">Started</div>
          <div>{span.start_time ? formatDate(span.start_time) : "-"}</div>
        </div>
        <div>
          <div className="text-[var(--muted-foreground)]">Span ID</div>
          <div className="truncate font-mono text-xs">{span.id}</div>
        </div>
      </div>

      {span.input && (
        <div>
          <div className="mb-1 font-medium text-[var(--muted-foreground)]">Input</div>
          <pre className="max-h-48 overflow-auto rounded bg-[var(--muted)] p-3 text-xs">
            {JSON.stringify(span.input, null, 2)}
          </pre>
        </div>
      )}

      {span.output && (
        <div>
          <div className="mb-1 font-medium text-[var(--muted-foreground)]">Output</div>
          <pre className="max-h-48 overflow-auto rounded bg-[var(--muted)] p-3 text-xs">
            {JSON.stringify(span.output, null, 2)}
          </pre>
        </div>
      )}

      {span.events.length > 0 && (
        <div>
          <div className="mb-1 font-medium text-[var(--muted-foreground)]">
            Events ({span.events.length})
          </div>
          <div className="space-y-1">
            {span.events.map((event, i) => (
              <div key={i} className="rounded bg-[var(--muted)] p-2 text-xs">
                <span className="font-medium">{event.name}</span>
                {event.timestamp && (
                  <span className="ml-2 text-[var(--muted-foreground)]">
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

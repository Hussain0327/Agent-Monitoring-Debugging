"use client";

import type { Span } from "@/lib/types";
import { cn } from "@/lib/utils";

interface TraceTimelineProps {
  spans: Span[];
}

export function TraceTimeline({ spans }: TraceTimelineProps) {
  if (!spans.length) {
    return (
      <div className="text-sm text-[var(--muted-foreground)]">No spans to display.</div>
    );
  }

  const times = spans.flatMap((s) => [
    s.start_time ? new Date(s.start_time).getTime() : null,
    s.end_time ? new Date(s.end_time).getTime() : null,
  ]).filter((t): t is number => t !== null);

  if (!times.length) {
    return (
      <div className="text-sm text-[var(--muted-foreground)]">No timing data available.</div>
    );
  }

  const minTime = Math.min(...times);
  const maxTime = Math.max(...times);
  const totalDuration = maxTime - minTime || 1;

  const kindColors: Record<string, string> = {
    llm: "bg-blue-500",
    tool: "bg-green-500",
    chain: "bg-purple-500",
    retriever: "bg-orange-500",
    agent: "bg-pink-500",
    custom: "bg-gray-500",
  };

  return (
    <div className="space-y-1">
      {spans.map((span) => {
        const start = span.start_time ? new Date(span.start_time).getTime() : minTime;
        const end = span.end_time ? new Date(span.end_time).getTime() : maxTime;
        const leftPct = ((start - minTime) / totalDuration) * 100;
        const widthPct = Math.max(((end - start) / totalDuration) * 100, 1);

        return (
          <div key={span.id} className="flex items-center gap-2 text-xs">
            <div className="w-32 truncate text-[var(--muted-foreground)]" title={span.name}>
              {span.name || "unnamed"}
            </div>
            <div className="relative h-5 flex-1 rounded bg-[var(--muted)]">
              <div
                className={cn("absolute h-full rounded", kindColors[span.kind] || "bg-gray-400")}
                style={{ left: `${leftPct}%`, width: `${widthPct}%` }}
                title={`${span.kind} | ${end - start}ms`}
              />
            </div>
            <div className="w-16 text-right text-[var(--muted-foreground)]">
              {end - start}ms
            </div>
          </div>
        );
      })}
    </div>
  );
}

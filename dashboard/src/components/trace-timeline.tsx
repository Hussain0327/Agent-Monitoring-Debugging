"use client";

import type { Span } from "@/lib/types";
import { cn } from "@/lib/utils";

interface TraceTimelineProps {
  spans: Span[];
}

const kindColors: Record<string, { bar: string; text: string }> = {
  llm: { bar: "bg-[var(--accent)]", text: "text-[var(--accent-text)]" },
  tool: { bar: "bg-[var(--success)]", text: "text-[var(--success)]" },
  chain: { bar: "bg-purple-400", text: "text-purple-400" },
  retriever: { bar: "bg-orange-400", text: "text-orange-400" },
  agent: { bar: "bg-pink-400", text: "text-pink-400" },
  custom: { bar: "bg-[var(--muted-foreground)]", text: "text-[var(--muted-foreground)]" },
};

export function TraceTimeline({ spans }: TraceTimelineProps) {
  if (!spans.length) {
    return (
      <div className="font-mono text-xs text-[var(--muted-foreground)]">No spans to display.</div>
    );
  }

  const times = spans.flatMap((s) => [
    s.start_time ? new Date(s.start_time).getTime() : null,
    s.end_time ? new Date(s.end_time).getTime() : null,
  ]).filter((t): t is number => t !== null);

  if (!times.length) {
    return (
      <div className="font-mono text-xs text-[var(--muted-foreground)]">No timing data available.</div>
    );
  }

  const minTime = Math.min(...times);
  const maxTime = Math.max(...times);
  const totalDuration = maxTime - minTime || 1;

  return (
    <div className="space-y-1">
      {spans.map((span) => {
        const start = span.start_time ? new Date(span.start_time).getTime() : minTime;
        const end = span.end_time ? new Date(span.end_time).getTime() : maxTime;
        const leftPct = ((start - minTime) / totalDuration) * 100;
        const widthPct = Math.max(((end - start) / totalDuration) * 100, 1);
        const colors = kindColors[span.kind] || kindColors.custom;

        return (
          <div key={span.id} className="flex items-center gap-3 text-xs">
            <div
              className="w-32 truncate font-mono text-[11px] text-[var(--muted-foreground)]"
              title={span.name}
            >
              {span.name || "unnamed"}
            </div>
            <div className="relative h-6 flex-1 overflow-hidden rounded-md bg-[var(--background)]">
              <div
                className={cn("absolute h-full rounded-md opacity-80 transition-all", colors.bar)}
                style={{ left: `${leftPct}%`, width: `${widthPct}%` }}
                title={`${span.kind} | ${end - start}ms`}
              />
            </div>
            <div className={cn("w-16 text-right font-mono text-[10px]", colors.text)}>
              {end - start}ms
            </div>
          </div>
        );
      })}

      {/* Legend */}
      <div className="mt-3 flex flex-wrap items-center gap-3 border-t border-[var(--border)] pt-3">
        {Object.entries(kindColors).map(([kind, colors]) => (
          <div key={kind} className="flex items-center gap-1.5">
            <div className={cn("h-2 w-2 rounded-full", colors.bar)} />
            <span className="font-mono text-[10px] uppercase tracking-wider text-[var(--muted-foreground)]">
              {kind}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

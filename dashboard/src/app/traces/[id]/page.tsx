"use client";

import { use } from "react";
import { useTrace } from "@/hooks/use-traces";
import { SpanTree } from "@/components/span-tree";
import { SpanDetail } from "@/components/span-detail";
import { StatusBadge } from "@/components/status-badge";
import { TraceTimeline } from "@/components/trace-timeline";
import { ReplayControls } from "@/components/replay-controls";
import { DiffViewer } from "@/components/diff-viewer";
import { formatDuration, formatDate, buildSpanTree } from "@/lib/utils";
import { ArrowLeft, GitBranch, Clock, Play } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { useSearchParams } from "next/navigation";
import type { Span } from "@/lib/types";

type ViewMode = "tree" | "timeline" | "replay";

const modeConfig: Record<ViewMode, { icon: typeof GitBranch; label: string }> = {
  tree: { icon: GitBranch, label: "Tree" },
  timeline: { icon: Clock, label: "Timeline" },
  replay: { icon: Play, label: "Replay" },
};

export default function TraceDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const searchParams = useSearchParams();
  const initialMode = searchParams.get("mode") === "replay" ? "replay" : "tree";
  const { data: trace, isLoading, error } = useTrace(id);
  const [selectedSpan, setSelectedSpan] = useState<Span | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>(initialMode);
  const [replayDiffs, setReplayDiffs] = useState<Record<string, unknown>[]>([]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-64 animate-pulse rounded-lg bg-[var(--background-raised)]" />
        <div className="h-4 w-40 animate-pulse rounded bg-[var(--background-raised)]" />
        <div className="h-[400px] animate-pulse rounded-xl border border-[var(--border)] bg-[var(--background-raised)]" />
      </div>
    );
  }

  if (error || !trace) {
    return (
      <div className="rounded-xl border border-[var(--danger)]/20 bg-[var(--danger-dim)] p-6 text-center font-mono text-sm text-[var(--danger)]">
        Failed to load trace
      </div>
    );
  }

  const tree = buildSpanTree(trace.spans);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="animate-fade-up flex items-center gap-3">
        <Link
          href="/traces"
          className="flex h-8 w-8 items-center justify-center rounded-lg border border-[var(--border)] text-[var(--muted-foreground)] transition-colors hover:bg-[var(--background-elevated)] hover:text-[var(--foreground)]"
        >
          <ArrowLeft size={14} />
        </Link>
        <div>
          <h1 className="text-xl font-semibold tracking-tight">{trace.name || "Unnamed Trace"}</h1>
          <div className="mt-1 flex items-center gap-3">
            <StatusBadge status={trace.status} />
            <span className="font-mono text-xs text-[var(--muted-foreground)]">{trace.span_count} spans</span>
            <span className="font-mono text-xs text-[var(--muted-foreground)]">{formatDuration(trace.start_time, trace.end_time)}</span>
            <span className="font-mono text-xs text-[var(--muted-foreground)]">{formatDate(trace.created_at)}</span>
          </div>
        </div>
      </div>

      {/* View mode tabs */}
      <div className="animate-fade-up flex gap-1 rounded-xl border border-[var(--border)] bg-[var(--background-raised)] p-1" style={{ animationDelay: "0.05s" }}>
        {(Object.entries(modeConfig) as [ViewMode, typeof modeConfig.tree][]).map(([mode, cfg]) => {
          const Icon = cfg.icon;
          return (
            <button
              key={mode}
              onClick={() => setViewMode(mode)}
              className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                viewMode === mode
                  ? "bg-[var(--accent-dim)] text-[var(--accent-text)]"
                  : "text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
              }`}
            >
              <Icon size={13} />
              {cfg.label}
            </button>
          );
        })}
      </div>

      {/* Content */}
      {viewMode === "tree" && (
        <div className="animate-fade-up grid grid-cols-1 gap-4 lg:grid-cols-2" style={{ animationDelay: "0.1s" }}>
          <div className="rounded-xl border border-[var(--border)] bg-[var(--background-raised)] p-5">
            <h2 className="mb-4 flex items-center gap-2 text-sm font-semibold">
              <GitBranch size={14} className="text-[var(--accent)]" />
              Span Tree
            </h2>
            <SpanTree nodes={tree} onSelect={setSelectedSpan} selectedId={selectedSpan?.id} />
          </div>
          <div className="rounded-xl border border-[var(--border)] bg-[var(--background-raised)] p-5">
            <h2 className="mb-4 text-sm font-semibold">Span Detail</h2>
            {selectedSpan ? (
              <SpanDetail span={selectedSpan} />
            ) : (
              <p className="font-mono text-xs text-[var(--muted-foreground)]">Select a span to view details</p>
            )}
          </div>
        </div>
      )}

      {viewMode === "timeline" && (
        <div className="animate-fade-up rounded-xl border border-[var(--border)] bg-[var(--background-raised)] p-5" style={{ animationDelay: "0.1s" }}>
          <h2 className="mb-4 flex items-center gap-2 text-sm font-semibold">
            <Clock size={14} className="text-[var(--accent)]" />
            Timeline
          </h2>
          <TraceTimeline spans={trace.spans} />
        </div>
      )}

      {viewMode === "replay" && (
        <div className="animate-fade-up space-y-4" style={{ animationDelay: "0.1s" }}>
          <ReplayControls
            traceId={id}
            onReplayComplete={(data) => {
              setReplayDiffs(data.diffs);
            }}
          />
          {replayDiffs.length > 0 && (
            <div className="rounded-xl border border-[var(--border)] bg-[var(--background-raised)] p-5">
              <h2 className="mb-4 text-sm font-semibold">Replay Diff</h2>
              <DiffViewer diffs={replayDiffs as never} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

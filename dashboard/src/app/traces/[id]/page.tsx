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
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { useSearchParams } from "next/navigation";
import type { Span } from "@/lib/types";

type ViewMode = "tree" | "timeline" | "replay";

export default function TraceDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const searchParams = useSearchParams();
  const initialMode = searchParams.get("mode") === "replay" ? "replay" : "tree";
  const { data: trace, isLoading, error } = useTrace(id);
  const [selectedSpan, setSelectedSpan] = useState<Span | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>(initialMode);
  const [replayDiffs, setReplayDiffs] = useState<Record<string, unknown>[]>([]);

  if (isLoading) {
    return <div className="text-[var(--muted-foreground)]">Loading trace...</div>;
  }

  if (error || !trace) {
    return <div className="text-red-500">Failed to load trace</div>;
  }

  const tree = buildSpanTree(trace.spans);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link href="/traces" className="text-[var(--muted-foreground)] hover:text-[var(--foreground)]">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-semibold">{trace.name || "Unnamed Trace"}</h1>
          <div className="flex items-center gap-3 text-sm text-[var(--muted-foreground)]">
            <StatusBadge status={trace.status} />
            <span>{trace.span_count} spans</span>
            <span>{formatDuration(trace.start_time, trace.end_time)}</span>
            <span>{formatDate(trace.created_at)}</span>
          </div>
        </div>
      </div>

      <div className="flex gap-2">
        {(["tree", "timeline", "replay"] as const).map((mode) => (
          <button
            key={mode}
            onClick={() => setViewMode(mode)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium ${
              viewMode === mode
                ? "bg-vigil-100 text-vigil-700 dark:bg-vigil-900/30 dark:text-vigil-300"
                : "text-[var(--muted-foreground)] hover:bg-[var(--muted)]"
            }`}
          >
            {mode.charAt(0).toUpperCase() + mode.slice(1)}
          </button>
        ))}
      </div>

      {viewMode === "tree" && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="rounded-lg border border-[var(--border)] p-4">
            <h2 className="mb-3 font-medium">Span Tree</h2>
            <SpanTree nodes={tree} onSelect={setSelectedSpan} selectedId={selectedSpan?.id} />
          </div>
          <div className="rounded-lg border border-[var(--border)] p-4">
            <h2 className="mb-3 font-medium">Span Detail</h2>
            {selectedSpan ? (
              <SpanDetail span={selectedSpan} />
            ) : (
              <p className="text-sm text-[var(--muted-foreground)]">Select a span to view details</p>
            )}
          </div>
        </div>
      )}

      {viewMode === "timeline" && (
        <div className="rounded-lg border border-[var(--border)] p-4">
          <h2 className="mb-3 font-medium">Timeline</h2>
          <TraceTimeline spans={trace.spans} />
        </div>
      )}

      {viewMode === "replay" && (
        <div className="space-y-4">
          <ReplayControls
            traceId={id}
            onReplayComplete={(data) => {
              setReplayDiffs(data.diffs);
            }}
          />
          {replayDiffs.length > 0 && (
            <div className="rounded-lg border border-[var(--border)] p-4">
              <h2 className="mb-3 font-medium">Replay Diff</h2>
              <DiffViewer diffs={replayDiffs as never} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

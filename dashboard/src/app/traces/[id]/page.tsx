"use client";

import { use } from "react";
import { useTrace } from "@/hooks/use-traces";
import { SpanTree } from "@/components/span-tree";
import { SpanDetail } from "@/components/span-detail";
import { StatusBadge } from "@/components/status-badge";
import { formatDuration, formatDate, buildSpanTree } from "@/lib/utils";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import type { Span } from "@/lib/types";

export default function TraceDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: trace, isLoading, error } = useTrace(id);
  const [selectedSpan, setSelectedSpan] = useState<Span | null>(null);

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
        <Link href="/" className="text-[var(--muted-foreground)] hover:text-[var(--foreground)]">
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
    </div>
  );
}

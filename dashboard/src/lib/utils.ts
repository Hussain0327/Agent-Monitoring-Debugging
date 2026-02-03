import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import type { Span, SpanTreeNode } from "./types";

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export function formatDuration(startTime: string | null, endTime: string | null): string {
  if (!startTime || !endTime) return "-";
  const ms = new Date(endTime).getTime() - new Date(startTime).getTime();
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60_000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 60_000).toFixed(1)}m`;
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function buildSpanTree(spans: Span[]): SpanTreeNode[] {
  const nodeMap = new Map<string, SpanTreeNode>();
  const roots: SpanTreeNode[] = [];

  for (const span of spans) {
    nodeMap.set(span.id, { span, children: [] });
  }

  for (const span of spans) {
    const node = nodeMap.get(span.id)!;
    if (span.parent_span_id && nodeMap.has(span.parent_span_id)) {
      nodeMap.get(span.parent_span_id)!.children.push(node);
    } else {
      roots.push(node);
    }
  }

  return roots;
}

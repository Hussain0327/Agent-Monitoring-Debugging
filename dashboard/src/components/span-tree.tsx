"use client";

import { useState } from "react";
import { ChevronRight, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { StatusBadge } from "./status-badge";
import { formatDuration } from "@/lib/utils";
import type { SpanTreeNode } from "@/lib/types";

interface SpanTreeProps {
  nodes: SpanTreeNode[];
  onSelect: (span: SpanTreeNode["span"]) => void;
  selectedId?: string;
  depth?: number;
}

export function SpanTree({ nodes, onSelect, selectedId, depth = 0 }: SpanTreeProps) {
  return (
    <div role={depth === 0 ? "tree" : "group"} className="space-y-px">
      {nodes.map((node) => (
        <SpanTreeItem
          key={node.span.id}
          node={node}
          onSelect={onSelect}
          selectedId={selectedId}
          depth={depth}
        />
      ))}
    </div>
  );
}

function SpanTreeItem({
  node,
  onSelect,
  selectedId,
  depth,
}: {
  node: SpanTreeNode;
  onSelect: (span: SpanTreeNode["span"]) => void;
  selectedId?: string;
  depth: number;
}) {
  const [expanded, setExpanded] = useState(true);
  const hasChildren = node.children.length > 0;
  const isSelected = node.span.id === selectedId;

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case "ArrowRight":
        if (hasChildren && !expanded) {
          setExpanded(true);
          e.preventDefault();
        }
        break;
      case "ArrowLeft":
        if (hasChildren && expanded) {
          setExpanded(false);
          e.preventDefault();
        }
        break;
      case "Enter":
      case " ":
        onSelect(node.span);
        if (hasChildren) setExpanded(!expanded);
        e.preventDefault();
        break;
    }
  };

  return (
    <div
      role="treeitem"
      aria-expanded={hasChildren ? expanded : undefined}
      aria-selected={isSelected}
    >
      <button
        onClick={() => {
          onSelect(node.span);
          if (hasChildren) setExpanded(!expanded);
        }}
        onKeyDown={handleKeyDown}
        className={cn(
          "flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-sm transition-colors",
          isSelected
            ? "bg-[var(--accent-dim)] text-[var(--foreground)]"
            : "text-[var(--foreground)] hover:bg-[var(--background-elevated)]",
        )}
        style={{ paddingLeft: `${depth * 20 + 8}px` }}
      >
        {hasChildren ? (
          expanded ? (
            <ChevronDown size={12} className="shrink-0 text-[var(--muted-foreground)]" />
          ) : (
            <ChevronRight size={12} className="shrink-0 text-[var(--muted-foreground)]" />
          )
        ) : (
          <span className="w-3 shrink-0" />
        )}

        <StatusBadge status={node.span.status} size="sm" />

        <span className="truncate font-mono text-xs">{node.span.name || "unnamed"}</span>

        <span className="ml-auto shrink-0 rounded-md bg-[var(--background-elevated)] px-1.5 py-0.5 font-mono text-[10px] text-[var(--muted-foreground)]">
          {node.span.kind}
        </span>

        <span className="shrink-0 font-mono text-[10px] text-[var(--muted-foreground)]">
          {formatDuration(node.span.start_time, node.span.end_time)}
        </span>
      </button>

      {expanded && hasChildren && (
        <SpanTree nodes={node.children} onSelect={onSelect} selectedId={selectedId} depth={depth + 1} />
      )}
    </div>
  );
}

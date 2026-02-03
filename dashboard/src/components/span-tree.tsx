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
    <div role={depth === 0 ? "tree" : "group"} className="space-y-0.5">
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
          "flex w-full items-center gap-1.5 rounded px-2 py-1 text-left text-sm transition-colors",
          isSelected ? "bg-vigil-100 dark:bg-vigil-900/30" : "hover:bg-[var(--muted)]",
        )}
        style={{ paddingLeft: `${depth * 20 + 8}px` }}
      >
        {hasChildren ? (
          expanded ? (
            <ChevronDown size={14} className="shrink-0 text-[var(--muted-foreground)]" />
          ) : (
            <ChevronRight size={14} className="shrink-0 text-[var(--muted-foreground)]" />
          )
        ) : (
          <span className="w-3.5 shrink-0" />
        )}

        <StatusBadge status={node.span.status} size="sm" />

        <span className="truncate font-mono">{node.span.name || "unnamed"}</span>

        <span className="ml-auto shrink-0 text-xs text-[var(--muted-foreground)]">
          {node.span.kind}
        </span>

        <span className="shrink-0 text-xs text-[var(--muted-foreground)]">
          {formatDuration(node.span.start_time, node.span.end_time)}
        </span>
      </button>

      {expanded && hasChildren && (
        <SpanTree nodes={node.children} onSelect={onSelect} selectedId={selectedId} depth={depth + 1} />
      )}
    </div>
  );
}

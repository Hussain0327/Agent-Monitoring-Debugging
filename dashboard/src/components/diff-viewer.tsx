"use client";

import { cn } from "@/lib/utils";
import { ArrowRight, Copy, Cpu } from "lucide-react";

interface DiffItem {
  span_id: string;
  span_name: string;
  original_input: Record<string, unknown>;
  mutated_input: Record<string, unknown>;
  original_output: Record<string, unknown> | null;
  new_output?: Record<string, unknown> | null;
  was_executed?: boolean;
  note?: string;
}

interface DiffViewerProps {
  diffs: DiffItem[];
}

export function DiffViewer({ diffs }: DiffViewerProps) {
  if (!diffs.length) {
    return (
      <div className="font-mono text-xs text-[var(--muted-foreground)]">
        No diffs — no mutations were applied.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {diffs.map((diff) => (
        <div key={diff.span_id} className="rounded-xl border border-[var(--border)] bg-[var(--background-raised)] overflow-hidden">
          <div className="flex items-center gap-2 border-b border-[var(--border)] px-4 py-3">
            <span className="font-mono text-sm font-medium text-[var(--foreground)]">{diff.span_name}</span>
            {diff.was_executed === false && (
              <span className="flex items-center gap-1 rounded-md bg-[var(--background-elevated)] px-1.5 py-0.5 font-mono text-[10px] text-[var(--muted-foreground)]">
                <Copy size={9} />
                Copied
              </span>
            )}
            {diff.was_executed && (
              <span className="flex items-center gap-1 rounded-md bg-[var(--accent-dim)] px-1.5 py-0.5 font-mono text-[10px] text-[var(--accent-text)]">
                <Cpu size={9} />
                Re-executed
              </span>
            )}
          </div>

          <div className="grid grid-cols-2 divide-x divide-[var(--border)]">
            <div className="p-4">
              <div className="mb-2 font-mono text-[10px] uppercase tracking-wider text-[var(--danger)]">
                Original Input
              </div>
              <pre className="max-h-48 overflow-auto rounded-lg bg-[var(--danger-dim)] p-3 font-mono text-xs text-[var(--foreground)]">
                {JSON.stringify(diff.original_input, null, 2)}
              </pre>
            </div>
            <div className="p-4">
              <div className="mb-2 font-mono text-[10px] uppercase tracking-wider text-[var(--success)]">
                Mutated Input
              </div>
              <pre className="max-h-48 overflow-auto rounded-lg bg-[var(--success-dim)] p-3 font-mono text-xs text-[var(--foreground)]">
                {JSON.stringify(diff.mutated_input, null, 2)}
              </pre>
            </div>
          </div>

          {/* Outputs */}
          {(diff.original_output || diff.new_output) && (
            <div className={cn(
              "grid divide-x divide-[var(--border)] border-t border-[var(--border)]",
              diff.original_output && diff.new_output ? "grid-cols-2" : "grid-cols-1",
            )}>
              {diff.original_output && (
                <div className="p-4">
                  <div className="mb-2 font-mono text-[10px] uppercase tracking-wider text-[var(--muted-foreground)]">
                    Original Output
                  </div>
                  <pre className="max-h-48 overflow-auto rounded-lg border border-[var(--border)] bg-[var(--background)] p-3 font-mono text-xs text-[var(--foreground)]">
                    {JSON.stringify(diff.original_output, null, 2)}
                  </pre>
                </div>
              )}
              {diff.new_output && (
                <div className="p-4">
                  <div className="mb-2 flex items-center gap-1 font-mono text-[10px] uppercase tracking-wider text-[var(--accent-text)]">
                    <ArrowRight size={10} />
                    New Output
                  </div>
                  <pre className="max-h-48 overflow-auto rounded-lg bg-[var(--accent-dim)] p-3 font-mono text-xs text-[var(--foreground)]">
                    {JSON.stringify(diff.new_output, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

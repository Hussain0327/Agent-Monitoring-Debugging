"use client";

interface DiffItem {
  span_id: string;
  span_name: string;
  original_input: Record<string, unknown>;
  mutated_input: Record<string, unknown>;
  original_output: Record<string, unknown> | null;
  note?: string;
}

interface DiffViewerProps {
  diffs: DiffItem[];
}

export function DiffViewer({ diffs }: DiffViewerProps) {
  if (!diffs.length) {
    return (
      <div className="text-sm text-[var(--muted-foreground)]">
        No diffs — no mutations were applied.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {diffs.map((diff) => (
        <div key={diff.span_id} className="rounded-lg border border-[var(--border)] p-4">
          <div className="mb-2 text-sm font-medium">{diff.span_name}</div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="mb-1 text-xs font-medium text-red-500">Original Input</div>
              <pre className="rounded-md bg-red-50 p-3 text-xs dark:bg-red-900/20">
                {JSON.stringify(diff.original_input, null, 2)}
              </pre>
            </div>
            <div>
              <div className="mb-1 text-xs font-medium text-green-500">Mutated Input</div>
              <pre className="rounded-md bg-green-50 p-3 text-xs dark:bg-green-900/20">
                {JSON.stringify(diff.mutated_input, null, 2)}
              </pre>
            </div>
          </div>
          {diff.original_output && (
            <div className="mt-3">
              <div className="mb-1 text-xs font-medium text-[var(--muted-foreground)]">Original Output</div>
              <pre className="rounded-md bg-[var(--muted)] p-3 text-xs">
                {JSON.stringify(diff.original_output, null, 2)}
              </pre>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

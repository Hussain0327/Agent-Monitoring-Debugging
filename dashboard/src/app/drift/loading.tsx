export default function DriftLoading() {
  return (
    <div className="space-y-6">
      <div className="h-8 w-48 animate-pulse rounded bg-[var(--muted)]" />
      <div className="grid grid-cols-3 gap-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="rounded-lg border border-[var(--border)] p-4">
            <div className="mb-2 h-3 w-20 animate-pulse rounded bg-[var(--muted)]" />
            <div className="h-8 w-16 animate-pulse rounded bg-[var(--muted)]" />
          </div>
        ))}
      </div>
      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="rounded-lg border border-[var(--border)] p-4">
            <div className="flex justify-between">
              <div className="space-y-2">
                <div className="h-4 w-48 animate-pulse rounded bg-[var(--muted)]" />
                <div className="h-3 w-32 animate-pulse rounded bg-[var(--muted)]" />
              </div>
              <div className="h-6 w-16 animate-pulse rounded bg-[var(--muted)]" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

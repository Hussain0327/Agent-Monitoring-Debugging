export default function TraceDetailLoading() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <div className="h-8 w-8 animate-pulse rounded bg-[var(--muted)]" />
        <div className="h-6 w-64 animate-pulse rounded bg-[var(--muted)]" />
        <div className="h-5 w-16 animate-pulse rounded-full bg-[var(--muted)]" />
      </div>
      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-2 rounded-lg border border-[var(--border)] p-4">
          <div className="mb-3 h-4 w-24 animate-pulse rounded bg-[var(--muted)]" />
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="flex items-center gap-2" style={{ paddingLeft: `${(i % 3) * 20}px` }}>
              <div className="h-4 w-4 animate-pulse rounded bg-[var(--muted)]" />
              <div className="h-4 w-12 animate-pulse rounded-full bg-[var(--muted)]" />
              <div className="h-4 w-32 animate-pulse rounded bg-[var(--muted)]" />
            </div>
          ))}
        </div>
        <div className="space-y-4 rounded-lg border border-[var(--border)] p-4">
          <div className="h-4 w-32 animate-pulse rounded bg-[var(--muted)]" />
          <div className="grid grid-cols-2 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i}>
                <div className="mb-1 h-3 w-16 animate-pulse rounded bg-[var(--muted)]" />
                <div className="h-4 w-24 animate-pulse rounded bg-[var(--muted)]" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Loading() {
  return (
    <div className="space-y-6">
      <div className="h-8 w-48 animate-pulse rounded bg-[var(--muted)]" />
      <div className="rounded-lg border border-[var(--border)] p-4">
        <div className="mb-4 h-4 w-40 animate-pulse rounded bg-[var(--muted)]" />
        <div className="h-[200px] animate-pulse rounded bg-[var(--muted)]" />
      </div>
      <div className="rounded-lg border border-[var(--border)]">
        <div className="border-b border-[var(--border)] bg-[var(--muted)] px-4 py-3">
          <div className="h-4 w-64 animate-pulse rounded bg-[var(--border)]" />
        </div>
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="flex gap-4 border-b border-[var(--border)] px-4 py-3 last:border-0">
            <div className="h-4 w-32 animate-pulse rounded bg-[var(--muted)]" />
            <div className="h-4 w-16 animate-pulse rounded bg-[var(--muted)]" />
            <div className="h-4 w-12 animate-pulse rounded bg-[var(--muted)]" />
            <div className="h-4 w-20 animate-pulse rounded bg-[var(--muted)]" />
            <div className="h-4 w-28 animate-pulse rounded bg-[var(--muted)]" />
          </div>
        ))}
      </div>
    </div>
  );
}

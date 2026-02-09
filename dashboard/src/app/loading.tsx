export default function Loading() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 animate-pulse rounded-xl bg-[var(--background-raised)]" />
        <div>
          <div className="h-6 w-48 animate-pulse rounded-lg bg-[var(--background-raised)]" />
          <div className="mt-1.5 h-3 w-32 animate-pulse rounded bg-[var(--background-raised)]" />
        </div>
      </div>

      <div className="rounded-xl border border-[var(--border)] bg-[var(--background-raised)] p-5">
        <div className="mb-4 h-4 w-40 animate-pulse rounded bg-[var(--background-elevated)]" />
        <div className="h-[200px] animate-pulse rounded-lg bg-[var(--background-elevated)]" />
      </div>

      <div className="overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--background-raised)]">
        <div className="border-b border-[var(--border)] px-5 py-3">
          <div className="h-3 w-64 animate-pulse rounded bg-[var(--background-elevated)]" />
        </div>
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="flex gap-4 border-b border-[var(--border)] px-5 py-3 last:border-0"
            style={{ opacity: 1 - i * 0.15 }}
          >
            <div className="h-3 w-32 animate-pulse rounded bg-[var(--background-elevated)]" />
            <div className="h-3 w-16 animate-pulse rounded bg-[var(--background-elevated)]" />
            <div className="h-3 w-12 animate-pulse rounded bg-[var(--background-elevated)]" />
            <div className="h-3 w-20 animate-pulse rounded bg-[var(--background-elevated)]" />
            <div className="h-3 w-28 animate-pulse rounded bg-[var(--background-elevated)]" />
          </div>
        ))}
      </div>
    </div>
  );
}

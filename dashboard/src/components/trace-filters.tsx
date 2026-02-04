"use client";

interface TraceFilterValues {
  status?: string;
  startDate?: string;
  endDate?: string;
}

interface TraceFiltersProps {
  filters: TraceFilterValues;
  onChange: (filters: TraceFilterValues) => void;
}

const STATUS_OPTIONS = ["", "ok", "error", "unset"];

export function TraceFilters({ filters, onChange }: TraceFiltersProps) {
  return (
    <div className="flex flex-wrap items-end gap-4 rounded-lg border border-[var(--border)] p-4">
      <div>
        <label htmlFor="status-filter" className="mb-1 block text-xs font-medium text-[var(--muted-foreground)]">
          Status
        </label>
        <select
          id="status-filter"
          value={filters.status || ""}
          onChange={(e) => onChange({ ...filters, status: e.target.value || undefined })}
          className="rounded-md border border-[var(--border)] bg-[var(--background)] px-3 py-1.5 text-sm"
        >
          <option value="">All statuses</option>
          {STATUS_OPTIONS.filter(Boolean).map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="start-date" className="mb-1 block text-xs font-medium text-[var(--muted-foreground)]">
          Start date
        </label>
        <input
          id="start-date"
          type="date"
          value={filters.startDate || ""}
          onChange={(e) => onChange({ ...filters, startDate: e.target.value || undefined })}
          className="rounded-md border border-[var(--border)] bg-[var(--background)] px-3 py-1.5 text-sm"
        />
      </div>

      <div>
        <label htmlFor="end-date" className="mb-1 block text-xs font-medium text-[var(--muted-foreground)]">
          End date
        </label>
        <input
          id="end-date"
          type="date"
          value={filters.endDate || ""}
          onChange={(e) => onChange({ ...filters, endDate: e.target.value || undefined })}
          className="rounded-md border border-[var(--border)] bg-[var(--background)] px-3 py-1.5 text-sm"
        />
      </div>

      <button
        onClick={() => onChange({})}
        className="rounded-md border border-[var(--border)] px-3 py-1.5 text-sm text-[var(--muted-foreground)] hover:bg-[var(--border)]"
      >
        Clear filters
      </button>
    </div>
  );
}

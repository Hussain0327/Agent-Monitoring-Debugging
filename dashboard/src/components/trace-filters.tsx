"use client";

import { X } from "lucide-react";

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
  const hasFilters = filters.status || filters.startDate || filters.endDate;

  return (
    <div className="flex flex-wrap items-end gap-4 rounded-xl border border-[var(--border)] bg-[var(--background-raised)] p-4">
      <div>
        <label htmlFor="status-filter" className="mb-1.5 block font-mono text-[10px] font-medium uppercase tracking-wider text-[var(--muted-foreground)]">
          Status
        </label>
        <select
          id="status-filter"
          value={filters.status || ""}
          onChange={(e) => onChange({ ...filters, status: e.target.value || undefined })}
          className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-1.5 text-sm transition-colors focus:border-[var(--accent)] focus:outline-none"
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
        <label htmlFor="start-date" className="mb-1.5 block font-mono text-[10px] font-medium uppercase tracking-wider text-[var(--muted-foreground)]">
          Start date
        </label>
        <input
          id="start-date"
          type="date"
          value={filters.startDate || ""}
          onChange={(e) => onChange({ ...filters, startDate: e.target.value || undefined })}
          className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-1.5 text-sm transition-colors focus:border-[var(--accent)] focus:outline-none"
        />
      </div>

      <div>
        <label htmlFor="end-date" className="mb-1.5 block font-mono text-[10px] font-medium uppercase tracking-wider text-[var(--muted-foreground)]">
          End date
        </label>
        <input
          id="end-date"
          type="date"
          value={filters.endDate || ""}
          onChange={(e) => onChange({ ...filters, endDate: e.target.value || undefined })}
          className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-1.5 text-sm transition-colors focus:border-[var(--accent)] focus:outline-none"
        />
      </div>

      {hasFilters && (
        <button
          onClick={() => onChange({})}
          className="flex items-center gap-1.5 rounded-lg border border-[var(--border)] px-3 py-1.5 text-sm text-[var(--muted-foreground)] transition-colors hover:bg-[var(--background-elevated)] hover:text-[var(--foreground)]"
        >
          <X size={12} />
          Clear
        </button>
      )}
    </div>
  );
}

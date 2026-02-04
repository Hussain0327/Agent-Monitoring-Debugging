"use client";

import { TraceList } from "@/components/trace-list";
import { TraceFilters } from "@/components/trace-filters";
import { useState } from "react";

export default function TracesPage() {
  const [filters, setFilters] = useState<{
    status?: string;
    startDate?: string;
    endDate?: string;
  }>({});

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Traces</h1>
        <p className="text-[var(--muted-foreground)]">Browse and filter all traces</p>
      </div>

      <TraceFilters filters={filters} onChange={setFilters} />
      <TraceList filters={filters} />
    </div>
  );
}

"use client";

import { TraceList } from "@/components/trace-list";
import { MetricsChart } from "@/components/metrics-chart";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <p className="text-[var(--muted-foreground)]">Monitor your AI agent pipelines</p>
      </div>

      <MetricsChart />

      <div>
        <h2 className="mb-4 text-lg font-medium">Recent Traces</h2>
        <TraceList />
      </div>
    </div>
  );
}

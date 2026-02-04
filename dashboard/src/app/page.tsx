"use client";

import { MetricsChart } from "@/components/metrics-chart";
import { TraceList } from "@/components/trace-list";
import Link from "next/link";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <p className="text-[var(--muted-foreground)]">Monitor your AI agent pipelines</p>
      </div>

      <MetricsChart />

      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-medium">Recent Traces</h2>
          <Link
            href="/traces"
            className="text-sm text-vigil-600 hover:underline"
          >
            View all traces
          </Link>
        </div>
        <TraceList />
      </div>
    </div>
  );
}

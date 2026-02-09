"use client";

import { MetricsChart } from "@/components/metrics-chart";
import { TraceList } from "@/components/trace-list";
import Link from "next/link";
import { ArrowRight, Activity, Zap, AlertTriangle } from "lucide-react";

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-fade-up">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--accent-dim)] glow-accent-sm">
            <Activity size={20} className="text-[var(--accent)]" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
            <p className="text-sm text-[var(--muted-foreground)]">Monitor your AI agent pipelines</p>
          </div>
        </div>
      </div>

      {/* Quick Stats Row */}
      <div className="animate-fade-up grid grid-cols-3 gap-4" style={{ animationDelay: "0.05s" }}>
        <div className="rounded-xl border border-[var(--border)] bg-[var(--background-raised)] p-5">
          <div className="flex items-center gap-2 text-[var(--muted-foreground)]">
            <Zap size={14} />
            <span className="font-mono text-[11px] uppercase tracking-wider">Latency</span>
          </div>
          <div className="mt-2 font-mono text-2xl font-light text-[var(--foreground)]">—</div>
          <div className="mt-1 text-xs text-[var(--muted-foreground)]">avg response time</div>
        </div>
        <div className="rounded-xl border border-[var(--border)] bg-[var(--background-raised)] p-5">
          <div className="flex items-center gap-2 text-[var(--muted-foreground)]">
            <Activity size={14} />
            <span className="font-mono text-[11px] uppercase tracking-wider">Traces</span>
          </div>
          <div className="mt-2 font-mono text-2xl font-light text-[var(--foreground)]">—</div>
          <div className="mt-1 text-xs text-[var(--muted-foreground)]">last 24 hours</div>
        </div>
        <div className="rounded-xl border border-[var(--border)] bg-[var(--background-raised)] p-5">
          <div className="flex items-center gap-2 text-[var(--muted-foreground)]">
            <AlertTriangle size={14} />
            <span className="font-mono text-[11px] uppercase tracking-wider">Drift</span>
          </div>
          <div className="mt-2 font-mono text-2xl font-light text-[var(--foreground)]">—</div>
          <div className="mt-1 text-xs text-[var(--muted-foreground)]">active alerts</div>
        </div>
      </div>

      {/* Metrics Chart */}
      <div className="animate-fade-up" style={{ animationDelay: "0.1s" }}>
        <MetricsChart />
      </div>

      {/* Recent Traces */}
      <div className="animate-fade-up" style={{ animationDelay: "0.15s" }}>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-base font-semibold">Recent Traces</h2>
          <Link
            href="/traces"
            className="group flex items-center gap-1 text-sm text-[var(--accent-text)] transition-colors hover:text-[var(--accent)]"
          >
            View all
            <ArrowRight size={14} className="transition-transform group-hover:translate-x-0.5" />
          </Link>
        </div>
        <TraceList />
      </div>
    </div>
  );
}

"use client";

import { useQuery } from "@tanstack/react-query";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { api } from "@/lib/api";
import { Zap } from "lucide-react";

const placeholderData = [
  { time: "00:00", latency: 0 },
  { time: "04:00", latency: 0 },
  { time: "08:00", latency: 0 },
  { time: "12:00", latency: 0 },
  { time: "16:00", latency: 0 },
  { time: "20:00", latency: 0 },
  { time: "24:00", latency: 0 },
];

function computeLatencyBuckets(
  spans: { start_time: string | null; end_time: string | null }[],
): { time: string; latency: number }[] {
  const buckets: Record<string, number[]> = {};

  for (const span of spans) {
    if (!span.start_time || !span.end_time) continue;
    const start = new Date(span.start_time);
    const end = new Date(span.end_time);
    const ms = end.getTime() - start.getTime();
    if (ms < 0) continue;

    const hour = start.getHours();
    const bucket = `${String(hour).padStart(2, "0")}:00`;
    if (!buckets[bucket]) buckets[bucket] = [];
    buckets[bucket].push(ms);
  }

  const result: { time: string; latency: number }[] = [];
  for (let h = 0; h < 24; h++) {
    const bucket = `${String(h).padStart(2, "0")}:00`;
    const values = buckets[bucket];
    if (values && values.length > 0) {
      const avg = values.reduce((a, b) => a + b, 0) / values.length;
      result.push({ time: bucket, latency: Math.round(avg) });
    } else {
      result.push({ time: bucket, latency: 0 });
    }
  }

  return result;
}

export function MetricsChart() {
  const { data: spanData } = useQuery({
    queryKey: ["spans-metrics"],
    queryFn: () => api.spans.list({ limit: 200 }),
    refetchInterval: 10_000,
  });

  const chartData =
    spanData && spanData.spans.length > 0
      ? computeLatencyBuckets(spanData.spans)
      : placeholderData;

  const hasData = spanData && spanData.spans.length > 0;

  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--background-raised)] p-5">
      <div className="mb-4 flex items-center gap-2">
        <Zap size={14} className="text-[var(--accent)]" />
        <h3 className="text-sm font-semibold">
          Latency
          <span className="ml-2 font-mono text-[11px] font-normal text-[var(--muted-foreground)]">
            24h {!hasData && "— no data"}
          </span>
        </h3>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="latencyGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--accent)" stopOpacity={0.2} />
              <stop offset="100%" stopColor="var(--accent)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis
            dataKey="time"
            tick={{ fontSize: 11, fontFamily: "JetBrains Mono", fill: "var(--muted-foreground)" }}
            stroke="var(--border)"
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fontFamily: "JetBrains Mono", fill: "var(--muted-foreground)" }}
            stroke="var(--border)"
            axisLine={false}
            tickLine={false}
            width={40}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--background-elevated)",
              border: "1px solid var(--border)",
              borderRadius: "8px",
              fontSize: "12px",
              fontFamily: "JetBrains Mono",
              color: "var(--foreground)",
            }}
            labelStyle={{ color: "var(--muted-foreground)" }}
          />
          <Area
            type="monotone"
            dataKey="latency"
            stroke="var(--accent)"
            fill="url(#latencyGradient)"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

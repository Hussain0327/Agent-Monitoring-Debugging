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
    <div className="rounded-lg border border-[var(--border)] p-4">
      <h3 className="mb-4 text-sm font-medium">
        Latency (ms) — Last 24h
        {!hasData && (
          <span className="ml-2 text-xs text-[var(--muted-foreground)]">
            (no data yet)
          </span>
        )}
      </h3>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="time" tick={{ fontSize: 12 }} stroke="var(--muted-foreground)" />
          <YAxis tick={{ fontSize: 12 }} stroke="var(--muted-foreground)" />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--muted)",
              border: "1px solid var(--border)",
              borderRadius: "6px",
              fontSize: "12px",
            }}
          />
          <Area
            type="monotone"
            dataKey="latency"
            stroke="#5c7cfa"
            fill="#5c7cfa"
            fillOpacity={0.1}
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

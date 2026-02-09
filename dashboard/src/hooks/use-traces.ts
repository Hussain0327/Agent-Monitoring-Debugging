"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useTraces(params?: {
  offset?: number;
  limit?: number;
  status?: string;
  startDate?: string;
  endDate?: string;
}) {
  return useQuery({
    queryKey: ["traces", params],
    queryFn: () => api.traces.list(params),
    // WebSocket invalidation is primary; keep polling as fallback at 30s
    refetchInterval: 30000,
  });
}

export function useTrace(id: string) {
  return useQuery({
    queryKey: ["trace", id],
    queryFn: () => api.traces.get(id),
    enabled: !!id,
  });
}

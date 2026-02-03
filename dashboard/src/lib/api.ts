import type { Trace, TraceListResponse, SpanListResponse, DriftAlert, DriftSummary } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

class APIError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "APIError";
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const body = await res.text();
    throw new APIError(res.status, body || res.statusText);
  }

  return res.json();
}

export const api = {
  traces: {
    list(params?: { offset?: number; limit?: number }): Promise<TraceListResponse> {
      const qs = new URLSearchParams();
      if (params?.offset) qs.set("offset", String(params.offset));
      if (params?.limit) qs.set("limit", String(params.limit));
      const query = qs.toString();
      return request(`/v1/traces${query ? `?${query}` : ""}`);
    },

    get(id: string): Promise<Trace> {
      return request(`/v1/traces/${id}`);
    },
  },

  spans: {
    list(params?: { kind?: string; status?: string; limit?: number; offset?: number }): Promise<SpanListResponse> {
      const qs = new URLSearchParams();
      if (params?.kind) qs.set("kind", params.kind);
      if (params?.status) qs.set("status", params.status);
      if (params?.offset) qs.set("offset", String(params.offset));
      if (params?.limit) qs.set("limit", String(params.limit));
      const query = qs.toString();
      return request(`/v1/spans${query ? `?${query}` : ""}`);
    },
  },

  drift: {
    alerts(includeResolved = false): Promise<DriftAlert[]> {
      return request(`/v1/drift/alerts?include_resolved=${includeResolved}`);
    },

    summary(): Promise<DriftSummary> {
      return request("/v1/drift/summary");
    },
  },
};

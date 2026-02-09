import type {
  Trace,
  TraceListResponse,
  SpanListResponse,
  DriftAlert,
  DriftSummary,
  ReplayRun,
  ReplayDiff,
  ReplayEstimateResponse,
  Notification,
  ProjectSettings,
} from "./types";
import { getToken, clearToken } from "./auth";

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
  const token = getToken();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options?.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(url, {
    ...options,
    headers,
  });

  if (res.status === 401) {
    clearToken();
    throw new APIError(401, "Unauthorized");
  }

  if (!res.ok) {
    const body = await res.text();
    throw new APIError(res.status, body || res.statusText);
  }

  return res.json();
}

export const api = {
  auth: {
    login(email: string, password: string): Promise<{ access_token: string; token_type: string }> {
      return request("/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
    },

    register(email: string, password: string): Promise<{ id: string; email: string }> {
      return request("/v1/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
    },
  },

  traces: {
    list(params?: {
      offset?: number;
      limit?: number;
      status?: string;
      startDate?: string;
      endDate?: string;
    }): Promise<TraceListResponse> {
      const qs = new URLSearchParams();
      if (params?.offset) qs.set("offset", String(params.offset));
      if (params?.limit) qs.set("limit", String(params.limit));
      if (params?.status) qs.set("status", params.status);
      if (params?.startDate) qs.set("start_date", params.startDate);
      if (params?.endDate) qs.set("end_date", params.endDate);
      const query = qs.toString();
      return request(`/v1/traces${query ? `?${query}` : ""}`);
    },

    get(id: string): Promise<Trace> {
      return request(`/v1/traces/${id}`);
    },

    update(id: string, data: { status?: string; metadata?: Record<string, unknown> }): Promise<Trace> {
      return request(`/v1/traces/${id}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      });
    },

    addEvent(traceId: string, spanId: string, data: { name: string; attributes?: Record<string, unknown> }): Promise<Record<string, unknown>> {
      return request(`/v1/traces/${traceId}/events/${spanId}`, {
        method: "POST",
        body: JSON.stringify(data),
      });
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

    resolve(alertId: string): Promise<DriftAlert> {
      return request(`/v1/drift/alerts/${alertId}/resolve`, {
        method: "PATCH",
      });
    },
  },

  replay: {
    run(traceId: string, mutations: Record<string, Record<string, unknown>>): Promise<ReplayEstimateResponse> {
      return request(`/v1/traces/${traceId}/replay`, {
        method: "POST",
        body: JSON.stringify({ mutations }),
      });
    },

    confirm(traceId: string, replayId: string): Promise<ReplayRun> {
      return request(`/v1/traces/${traceId}/replay/${replayId}/confirm`, {
        method: "POST",
      });
    },

    cancel(traceId: string, replayId: string): Promise<ReplayRun> {
      return request(`/v1/traces/${traceId}/replay/${replayId}/cancel`, {
        method: "POST",
      });
    },

    status(traceId: string, replayId: string): Promise<ReplayRun> {
      return request(`/v1/traces/${traceId}/replay/${replayId}`);
    },

    diff(traceId: string, replayId: string): Promise<ReplayDiff> {
      return request(`/v1/traces/${traceId}/replay/${replayId}/diff`);
    },
  },

  notifications: {
    list(params?: { unread_only?: boolean; limit?: number; offset?: number }): Promise<Notification[]> {
      const qs = new URLSearchParams();
      if (params?.unread_only) qs.set("unread_only", "true");
      if (params?.limit) qs.set("limit", String(params.limit));
      if (params?.offset) qs.set("offset", String(params.offset));
      const query = qs.toString();
      return request(`/v1/notifications${query ? `?${query}` : ""}`);
    },

    markRead(id: string): Promise<Notification> {
      return request(`/v1/notifications/${id}/read`, {
        method: "PATCH",
      });
    },

    markAllRead(): Promise<{ marked_read: number }> {
      return request("/v1/notifications/read-all", {
        method: "POST",
      });
    },

    count(): Promise<{ unread: number }> {
      return request("/v1/notifications/count");
    },
  },

  projects: {
    getSettings(projectId: string): Promise<ProjectSettings> {
      return request(`/v1/projects/${projectId}/settings`);
    },

    updateSettings(projectId: string, data: {
      openai_api_key?: string;
      anthropic_api_key?: string;
      default_openai_model?: string;
      default_anthropic_model?: string;
      drift_check_interval_minutes?: number;
      drift_check_enabled?: boolean;
    }): Promise<ProjectSettings> {
      return request(`/v1/projects/${projectId}/settings`, {
        method: "PUT",
        body: JSON.stringify(data),
      });
    },
  },
};

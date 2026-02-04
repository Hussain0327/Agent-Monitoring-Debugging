export interface Span {
  id: string;
  trace_id: string;
  parent_span_id: string | null;
  name: string;
  kind: SpanKind;
  status: SpanStatus;
  input: Record<string, unknown> | null;
  output: Record<string, unknown> | null;
  metadata: Record<string, unknown>;
  events: SpanEvent[];
  start_time: string | null;
  end_time: string | null;
  created_at: string;
}

export interface Trace {
  id: string;
  project_id: string;
  name: string;
  status: string;
  metadata: Record<string, unknown>;
  start_time: string | null;
  end_time: string | null;
  created_at: string;
  span_count: number;
  spans: Span[];
}

export interface TraceListResponse {
  traces: Trace[];
  total: number;
  offset: number;
  limit: number;
}

export interface SpanEvent {
  name: string;
  timestamp: string;
  attributes: Record<string, unknown>;
}

export interface DriftAlert {
  id: string;
  project_id: string;
  span_kind: string;
  metric_name: string;
  baseline_value: number;
  current_value: number;
  psi_score: number;
  severity: "low" | "medium" | "high";
  resolved: boolean;
  created_at: string;
}

export interface DriftSummary {
  total_alerts: number;
  unresolved: number;
  by_severity: Record<string, number>;
  recent_alerts: DriftAlert[];
}

export type SpanKind = "llm" | "tool" | "chain" | "retriever" | "agent" | "custom";
export type SpanStatus = "ok" | "error" | "unset";

export interface SpanTreeNode {
  span: Span;
  children: SpanTreeNode[];
}

export interface SpanListResponse {
  spans: Span[];
  total: number;
  offset: number;
  limit: number;
}

export interface ReplayRun {
  id: string;
  original_trace_id: string;
  status: string;
  created_by: string | null;
  config: Record<string, unknown>;
  result_trace_id: string | null;
  created_at: string;
}

export interface ReplayDiff {
  original_trace_id: string;
  mutations: Record<string, unknown>;
  diffs: Array<{
    span_id: string;
    span_name: string;
    original_input: Record<string, unknown>;
    mutated_input: Record<string, unknown>;
    original_output: Record<string, unknown> | null;
    note: string;
  }>;
}

export interface ReplayConfig {
  mutations: Record<string, Record<string, unknown>>;
}

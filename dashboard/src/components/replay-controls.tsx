"use client";

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { ReplayEstimateResponse } from "@/lib/types";
import Link from "next/link";
import { Play, Loader2, CheckCircle, XCircle, DollarSign, Cpu, ArrowRight, RotateCcw } from "lucide-react";

interface ReplayControlsProps {
  traceId: string;
  onReplayComplete?: (data: { diffs: Record<string, unknown>[]; replay_run_id?: string }) => void;
}

type Phase = "input" | "estimating" | "confirming" | "running" | "completed" | "failed" | "cancelled";

export function ReplayControls({ traceId, onReplayComplete }: ReplayControlsProps) {
  const [mutationsJson, setMutationsJson] = useState("{}");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [phase, setPhase] = useState<Phase>("input");
  const [estimate, setEstimate] = useState<ReplayEstimateResponse | null>(null);
  const [replayRunId, setReplayRunId] = useState<string | null>(null);

  const { data: replayStatus } = useQuery({
    queryKey: ["replay", traceId, replayRunId],
    queryFn: () => api.replay.status(traceId, replayRunId!),
    enabled: !!replayRunId && phase === "running",
    refetchInterval: 2000,
  });

  useEffect(() => {
    if (!replayStatus) return;
    if (replayStatus.status === "completed") {
      setPhase("completed");
      if (replayRunId) {
        api.replay.diff(traceId, replayRunId).then((diff) => {
          onReplayComplete?.({ diffs: diff.diffs as unknown as Record<string, unknown>[], replay_run_id: replayRunId });
        });
      }
    } else if (replayStatus.status === "failed") {
      setPhase("failed");
      setError(replayStatus.error_message || "Replay failed");
    }
  }, [replayStatus, replayRunId, traceId, onReplayComplete]);

  async function handleEstimate() {
    setError("");
    setLoading(true);
    try {
      const mutations = JSON.parse(mutationsJson);
      const result = await api.replay.run(traceId, mutations);
      setEstimate(result);
      setReplayRunId(result.replay_run_id);
      setPhase("confirming");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create estimate");
    } finally {
      setLoading(false);
    }
  }

  async function handleConfirm() {
    if (!replayRunId) return;
    setError("");
    setLoading(true);
    try {
      await api.replay.confirm(traceId, replayRunId);
      setPhase("running");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to confirm replay");
    } finally {
      setLoading(false);
    }
  }

  async function handleCancel() {
    if (!replayRunId) return;
    setError("");
    try {
      await api.replay.cancel(traceId, replayRunId);
      setPhase("cancelled");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to cancel");
    }
  }

  function handleReset() {
    setPhase("input");
    setEstimate(null);
    setReplayRunId(null);
    setError("");
  }

  return (
    <div className="space-y-4 rounded-xl border border-[var(--border)] bg-[var(--background-raised)] p-5">
      <div className="flex items-center gap-2">
        <Play size={14} className="text-[var(--accent)]" />
        <h3 className="text-sm font-semibold">Replay Trace</h3>
      </div>

      {/* Phase 1: Input mutations */}
      {phase === "input" && (
        <>
          <div>
            <label htmlFor="mutations" className="mb-1.5 block font-mono text-[10px] uppercase tracking-wider text-[var(--muted-foreground)]">
              Mutations (JSON: span_id → field overrides)
            </label>
            <textarea
              id="mutations"
              rows={4}
              value={mutationsJson}
              onChange={(e) => setMutationsJson(e.target.value)}
              className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 font-mono text-xs text-[var(--foreground)] transition-colors focus:border-[var(--accent)] focus:outline-none"
            />
          </div>
          <button
            onClick={handleEstimate}
            disabled={loading}
            className="flex items-center gap-2 rounded-lg bg-[var(--accent)] px-4 py-2 text-sm font-medium text-[var(--background)] transition-colors hover:opacity-90 disabled:opacity-50"
          >
            {loading ? (
              <Loader2 size={14} className="animate-spin" />
            ) : (
              <DollarSign size={14} />
            )}
            {loading ? "Estimating..." : "Get Cost Estimate"}
          </button>
        </>
      )}

      {/* Phase 2: Show estimate, confirm or cancel */}
      {phase === "confirming" && estimate && (
        <div className="space-y-4">
          <div className="rounded-lg border border-[var(--warning)]/20 bg-[var(--warning-dim)] p-4">
            <div className="flex items-center gap-2 text-sm font-medium text-[var(--warning)]">
              <DollarSign size={14} />
              Cost Estimate
            </div>
            <div className="mt-3 grid grid-cols-2 gap-3">
              <div>
                <div className="font-mono text-[10px] uppercase tracking-wider text-[var(--muted-foreground)]">LLM Spans</div>
                <div className="mt-0.5 font-mono text-lg font-light">{estimate.llm_spans_count}</div>
              </div>
              <div>
                <div className="font-mono text-[10px] uppercase tracking-wider text-[var(--muted-foreground)]">Est. Cost</div>
                <div className="mt-0.5 font-mono text-lg font-light text-[var(--warning)]">
                  ${estimate.estimated_cost_usd.toFixed(4)}
                </div>
              </div>
            </div>
            {estimate.llm_spans.length > 0 && (
              <div className="mt-3 space-y-1 border-t border-[var(--warning)]/10 pt-3">
                {estimate.llm_spans.map((s) => (
                  <div key={s.span_id} className="flex items-center justify-between font-mono text-[11px] text-[var(--muted-foreground)]">
                    <span className="flex items-center gap-1.5">
                      <Cpu size={10} />
                      {s.span_name}
                      <span className="rounded bg-[var(--background-elevated)] px-1 py-0.5 text-[10px]">{s.provider}</span>
                    </span>
                    <span>${s.estimated_cost_usd.toFixed(4)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleConfirm}
              disabled={loading}
              className="flex items-center gap-2 rounded-lg bg-[var(--success)] px-4 py-2 text-sm font-medium text-[var(--background)] transition-colors hover:opacity-90 disabled:opacity-50"
            >
              {loading ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                <CheckCircle size={14} />
              )}
              {loading ? "Confirming..." : "Confirm & Execute"}
            </button>
            <button
              onClick={handleCancel}
              className="flex items-center gap-1.5 rounded-lg border border-[var(--border)] px-4 py-2 text-sm text-[var(--muted-foreground)] transition-colors hover:bg-[var(--background-elevated)] hover:text-[var(--foreground)]"
            >
              <XCircle size={14} />
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Phase 3: Running */}
      {phase === "running" && (
        <div className="flex items-center gap-3 rounded-lg border border-[var(--accent)]/20 bg-[var(--accent-dim)] p-4">
          <Loader2 size={16} className="animate-spin text-[var(--accent)]" />
          <span className="text-sm text-[var(--accent-text)]">Executing replay...</span>
        </div>
      )}

      {/* Phase 4: Completed */}
      {phase === "completed" && replayStatus?.result_trace_id && (
        <div className="space-y-3 rounded-lg border border-[var(--success)]/20 bg-[var(--success-dim)] p-4">
          <div className="flex items-center gap-2 text-sm font-medium text-[var(--success)]">
            <CheckCircle size={14} />
            Replay completed
          </div>
          {replayStatus.actual_cost_usd != null && (
            <div className="font-mono text-xs text-[var(--muted-foreground)]">
              Actual cost: ${replayStatus.actual_cost_usd.toFixed(4)}
            </div>
          )}
          <div className="flex items-center gap-3">
            <Link
              href={`/traces/${replayStatus.result_trace_id}`}
              className="flex items-center gap-1.5 text-sm text-[var(--accent-text)] transition-colors hover:text-[var(--accent)]"
            >
              View result trace
              <ArrowRight size={14} />
            </Link>
            <button onClick={handleReset} className="flex items-center gap-1.5 text-xs text-[var(--muted-foreground)] transition-colors hover:text-[var(--foreground)]">
              <RotateCcw size={10} />
              Run another
            </button>
          </div>
        </div>
      )}

      {/* Failed or cancelled */}
      {(phase === "failed" || phase === "cancelled") && (
        <div className="space-y-3 rounded-lg border border-[var(--danger)]/20 bg-[var(--danger-dim)] p-4">
          <div className="flex items-center gap-2 text-sm text-[var(--danger)]">
            <XCircle size={14} />
            {phase === "failed" ? "Replay failed" : "Replay cancelled"}
          </div>
          <button onClick={handleReset} className="flex items-center gap-1.5 text-xs text-[var(--accent-text)] transition-colors hover:text-[var(--accent)]">
            <RotateCcw size={10} />
            Try again
          </button>
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-[var(--danger)]/20 bg-[var(--danger-dim)] px-3 py-2 font-mono text-xs text-[var(--danger)]">
          {error}
        </div>
      )}
    </div>
  );
}

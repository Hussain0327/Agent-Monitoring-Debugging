"use client";

import { useState } from "react";
import { api } from "@/lib/api";

interface ReplayControlsProps {
  traceId: string;
  onReplayComplete?: (data: { diffs: Record<string, unknown>[]; replay_run_id?: string }) => void;
}

export function ReplayControls({ traceId, onReplayComplete }: ReplayControlsProps) {
  const [mutationsJson, setMutationsJson] = useState("{}");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleReplay() {
    setError("");
    setLoading(true);
    try {
      const mutations = JSON.parse(mutationsJson);
      const result = await api.replay.run(traceId, mutations);
      onReplayComplete?.(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Replay failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-3 rounded-lg border border-[var(--border)] p-4">
      <h3 className="font-medium">Replay Trace</h3>

      <div>
        <label htmlFor="mutations" className="mb-1 block text-xs text-[var(--muted-foreground)]">
          Mutations (JSON: span_id -&gt; field overrides)
        </label>
        <textarea
          id="mutations"
          rows={4}
          value={mutationsJson}
          onChange={(e) => setMutationsJson(e.target.value)}
          className="w-full rounded-md border border-[var(--border)] bg-[var(--background)] px-3 py-2 font-mono text-xs"
        />
      </div>

      {error && (
        <div className="text-sm text-red-500">{error}</div>
      )}

      <button
        onClick={handleReplay}
        disabled={loading}
        className="rounded-md bg-vigil-600 px-4 py-2 text-sm font-medium text-white hover:bg-vigil-700 disabled:opacity-50"
      >
        {loading ? "Running..." : "Run Replay"}
      </button>
    </div>
  );
}

"""Tests for trace replay endpoint."""

from __future__ import annotations

import pytest
import uuid


class TestReplay:
    async def test_replay_not_found(self, client):
        res = await client.post(
            "/v1/traces/nonexistent/replay",
            json={"mutations": {}},
        )
        assert res.status_code == 404

    async def test_replay_with_mutations(self, client):
        # First ingest a trace with spans
        span_id = uuid.uuid4().hex
        trace_id = uuid.uuid4().hex
        await client.post(
            "/v1/traces",
            json={
                "spans": [
                    {
                        "span_id": span_id,
                        "trace_id": trace_id,
                        "name": "llm-call",
                        "kind": "llm",
                        "status": "ok",
                        "input": {"model": "gpt-4", "prompt": "hello"},
                        "output": {"response": "world"},
                    }
                ],
                "trace_name": "test-trace",
            },
        )

        # Now replay with mutations
        res = await client.post(
            f"/v1/traces/{trace_id}/replay",
            json={"mutations": {span_id: {"model": "gpt-4-turbo"}}},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["original_trace_id"] == trace_id
        assert len(data["diffs"]) == 1
        assert data["diffs"][0]["mutated_input"]["model"] == "gpt-4-turbo"

    async def test_replay_no_mutations(self, client):
        span_id = uuid.uuid4().hex
        trace_id = uuid.uuid4().hex
        await client.post(
            "/v1/traces",
            json={
                "spans": [{"span_id": span_id, "trace_id": trace_id, "name": "test", "kind": "custom", "status": "ok"}],
                "trace_name": "test",
            },
        )
        res = await client.post(
            f"/v1/traces/{trace_id}/replay",
            json={"mutations": {}},
        )
        assert res.status_code == 200
        assert res.json()["diffs"] == []

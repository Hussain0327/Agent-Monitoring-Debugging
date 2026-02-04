"""Tests for trace replay endpoint."""

from __future__ import annotations

import uuid

import pytest


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
        assert "replay_run_id" in data

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

    async def test_get_replay_status(self, client):
        """GET /v1/traces/{id}/replay/{replay_id} returns replay run status."""
        span_id = uuid.uuid4().hex
        trace_id = uuid.uuid4().hex
        await client.post(
            "/v1/traces",
            json={
                "spans": [{"span_id": span_id, "trace_id": trace_id, "name": "t", "kind": "custom"}],
                "trace_name": "replay-status-test",
            },
        )
        replay_res = await client.post(
            f"/v1/traces/{trace_id}/replay",
            json={"mutations": {}},
        )
        replay_id = replay_res.json()["replay_run_id"]

        status_res = await client.get(f"/v1/traces/{trace_id}/replay/{replay_id}")
        assert status_res.status_code == 200
        data = status_res.json()
        assert data["status"] == "completed"
        assert data["original_trace_id"] == trace_id

    async def test_get_replay_diff(self, client):
        """GET /v1/traces/{id}/replay/{replay_id}/diff returns diff data."""
        span_id = uuid.uuid4().hex
        trace_id = uuid.uuid4().hex
        await client.post(
            "/v1/traces",
            json={
                "spans": [{
                    "span_id": span_id, "trace_id": trace_id,
                    "name": "t", "kind": "llm",
                    "input": {"model": "gpt-4"},
                }],
                "trace_name": "replay-diff-test",
            },
        )
        replay_res = await client.post(
            f"/v1/traces/{trace_id}/replay",
            json={"mutations": {span_id: {"model": "gpt-4o"}}},
        )
        replay_id = replay_res.json()["replay_run_id"]

        diff_res = await client.get(f"/v1/traces/{trace_id}/replay/{replay_id}/diff")
        assert diff_res.status_code == 200
        data = diff_res.json()
        assert data["original_trace_id"] == trace_id
        assert len(data["diffs"]) == 1

    async def test_get_replay_not_found(self, client):
        """GET replay endpoints return 404 for nonexistent IDs."""
        res = await client.get("/v1/traces/fake/replay/fake")
        assert res.status_code == 404

        res = await client.get("/v1/traces/fake/replay/fake/diff")
        assert res.status_code == 404

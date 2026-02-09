"""Tests for trace replay endpoints."""

from __future__ import annotations

import uuid


class TestReplay:
    async def test_replay_not_found(self, client):
        res = await client.post(
            "/v1/traces/nonexistent/replay",
            json={"mutations": {}},
        )
        assert res.status_code == 404

    async def test_replay_estimate_with_mutations(self, client):
        """POST /v1/traces/{id}/replay now returns a cost estimate."""
        span_id = uuid.uuid4().hex
        trace_id = uuid.uuid4().hex
        await client.post(
            "/v1/traces",
            json={
                "spans": [
                    {
                        "span_id": span_id,
                        "trace_id": trace_id,
                        "name": "openai-llm-call",
                        "kind": "llm",
                        "status": "ok",
                        "input": {"model": "gpt-4", "prompt": "hello"},
                        "output": {"response": "world"},
                    }
                ],
                "trace_name": "test-trace",
            },
        )

        # Replay now returns a cost estimate (two-phase API)
        res = await client.post(
            f"/v1/traces/{trace_id}/replay",
            json={"mutations": {span_id: {"model": "gpt-4-turbo"}}},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["original_trace_id"] == trace_id
        assert data["status"] == "estimating"
        assert "replay_run_id" in data
        assert "estimated_cost_usd" in data
        assert data["llm_spans_count"] == 1
        assert len(data["llm_spans"]) == 1
        assert data["llm_spans"][0]["provider"] == "openai"

    async def test_replay_estimate_no_llm_spans(self, client):
        """Non-LLM spans result in zero LLM spans in estimate."""
        span_id = uuid.uuid4().hex
        trace_id = uuid.uuid4().hex
        await client.post(
            "/v1/traces",
            json={
                "spans": [
                    {
                        "span_id": span_id,
                        "trace_id": trace_id,
                        "name": "test",
                        "kind": "custom",
                        "status": "ok",
                    }
                ],
                "trace_name": "test",
            },
        )
        res = await client.post(
            f"/v1/traces/{trace_id}/replay",
            json={"mutations": {}},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["llm_spans_count"] == 0
        assert data["llm_spans"] == []
        assert data["estimated_cost_usd"] == 0.0

    async def test_get_replay_status(self, client):
        """GET /v1/traces/{id}/replay/{replay_id} returns replay run status."""
        span_id = uuid.uuid4().hex
        trace_id = uuid.uuid4().hex
        await client.post(
            "/v1/traces",
            json={
                "spans": [
                    {
                        "span_id": span_id,
                        "trace_id": trace_id,
                        "name": "t",
                        "kind": "custom",
                    }
                ],
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
        assert data["status"] == "estimating"
        assert data["original_trace_id"] == trace_id

    async def test_cancel_replay(self, client):
        """POST cancel transitions from estimating to cancelled."""
        span_id = uuid.uuid4().hex
        trace_id = uuid.uuid4().hex
        await client.post(
            "/v1/traces",
            json={
                "spans": [
                    {
                        "span_id": span_id,
                        "trace_id": trace_id,
                        "name": "t",
                        "kind": "custom",
                    }
                ],
                "trace_name": "cancel-test",
            },
        )
        replay_res = await client.post(
            f"/v1/traces/{trace_id}/replay",
            json={"mutations": {}},
        )
        replay_id = replay_res.json()["replay_run_id"]

        cancel_res = await client.post(
            f"/v1/traces/{trace_id}/replay/{replay_id}/cancel"
        )
        assert cancel_res.status_code == 200
        assert cancel_res.json()["status"] == "cancelled"

    async def test_get_replay_not_found(self, client):
        """GET replay endpoints return 404 for nonexistent IDs."""
        res = await client.get("/v1/traces/fake/replay/fake")
        assert res.status_code == 404

        res = await client.get("/v1/traces/fake/replay/fake/diff")
        assert res.status_code == 404

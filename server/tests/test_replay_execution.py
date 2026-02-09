"""Tests for replay execution (estimate, confirm, cancel)."""

from __future__ import annotations

import uuid

import pytest


@pytest.mark.asyncio
async def test_replay_estimate(client):
    """POST /v1/traces/{id}/replay returns a cost estimate."""
    span_id = uuid.uuid4().hex
    trace_id = uuid.uuid4().hex
    await client.post(
        "/v1/traces",
        json={
            "spans": [
                {
                    "span_id": span_id,
                    "trace_id": trace_id,
                    "name": "openai-chat",
                    "kind": "llm",
                    "status": "ok",
                    "input": {"model": "gpt-4o", "messages": [{"role": "user", "content": "Hello"}]},
                    "output": {"content": "Hi there!"},
                },
                {
                    "span_id": uuid.uuid4().hex,
                    "trace_id": trace_id,
                    "name": "search-tool",
                    "kind": "tool",
                    "status": "ok",
                    "input": {"query": "test"},
                    "output": {"results": []},
                },
            ],
            "trace_name": "test-trace",
        },
    )

    resp = await client.post(f"/v1/traces/{trace_id}/replay", json={"mutations": {}})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "estimating"
    assert data["llm_spans_count"] == 1
    assert data["estimated_cost_usd"] >= 0
    assert "replay_run_id" in data


@pytest.mark.asyncio
async def test_replay_estimate_with_mutations(client):
    """Replay estimate includes mutated LLM spans."""
    span_id = uuid.uuid4().hex
    trace_id = uuid.uuid4().hex
    await client.post(
        "/v1/traces",
        json={
            "spans": [
                {
                    "span_id": span_id,
                    "trace_id": trace_id,
                    "name": "openai-chat",
                    "kind": "llm",
                    "status": "ok",
                    "input": {"model": "gpt-4o", "messages": [{"role": "user", "content": "Hello"}]},
                    "output": {"content": "Hi there!"},
                },
            ],
            "trace_name": "test-trace",
        },
    )

    resp = await client.post(
        f"/v1/traces/{trace_id}/replay",
        json={"mutations": {span_id: {"messages": [{"role": "user", "content": "Changed!"}]}}},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["llm_spans_count"] == 1


@pytest.mark.asyncio
async def test_replay_cancel(client):
    """Cancel a replay in estimating status."""
    trace_id = uuid.uuid4().hex
    await client.post(
        "/v1/traces",
        json={
            "spans": [
                {
                    "span_id": uuid.uuid4().hex,
                    "trace_id": trace_id,
                    "name": "t",
                    "kind": "custom",
                    "status": "ok",
                }
            ],
            "trace_name": "cancel-test",
        },
    )

    # Create estimate
    resp = await client.post(f"/v1/traces/{trace_id}/replay", json={"mutations": {}})
    replay_id = resp.json()["replay_run_id"]

    # Cancel it
    resp = await client.post(f"/v1/traces/{trace_id}/replay/{replay_id}/cancel")
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


@pytest.mark.asyncio
async def test_replay_cancel_already_cancelled(client):
    """Cannot cancel a replay that's already cancelled."""
    trace_id = uuid.uuid4().hex
    await client.post(
        "/v1/traces",
        json={
            "spans": [
                {
                    "span_id": uuid.uuid4().hex,
                    "trace_id": trace_id,
                    "name": "t",
                    "kind": "custom",
                    "status": "ok",
                }
            ],
            "trace_name": "double-cancel-test",
        },
    )

    resp = await client.post(f"/v1/traces/{trace_id}/replay", json={"mutations": {}})
    replay_id = resp.json()["replay_run_id"]

    await client.post(f"/v1/traces/{trace_id}/replay/{replay_id}/cancel")
    resp = await client.post(f"/v1/traces/{trace_id}/replay/{replay_id}/cancel")
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_replay_status(client):
    """GET replay status endpoint."""
    trace_id = uuid.uuid4().hex
    await client.post(
        "/v1/traces",
        json={
            "spans": [
                {
                    "span_id": uuid.uuid4().hex,
                    "trace_id": trace_id,
                    "name": "t",
                    "kind": "custom",
                    "status": "ok",
                }
            ],
            "trace_name": "status-test",
        },
    )

    resp = await client.post(f"/v1/traces/{trace_id}/replay", json={"mutations": {}})
    replay_id = resp.json()["replay_run_id"]

    resp = await client.get(f"/v1/traces/{trace_id}/replay/{replay_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == replay_id
    assert data["status"] == "estimating"


@pytest.mark.asyncio
async def test_replay_not_found(client):
    """Replay for non-existent trace returns 404."""
    resp = await client.post("/v1/traces/nonexistent/replay", json={"mutations": {}})
    assert resp.status_code == 404

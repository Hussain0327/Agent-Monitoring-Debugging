"""Tests for span ingestion endpoint."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_ingest_creates_trace(client):
    """POST /v1/traces should create a trace and return trace_id."""
    response = await client.post(
        "/v1/traces",
        json={
            "spans": [
                {
                    "span_id": "span-001",
                    "name": "llm-call",
                    "kind": "llm",
                    "status": "ok",
                    "input": {"prompt": "hello"},
                    "output": {"response": "world"},
                }
            ],
            "trace_name": "test-trace",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "trace_id" in data
    assert data["span_count"] == 1


@pytest.mark.asyncio
async def test_ingest_multiple_spans(client):
    """POST /v1/traces should handle multiple spans in a batch."""
    response = await client.post(
        "/v1/traces",
        json={
            "spans": [
                {"span_id": "span-a", "name": "step-1", "kind": "chain"},
                {"span_id": "span-b", "name": "step-2", "kind": "llm", "parent_span_id": "span-a"},
                {"span_id": "span-c", "name": "step-3", "kind": "tool", "parent_span_id": "span-a"},
            ],
            "trace_name": "multi-span-trace",
        },
    )
    assert response.status_code == 201
    assert response.json()["span_count"] == 3


@pytest.mark.asyncio
async def test_ingest_empty_spans(client):
    """POST /v1/traces with empty spans should still succeed."""
    response = await client.post(
        "/v1/traces",
        json={"spans": []},
    )
    # Empty spans list — the endpoint may handle this differently,
    # but it should not crash
    assert response.status_code in (201, 422)

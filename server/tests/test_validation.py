"""Tests for input validation on server schemas."""

from __future__ import annotations

import uuid
import pytest


class TestSpanKindValidation:
    async def test_invalid_kind_rejected(self, client):
        res = await client.post(
            "/v1/traces",
            json={
                "spans": [
                    {
                        "span_id": uuid.uuid4().hex,
                        "name": "test",
                        "kind": "invalid_kind",
                        "status": "ok",
                    }
                ],
                "trace_name": "test",
            },
        )
        assert res.status_code == 422

    async def test_invalid_status_rejected(self, client):
        res = await client.post(
            "/v1/traces",
            json={
                "spans": [
                    {
                        "span_id": uuid.uuid4().hex,
                        "name": "test",
                        "kind": "llm",
                        "status": "invalid_status",
                    }
                ],
                "trace_name": "test",
            },
        )
        assert res.status_code == 422


class TestEmptySpans:
    async def test_empty_spans_rejected(self, client):
        res = await client.post(
            "/v1/traces",
            json={"spans": [], "trace_name": "test"},
        )
        assert res.status_code == 422


class TestProjectNameValidation:
    async def test_empty_name_rejected(self, client):
        res = await client.post("/v1/projects", json={"name": ""})
        assert res.status_code == 422

    async def test_too_long_name(self, client):
        res = await client.post("/v1/projects", json={"name": "x" * 300})
        assert res.status_code == 422

    async def test_valid_name_accepted(self, client):
        res = await client.post("/v1/projects", json={"name": "Valid Name"})
        assert res.status_code == 201

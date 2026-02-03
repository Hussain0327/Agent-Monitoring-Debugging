"""Pydantic schemas for span queries."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SpanResponse(BaseModel):
    id: str
    trace_id: str
    parent_span_id: str | None
    name: str
    kind: str
    status: str
    input: dict[str, Any] | None
    output: dict[str, Any] | None
    metadata: dict[str, Any]
    events: list[dict[str, Any]]
    start_time: datetime | None
    end_time: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SpanTreeNode(BaseModel):
    span: SpanResponse
    children: list["SpanTreeNode"] = Field(default_factory=list)


class SpanListResponse(BaseModel):
    spans: list[SpanResponse]
    total: int
    offset: int
    limit: int

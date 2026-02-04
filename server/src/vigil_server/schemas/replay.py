"""Pydantic schemas for replay endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ReplayRequest(BaseModel):
    """Schema for initiating a replay."""

    mutations: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Map of span_id -> {field: new_value} for input overrides",
    )


class ReplayRunResponse(BaseModel):
    """Schema for a replay run in responses."""

    id: str
    original_trace_id: str
    status: str
    created_by: str | None
    config: dict[str, Any]
    result_trace_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReplayDiffResponse(BaseModel):
    """Schema for replay diff output."""

    original_trace_id: str
    mutations: dict[str, Any]
    diffs: list[dict[str, Any]]

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
    estimated_cost_usd: float | None = None
    actual_cost_usd: float | None = None
    error_message: str | None = None
    llm_spans_count: int = 0
    project_id: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReplayEstimateResponse(BaseModel):
    """Schema for replay cost estimate."""

    replay_run_id: str
    original_trace_id: str
    status: str
    estimated_cost_usd: float
    llm_spans_count: int
    llm_spans: list[dict[str, Any]] = []


class SpanDiff(BaseModel):
    """Enhanced span diff with execution info."""

    span_id: str
    span_name: str
    original_input: dict[str, Any]
    mutated_input: dict[str, Any]
    original_output: dict[str, Any] | None = None
    new_output: dict[str, Any] | None = None
    was_executed: bool = False
    note: str | None = None


class ReplayDiffResponse(BaseModel):
    """Schema for replay diff output."""

    original_trace_id: str
    mutations: dict[str, Any]
    diffs: list[dict[str, Any]]

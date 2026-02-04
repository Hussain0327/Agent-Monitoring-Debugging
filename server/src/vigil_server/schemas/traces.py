"""Pydantic schemas for trace ingestion and query responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

VALID_KINDS = {"llm", "tool", "chain", "retriever", "agent", "custom"}
VALID_STATUSES = {"ok", "error", "unset"}


class SpanIngest(BaseModel):
    """Schema for a single span in an ingestion request."""

    span_id: str = Field(..., min_length=1, max_length=128)
    trace_id: str = Field(default="", max_length=128)
    parent_span_id: str | None = Field(default=None, max_length=128)
    name: str = Field(default="", max_length=512)
    kind: str = Field(default="custom", max_length=32)
    status: str = Field(default="unset", max_length=32)
    input: dict[str, Any] | None = None
    output: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    events: list[dict[str, Any]] = Field(default_factory=list)
    start_time: datetime | None = None
    end_time: datetime | None = None

    @field_validator("kind")
    @classmethod
    def validate_kind(cls, v: str) -> str:
        """Ensure kind is a recognised value."""
        if v not in VALID_KINDS:
            raise ValueError(f"kind must be one of {VALID_KINDS}, got '{v}'")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Ensure status is a recognised value."""
        if v not in VALID_STATUSES:
            raise ValueError(f"status must be one of {VALID_STATUSES}, got '{v}'")
        return v


class IngestRequest(BaseModel):
    """Schema for the span ingestion endpoint request body."""

    spans: list[SpanIngest] = Field(..., min_length=1)
    project_id: str = ""
    trace_name: str = ""
    trace_metadata: dict[str, Any] = Field(default_factory=dict)
    external_id: str | None = None


class IngestResponse(BaseModel):
    """Schema for the span ingestion endpoint response."""

    trace_id: str
    span_count: int


class SpanResponse(BaseModel):
    """Schema for a span in API responses."""

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


class TraceResponse(BaseModel):
    """Schema for a trace in API responses."""

    id: str
    project_id: str
    name: str
    status: str
    external_id: str | None = None
    metadata: dict[str, Any]
    start_time: datetime | None
    end_time: datetime | None
    created_at: datetime
    span_count: int = 0
    spans: list[SpanResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class TraceListResponse(BaseModel):
    """Paginated trace list response."""

    traces: list[TraceResponse]
    total: int
    offset: int
    limit: int


class EventAppendRequest(BaseModel):
    """Schema for appending an event to a trace's span."""

    name: str = Field(..., min_length=1, max_length=256)
    attributes: dict[str, Any] = Field(default_factory=dict)


class TraceUpdateRequest(BaseModel):
    """Schema for updating a trace."""

    status: str | None = None
    metadata: dict[str, Any] | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_STATUSES:
            raise ValueError(f"status must be one of {VALID_STATUSES}, got '{v}'")
        return v

"""Core Vigil types for traces, spans, and events."""

from __future__ import annotations

import enum
import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class SpanKind(enum.StrEnum):
    LLM = "llm"
    TOOL = "tool"
    CHAIN = "chain"
    RETRIEVER = "retriever"
    AGENT = "agent"
    CUSTOM = "custom"


class SpanStatus(enum.StrEnum):
    OK = "ok"
    ERROR = "error"
    UNSET = "unset"


class Event(BaseModel):
    name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    attributes: dict[str, Any] = Field(default_factory=dict)


class Span(BaseModel):
    span_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    trace_id: str = ""
    parent_span_id: str | None = None
    name: str = ""
    kind: SpanKind = SpanKind.CUSTOM
    status: SpanStatus = SpanStatus.UNSET
    input: dict[str, Any] | None = None
    output: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    events: list[Event] = Field(default_factory=list)
    start_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    end_time: datetime | None = None

    def end(self, status: SpanStatus = SpanStatus.OK) -> None:
        self.end_time = datetime.now(UTC)
        self.status = status

    def add_event(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        self.events.append(Event(name=name, attributes=attributes or {}))

    def set_input(self, data: dict[str, Any]) -> None:
        self.input = data

    def set_output(self, data: dict[str, Any]) -> None:
        self.output = data


class Trace(BaseModel):
    trace_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    name: str = ""
    project_id: str = ""
    status: str = "unset"
    metadata: dict[str, Any] = Field(default_factory=dict)
    spans: list[Span] = Field(default_factory=list)
    start_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    end_time: datetime | None = None

    def end(self) -> None:
        self.end_time = datetime.now(UTC)

"""ReplayRun model for persisting replay executions."""

from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from vigil_server.models.base import Base, TimestampMixin, UUIDMixin


class ReplayRun(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "replay_runs"

    original_trace_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("traces.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(32), default="pending")
    created_by: Mapped[str | None] = mapped_column(String(320), nullable=True)
    config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=True)
    result_trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # New columns for real replay execution
    estimated_cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    llm_spans_count: Mapped[int] = mapped_column(Integer, default=0)
    project_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

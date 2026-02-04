"""ReplayRun model for persisting replay executions."""

from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, ForeignKey, String
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

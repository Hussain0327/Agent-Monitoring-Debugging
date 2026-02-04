"""Span model."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vigil_server.models.base import Base, TimestampMixin, UUIDMixin


class Span(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "spans"

    trace_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("traces.id", ondelete="CASCADE"), index=True
    )
    parent_span_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(256), default="")
    kind: Mapped[str] = mapped_column(String(32), default="custom", index=True)
    status: Mapped[str] = mapped_column(String(32), default="unset", index=True)
    input: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    output: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=True)
    events: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=True)
    start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    trace: Mapped[Trace] = relationship(back_populates="spans")  # noqa: F821

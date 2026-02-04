"""Trace model."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vigil_server.models.base import Base, TimestampMixin, UUIDMixin


class Trace(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "traces"

    project_id: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(256), default="")
    status: Mapped[str] = mapped_column(String(32), default="unset")
    external_id: Mapped[str | None] = mapped_column(
        String(256), unique=True, index=True, nullable=True
    )
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=True)
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    spans: Mapped[list[Span]] = relationship(  # noqa: F821
        back_populates="trace",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

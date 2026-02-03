"""Drift alert model."""

from __future__ import annotations

from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from vigil_server.models.base import Base, TimestampMixin, UUIDMixin


class DriftAlert(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "drift_alerts"

    project_id: Mapped[str] = mapped_column(String(64), index=True)
    span_kind: Mapped[str] = mapped_column(String(32))
    metric_name: Mapped[str] = mapped_column(String(128))
    baseline_value: Mapped[float] = mapped_column(Float)
    current_value: Mapped[float] = mapped_column(Float)
    psi_score: Mapped[float] = mapped_column(Float)
    severity: Mapped[str] = mapped_column(String(32), default="low", index=True)
    resolved: Mapped[bool] = mapped_column(default=False, index=True)

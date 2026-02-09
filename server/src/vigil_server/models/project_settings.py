"""Project settings model for storing per-project configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vigil_server.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from vigil_server.models.project import Project


class ProjectSettings(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "project_settings"

    project_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("projects.id", ondelete="CASCADE"), unique=True, index=True
    )

    # Encrypted LLM API keys
    openai_api_key_encrypted: Mapped[str | None] = mapped_column(String(512), nullable=True)
    anthropic_api_key_encrypted: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Default models
    default_openai_model: Mapped[str] = mapped_column(String(128), default="gpt-4o")
    default_anthropic_model: Mapped[str] = mapped_column(
        String(128), default="claude-sonnet-4-5-20250929"
    )

    # Drift detection settings
    drift_check_interval_minutes: Mapped[int] = mapped_column(Integer, default=60)
    drift_check_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    project: Mapped[Project] = relationship(back_populates="settings")

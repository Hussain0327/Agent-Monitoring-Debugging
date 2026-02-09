"""Project and API key models."""

from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vigil_server.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from vigil_server.models.project_settings import ProjectSettings


def _generate_api_key() -> str:
    return f"vgl_{secrets.token_urlsafe(32)}"


class Project(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(String(1024), default="")

    api_keys: Mapped[list[APIKey]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    settings: Mapped[ProjectSettings | None] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )


class APIKey(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "api_keys"

    project_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    key: Mapped[str] = mapped_column(String(256), unique=True, default=_generate_api_key)
    name: Mapped[str] = mapped_column(String(128), default="default")
    is_active: Mapped[bool] = mapped_column(default=True)

    project: Mapped[Project] = relationship(back_populates="api_keys")

"""Async SQLAlchemy engine and session factory."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from vigil_server.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.log_level == "debug",
    future=True,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

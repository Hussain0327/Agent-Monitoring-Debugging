"""Async test fixtures with in-memory SQLite."""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from vigil_server.models import Base
from vigil_server.dependencies import get_db, get_current_project, get_optional_project
from vigil_server.main import app


@pytest_asyncio.fixture
async def db_engine():
    """Create an in-memory SQLite engine for tests."""
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """Provide a transactional database session for tests."""
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        async with session.begin():
            yield session


@pytest_asyncio.fixture
async def client(db_session):
    """HTTP test client with dependency overrides."""

    async def override_get_db():
        yield db_session

    async def override_get_project():
        return "test-project"

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_project] = override_get_project
    app.dependency_overrides[get_optional_project] = override_get_project

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

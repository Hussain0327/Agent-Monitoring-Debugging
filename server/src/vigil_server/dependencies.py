"""FastAPI dependency injection."""

from __future__ import annotations

from typing import Annotated, AsyncGenerator

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from vigil_server.config import settings
from vigil_server.db.session import async_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session."""
    async with async_session() as session:
        async with session.begin():
            yield session


async def get_current_project(
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> str:
    """Extract project_id from API key in Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )

    api_key = authorization.removeprefix("Bearer ").strip()

    # Dev key returns default project
    if api_key == settings.api_key:
        return "default"

    # Look up in database
    from sqlalchemy import select

    from vigil_server.models.project import APIKey

    stmt = select(APIKey).where(APIKey.key == api_key, APIKey.is_active == True)  # noqa: E712
    result = await db.execute(stmt)
    key_record = result.scalar_one_or_none()

    if not key_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return key_record.project_id


DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentProject = Annotated[str, Depends(get_current_project)]

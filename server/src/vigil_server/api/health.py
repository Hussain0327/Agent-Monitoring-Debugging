"""Health and readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter, status
from sqlalchemy import text

from vigil_server.db.session import async_session

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready", status_code=status.HTTP_200_OK)
async def ready() -> dict[str, str]:
    """Readiness check — verifies database connectivity."""
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as exc:
        return {"status": "not_ready", "detail": str(exc)}

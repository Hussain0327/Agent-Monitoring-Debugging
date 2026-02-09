"""FastAPI application factory with lifespan management."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from vigil_server.api.router import api_router
from vigil_server.config import settings
from vigil_server.db.session import engine
from vigil_server.exceptions import register_error_handlers
from vigil_server.logging_config import configure_logging
from vigil_server.middleware.rate_limit import RateLimitMiddleware
from vigil_server.middleware.request_id import RequestIDMiddleware

logger = logging.getLogger("vigil_server")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle: DB pool, Redis connection."""
    configure_logging(settings.log_level)
    logger.info("Starting Vigil server...")

    # For SQLite dev mode, create tables automatically
    if settings.is_sqlite:
        from vigil_server.models import Base

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("SQLite tables created")

    # Crash recovery: mark any "running" replays as "failed"
    await _recover_stuck_replays()

    # Start drift scheduler
    from vigil_server.services.scheduler import drift_scheduler

    await drift_scheduler.start()

    yield

    # Cleanup
    await drift_scheduler.stop()
    await engine.dispose()
    logger.info("Vigil server shut down")


async def _recover_stuck_replays() -> None:
    """Set any replays stuck in 'running' or 'confirmed' status to 'failed'."""
    from sqlalchemy import update

    from vigil_server.db.session import async_session
    from vigil_server.models.replay import ReplayRun

    try:
        async with async_session() as session, session.begin():
            stmt = (
                update(ReplayRun)
                .where(ReplayRun.status.in_(["running", "confirmed"]))
                .values(status="failed", error_message="Server restarted during execution")
            )
            result = await session.execute(stmt)
            if result.rowcount:
                logger.warning("Recovered %d stuck replay runs on startup", result.rowcount)
    except Exception:
        logger.exception("Failed to recover stuck replays on startup")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Vigil",
        description="Observability server for AI agent pipelines",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Error handlers
    register_error_handlers(app)

    # Middleware (order matters — outermost first)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )

    # Routes
    app.include_router(api_router)

    return app


app = create_app()

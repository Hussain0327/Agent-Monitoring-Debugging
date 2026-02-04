"""Trace ingestion and query service."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from vigil_server.exceptions import NotFoundError, VigilError
from vigil_server.models.span import Span as SpanModel
from vigil_server.models.trace import Trace as TraceModel

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession
from vigil_server.schemas.traces import IngestRequest, SpanResponse, TraceResponse

logger = logging.getLogger("vigil_server.services.trace")


async def ingest_spans(
    session: AsyncSession,
    request: IngestRequest,
    project_id: str,
) -> tuple[str, int]:
    """Ingest a batch of spans, creating or updating the parent trace."""
    # Determine trace_id from first span or generate new
    trace_id = (
        request.spans[0].trace_id
        if request.spans and request.spans[0].trace_id
        else uuid.uuid4().hex
    )

    try:
        # Upsert trace
        existing = await session.get(TraceModel, trace_id)
        if not existing:
            trace = TraceModel(
                id=trace_id,
                project_id=project_id or request.project_id or "default",
                name=request.trace_name,
                metadata_=request.trace_metadata,
                external_id=request.external_id,
            )
            session.add(trace)
        else:
            if request.trace_name:
                existing.name = request.trace_name

        # Insert spans
        for span_data in request.spans:
            span = SpanModel(
                id=span_data.span_id,
                trace_id=trace_id,
                parent_span_id=span_data.parent_span_id,
                name=span_data.name,
                kind=span_data.kind,
                status=span_data.status,
                input=span_data.input,
                output=span_data.output,
                metadata_=span_data.metadata,
                events=span_data.events,
                start_time=span_data.start_time,
                end_time=span_data.end_time,
            )
            session.add(span)

        await session.flush()
        logger.debug("Ingested %d spans for trace %s", len(request.spans), trace_id)
        return trace_id, len(request.spans)

    except SQLAlchemyError as exc:
        logger.exception("Database error during span ingestion for trace %s", trace_id)
        raise VigilError("Failed to ingest spans", status_code=500) from exc


async def get_trace(session: AsyncSession, trace_id: str) -> TraceModel | None:
    """Fetch a trace with all its spans."""
    try:
        return await session.get(TraceModel, trace_id)
    except SQLAlchemyError as exc:
        logger.exception("Database error fetching trace %s", trace_id)
        raise VigilError("Failed to fetch trace", status_code=500) from exc


async def list_traces(
    session: AsyncSession,
    project_id: str | None = None,
    offset: int = 0,
    limit: int = 50,
    status: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> tuple[Sequence[TraceModel], int]:
    """List traces with pagination and optional filters."""
    try:
        stmt = select(TraceModel).order_by(TraceModel.created_at.desc())
        count_stmt = select(func.count()).select_from(TraceModel)

        if project_id:
            stmt = stmt.where(TraceModel.project_id == project_id)
            count_stmt = count_stmt.where(TraceModel.project_id == project_id)

        if status:
            stmt = stmt.where(TraceModel.status == status)
            count_stmt = count_stmt.where(TraceModel.status == status)

        if start_date:
            stmt = stmt.where(TraceModel.created_at >= start_date)
            count_stmt = count_stmt.where(TraceModel.created_at >= start_date)

        if end_date:
            stmt = stmt.where(TraceModel.created_at <= end_date)
            count_stmt = count_stmt.where(TraceModel.created_at <= end_date)

        total_result = await session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = stmt.offset(offset).limit(limit)
        result = await session.execute(stmt)
        traces = result.scalars().all()

        return traces, total

    except SQLAlchemyError as exc:
        logger.exception("Database error listing traces")
        raise VigilError("Failed to list traces", status_code=500) from exc


async def append_event(
    session: AsyncSession,
    trace_id: str,
    span_id: str,
    event_name: str,
    attributes: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Append an event to a specific span within a trace."""
    try:
        trace = await session.get(TraceModel, trace_id)
        if not trace:
            raise NotFoundError("Trace", trace_id)

        target_span = None
        for s in trace.spans:
            if s.id == span_id:
                target_span = s
                break

        if not target_span:
            raise NotFoundError("Span", span_id)

        event = {
            "name": event_name,
            "timestamp": datetime.now().isoformat(),
            "attributes": attributes or {},
        }
        current_events = list(target_span.events or [])
        current_events.append(event)
        target_span.events = current_events
        await session.flush()
        return event

    except SQLAlchemyError as exc:
        logger.exception("Database error appending event to trace %s", trace_id)
        raise VigilError("Failed to append event", status_code=500) from exc


async def update_trace(
    session: AsyncSession,
    trace_id: str,
    status: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> TraceModel:
    """Update a trace's status and/or metadata."""
    try:
        trace = await session.get(TraceModel, trace_id)
        if not trace:
            raise NotFoundError("Trace", trace_id)

        if status is not None:
            trace.status = status
        if metadata is not None:
            current = dict(trace.metadata_ or {})
            current.update(metadata)
            trace.metadata_ = current

        await session.flush()
        return trace

    except SQLAlchemyError as exc:
        logger.exception("Database error updating trace %s", trace_id)
        raise VigilError("Failed to update trace", status_code=500) from exc


def build_trace_response(trace: TraceModel) -> TraceResponse:
    """Convert a trace model to response schema."""
    spans = [
        SpanResponse(
            id=s.id,
            trace_id=s.trace_id,
            parent_span_id=s.parent_span_id,
            name=s.name,
            kind=s.kind,
            status=s.status,
            input=s.input,
            output=s.output,
            metadata=s.metadata_ or {},
            events=s.events or [],
            start_time=s.start_time,
            end_time=s.end_time,
            created_at=s.created_at,
        )
        for s in trace.spans
    ]
    return TraceResponse(
        id=trace.id,
        project_id=trace.project_id,
        name=trace.name,
        status=trace.status,
        external_id=trace.external_id,
        metadata=trace.metadata_ or {},
        start_time=trace.start_time,
        end_time=trace.end_time,
        created_at=trace.created_at,
        span_count=len(spans),
        spans=spans,
    )

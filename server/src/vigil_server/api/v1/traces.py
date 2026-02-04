"""Trace ingestion and query endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status

from vigil_server.dependencies import CurrentProject, DBSession  # noqa: TC001
from vigil_server.schemas.traces import (
    EventAppendRequest,
    IngestRequest,
    IngestResponse,
    TraceListResponse,
    TraceResponse,
    TraceUpdateRequest,
)
from vigil_server.services.trace_service import (
    append_event,
    build_trace_response,
    get_trace,
    ingest_spans,
    list_traces,
    update_trace,
)

router = APIRouter(prefix="/traces", tags=["traces"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def ingest(
    request: IngestRequest,
    db: DBSession,
    project_id: CurrentProject,
) -> IngestResponse:
    """Ingest spans from the SDK."""
    trace_id, count = await ingest_spans(db, request, project_id)
    return IngestResponse(trace_id=trace_id, span_count=count)


@router.get("")
async def list_all(
    db: DBSession,
    project_id: CurrentProject,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: str | None = Query(None, alias="status"),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
) -> TraceListResponse:
    """List traces with pagination and optional filters."""
    traces, total = await list_traces(
        db,
        project_id,
        offset,
        limit,
        status=status_filter,
        start_date=start_date,
        end_date=end_date,
    )
    return TraceListResponse(
        traces=[build_trace_response(t) for t in traces],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{trace_id}")
async def get_one(
    trace_id: str,
    db: DBSession,
    project_id: CurrentProject,
) -> TraceResponse:
    """Get a single trace with all spans."""
    trace = await get_trace(db, trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return build_trace_response(trace)


@router.patch("/{trace_id}")
async def patch_trace(
    trace_id: str,
    body: TraceUpdateRequest,
    db: DBSession,
    _auth: CurrentProject,
) -> TraceResponse:
    """Update a trace's status and/or metadata."""
    trace = await update_trace(db, trace_id, status=body.status, metadata=body.metadata)
    return build_trace_response(trace)


@router.post("/{trace_id}/events/{span_id}", status_code=status.HTTP_201_CREATED)
async def add_event(
    trace_id: str,
    span_id: str,
    body: EventAppendRequest,
    db: DBSession,
    _auth: CurrentProject,
) -> dict:
    """Append an event to a span within a trace."""
    event = await append_event(db, trace_id, span_id, body.name, body.attributes)
    return event

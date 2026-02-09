"""Trace replay engine: estimate, confirm, execute with real LLM calls."""

from __future__ import annotations

import asyncio
import copy
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from vigil_server.exceptions import NotFoundError, VigilError
from vigil_server.models.replay import ReplayRun
from vigil_server.models.span import Span as SpanModel
from vigil_server.models.trace import Trace as TraceModel
from vigil_server.schemas.replay import ReplayDiffResponse
from vigil_server.services.llm_executor import detect_provider, estimate_cost, execute_llm_call

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("vigil_server.services.replay")


class ReplayResult:
    """Container for replay output including mutations and diffs."""

    def __init__(
        self,
        original_trace_id: str,
        mutations: dict[str, Any],
        diffs: list[dict[str, Any]],
        replay_run_id: str | None = None,
    ) -> None:
        self.original_trace_id = original_trace_id
        self.mutations = mutations
        self.diffs = diffs
        self.replay_run_id = replay_run_id

    def to_dict(self) -> dict[str, Any]:
        """Serialise the replay result to a dictionary."""
        result: dict[str, Any] = {
            "original_trace_id": self.original_trace_id,
            "mutations": self.mutations,
            "diffs": self.diffs,
        }
        if self.replay_run_id:
            result["replay_run_id"] = self.replay_run_id
        return result


async def create_replay_estimate(
    session: AsyncSession,
    trace_id: str,
    mutations: dict[str, Any] | None = None,
    project_id: str | None = None,
) -> dict[str, Any]:
    """Create a replay estimate: count LLM spans, estimate cost, return ReplayRun.

    Returns a dict with replay_run_id, estimated_cost_usd, llm_spans_count, etc.
    """
    try:
        trace = await session.get(TraceModel, trace_id, options=[selectinload(TraceModel.spans)])
    except SQLAlchemyError as exc:
        logger.exception("Database error loading trace %s for replay", trace_id)
        raise VigilError("Failed to load trace for replay", status_code=500) from exc

    if not trace:
        raise NotFoundError("Trace", trace_id)

    mutations = mutations or {}
    llm_spans = []
    total_cost = 0.0

    for span in trace.spans:
        provider = detect_provider(span.input, span.name)
        if provider and span.kind == "llm":
            effective_input = span.input or {}
            if span.id in mutations:
                effective_input = {**effective_input, **mutations[span.id]}
            cost = estimate_cost(effective_input, provider)
            total_cost += cost
            llm_spans.append(
                {
                    "span_id": span.id,
                    "span_name": span.name,
                    "provider": provider,
                    "estimated_cost_usd": cost,
                }
            )

    replay_run = ReplayRun(
        original_trace_id=trace_id,
        status="estimating",
        config={"mutations": mutations},
        estimated_cost_usd=total_cost,
        llm_spans_count=len(llm_spans),
        project_id=project_id,
    )
    session.add(replay_run)
    await session.flush()

    return {
        "replay_run_id": replay_run.id,
        "original_trace_id": trace_id,
        "status": "estimating",
        "estimated_cost_usd": total_cost,
        "llm_spans_count": len(llm_spans),
        "llm_spans": llm_spans,
    }


async def confirm_replay(
    session: AsyncSession,
    replay_id: str,
    get_api_key: Any = None,
) -> ReplayRun:
    """Confirm a replay and spawn background execution.

    get_api_key should be an async callable(provider: str) -> str that returns the API key.
    """
    run = await session.get(ReplayRun, replay_id)
    if not run:
        raise NotFoundError("ReplayRun", replay_id)
    if run.status != "estimating":
        raise VigilError(f"Replay {replay_id} is in status '{run.status}', expected 'estimating'")

    run.status = "confirmed"
    await session.flush()

    # Spawn background execution
    asyncio.create_task(
        _execute_replay_background(
            replay_id=run.id,
            trace_id=run.original_trace_id,
            mutations=run.config.get("mutations", {}),
            project_id=run.project_id,
            get_api_key=get_api_key,
        )
    )

    return run


async def cancel_replay(session: AsyncSession, replay_id: str) -> ReplayRun:
    """Cancel a replay that is still in estimating status."""
    run = await session.get(ReplayRun, replay_id)
    if not run:
        raise NotFoundError("ReplayRun", replay_id)
    if run.status not in ("estimating", "confirmed"):
        raise VigilError(f"Cannot cancel replay in status '{run.status}'")

    run.status = "cancelled"
    await session.flush()
    return run


async def _execute_replay_background(
    replay_id: str,
    trace_id: str,
    mutations: dict[str, Any],
    project_id: str | None,
    get_api_key: Any = None,
) -> None:
    """Background coroutine that executes a replay.

    Creates a result Trace, iterates spans topologically, calls LLMs
    for LLM spans, copies non-LLM spans, updates ReplayRun.
    """
    from vigil_server.db.session import async_session
    from vigil_server.services.notification_service import create_notification
    from vigil_server.services.websocket_manager import manager

    async with async_session() as session, session.begin():
        run = await session.get(ReplayRun, replay_id)
        if not run:
            return
        run.status = "running"
        await session.flush()

        # Broadcast replay started
        if project_id:
            await manager.broadcast(
                project_id,
                {
                    "type": "replay.status",
                    "data": {"replay_id": replay_id, "status": "running"},
                },
            )

    try:
        async with async_session() as session, session.begin():
            trace = await session.get(TraceModel, trace_id)
            if not trace:
                raise ValueError(f"Trace {trace_id} not found")

            # Create result trace
            result_trace = TraceModel(
                project_id=trace.project_id,
                name=f"Replay of {trace.name}",
                status="ok",
                metadata={"replay_of": trace_id, "replay_run_id": replay_id},
                start_time=datetime.now(UTC),
            )
            session.add(result_trace)
            await session.flush()

            diffs: list[dict[str, Any]] = []
            actual_cost = 0.0

            # Sort spans topologically (parents first)
            sorted_spans = _topological_sort(list(trace.spans))

            for span in sorted_spans:
                original_input = copy.deepcopy(span.input) or {}
                effective_input = original_input
                if span.id in mutations:
                    effective_input = {**original_input, **mutations[span.id]}

                provider = detect_provider(span.input, span.name)
                is_llm = provider is not None and span.kind == "llm"

                new_output = None
                was_executed = False

                if is_llm and get_api_key:
                    try:
                        api_key = await get_api_key(provider)
                        if api_key:
                            result = await execute_llm_call(effective_input, provider, api_key)
                            new_output = result
                            was_executed = True
                            actual_cost += estimate_cost(effective_input, provider)
                    except Exception:
                        logger.exception("LLM call failed for span %s", span.id)
                        new_output = {"error": "LLM call failed"}
                        was_executed = True

                # Create result span
                result_span = SpanModel(
                    trace_id=result_trace.id,
                    parent_span_id=span.parent_span_id,
                    name=span.name,
                    kind=span.kind,
                    status=span.status,
                    input=effective_input,
                    output=new_output if was_executed else span.output,
                    metadata={**(span.metadata or {}), "replay_source_span_id": span.id},
                    events=span.events,
                    start_time=datetime.now(UTC),
                    end_time=datetime.now(UTC),
                )
                session.add(result_span)

                diff_entry: dict[str, Any] = {
                    "span_id": span.id,
                    "span_name": span.name,
                    "original_input": original_input,
                    "mutated_input": effective_input,
                    "original_output": span.output,
                    "new_output": new_output,
                    "was_executed": was_executed,
                }
                if not was_executed:
                    diff_entry["note"] = "Copied (not re-executed)"
                diffs.append(diff_entry)

            result_trace.end_time = datetime.now(UTC)
            await session.flush()

            # Update the replay run
            run = await session.get(ReplayRun, replay_id)
            if run:
                run.status = "completed"
                run.result_trace_id = result_trace.id
                run.actual_cost_usd = actual_cost
                run.config = {**run.config, "diffs": diffs}
                await session.flush()

            # Create completion notification
            if project_id:
                await create_notification(
                    session,
                    project_id=project_id,
                    type="replay_complete",
                    title=f"Replay completed for trace {trace.name}",
                    body=f"Result trace: {result_trace.id}",
                    reference_id=replay_id,
                )

        # Broadcast completion
        if project_id:
            await manager.broadcast(
                project_id,
                {
                    "type": "replay.status",
                    "data": {
                        "replay_id": replay_id,
                        "status": "completed",
                        "result_trace_id": result_trace.id,
                    },
                },
            )

    except Exception:
        logger.exception("Replay execution failed for run %s", replay_id)
        async with async_session() as session, session.begin():
            run = await session.get(ReplayRun, replay_id)
            if run:
                run.status = "failed"
                run.error_message = "Execution failed — see server logs"
                await session.flush()

            if project_id:
                await create_notification(
                    session,
                    project_id=project_id,
                    type="replay_failed",
                    title="Replay failed",
                    body=f"Replay {replay_id} failed during execution",
                    reference_id=replay_id,
                )

        if project_id:
            await manager.broadcast(
                project_id,
                {
                    "type": "replay.status",
                    "data": {"replay_id": replay_id, "status": "failed"},
                },
            )


def _topological_sort(spans: list[SpanModel]) -> list[SpanModel]:
    """Sort spans so parents come before children."""
    by_id = {s.id: s for s in spans}
    visited: set[str] = set()
    result: list[SpanModel] = []

    def visit(span_id: str) -> None:
        if span_id in visited:
            return
        visited.add(span_id)
        span = by_id.get(span_id)
        if span and span.parent_span_id and span.parent_span_id in by_id:
            visit(span.parent_span_id)
        if span:
            result.append(span)

    for s in spans:
        visit(s.id)

    return result


# --- Legacy API (kept for backward compatibility) ---


async def replay_trace(
    session: AsyncSession,
    trace_id: str,
    mutations: dict[str, Any] | None = None,
) -> ReplayResult:
    """Load a trace, apply mutations to span inputs, and compute output diffs.

    This is the original replay (no real LLM execution). Kept for backward compat.
    """
    try:
        trace = await session.get(TraceModel, trace_id, options=[selectinload(TraceModel.spans)])
    except SQLAlchemyError as exc:
        logger.exception("Database error loading trace %s for replay", trace_id)
        raise VigilError("Failed to load trace for replay", status_code=500) from exc

    if not trace:
        raise NotFoundError("Trace", trace_id)

    mutations = mutations or {}
    diffs: list[dict[str, Any]] = []

    for span in trace.spans:
        if span.id in mutations:
            original_input = copy.deepcopy(span.input) or {}
            mutated_input = {**original_input, **mutations[span.id]}
            diffs.append(
                {
                    "span_id": span.id,
                    "span_name": span.name,
                    "original_input": original_input,
                    "mutated_input": mutated_input,
                    "original_output": span.output,
                    "note": "Replay would re-execute this span with mutated input",
                }
            )

    # Persist replay run
    replay_run = ReplayRun(
        original_trace_id=trace_id,
        status="completed",
        config={"mutations": mutations, "diffs": diffs},
    )
    session.add(replay_run)
    await session.flush()

    logger.debug(
        "Replayed trace %s with %d mutations (run=%s)", trace_id, len(mutations), replay_run.id
    )
    return ReplayResult(
        original_trace_id=trace_id,
        mutations=mutations,
        diffs=diffs,
        replay_run_id=replay_run.id,
    )


async def get_replay_run(session: AsyncSession, replay_id: str) -> ReplayRun | None:
    """Fetch a replay run by ID."""
    try:
        return await session.get(ReplayRun, replay_id)
    except SQLAlchemyError as exc:
        logger.exception("Database error fetching replay run %s", replay_id)
        raise VigilError("Failed to fetch replay run", status_code=500) from exc


async def get_replay_diff(
    session: AsyncSession, trace_id: str, replay_id: str
) -> ReplayDiffResponse | None:
    """Fetch the diff from a completed replay run."""
    run = await get_replay_run(session, replay_id)
    if not run or run.original_trace_id != trace_id:
        return None

    config = run.config or {}
    return ReplayDiffResponse(
        original_trace_id=run.original_trace_id,
        mutations=config.get("mutations", {}),
        diffs=config.get("diffs", []),
    )

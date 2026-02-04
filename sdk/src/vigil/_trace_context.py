"""Trace context manager for automatic trace lifecycle management.

Supports both sync (``with``) and async (``async with``) usage::

    async with TraceContext(client, "my-trace") as trace:
        ...  # trace is active here

    with TraceContext(client, "my-trace") as trace:
        ...  # trace is active here
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from vigil._client import VigilClient
    from vigil._types import Trace


class TraceContext:
    """Context manager that wraps a trace lifecycle.

    On entry, creates a new trace.  On exit, ends the trace with
    ``success=True`` (normal) or ``success=False`` (if an exception
    propagated).
    """

    def __init__(
        self,
        client: VigilClient,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._client = client
        self._name = name
        self._metadata = metadata
        self._trace: Trace | None = None

    # -- sync context manager ------------------------------------------------

    def __enter__(self) -> Trace:
        self._trace = self._client.start_trace(self._name, metadata=self._metadata)
        return self._trace

    def __exit__(self, exc_type: type | None, exc_val: BaseException | None, exc_tb: Any) -> None:
        self._client.end_trace(self._trace, success=exc_type is None)
        return None  # Don't suppress exceptions

    # -- async context manager -----------------------------------------------

    async def __aenter__(self) -> Trace:
        self._trace = self._client.start_trace(self._name, metadata=self._metadata)
        return self._trace

    async def __aexit__(
        self, exc_type: type | None, exc_val: BaseException | None, exc_tb: Any
    ) -> None:
        self._client.end_trace(self._trace, success=exc_type is None)
        return None  # Don't suppress exceptions

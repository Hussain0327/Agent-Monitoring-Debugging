"""Anthropic monkey-patch instrumentation.

Patches ``Messages.create`` and ``AsyncMessages.create`` to capture LLM
spans with input/output data.  Sync patches use the thread-safe
``end_span_sync`` to avoid event-loop conflicts.
"""

from __future__ import annotations

import functools
import logging
from typing import Any

from vigil._client import get_client
from vigil._types import SpanKind, SpanStatus
from vigil.integrations import register

logger = logging.getLogger("vigil.integrations.anthropic")

_original_create: Any = None
_original_acreate: Any = None


def _extract_input(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Extract relevant input fields from an Anthropic messages request."""
    return {
        "model": kwargs.get("model", ""),
        "messages": kwargs.get("messages", []),
        "max_tokens": kwargs.get("max_tokens"),
        "system": kwargs.get("system"),
    }


def _extract_output(response: Any) -> dict[str, Any]:
    """Extract relevant output fields from an Anthropic messages response."""
    try:
        return {
            "model": response.model,
            "content": [block.text for block in response.content if hasattr(block, "text")],
            "role": response.role,
            "stop_reason": response.stop_reason,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        }
    except (AttributeError, IndexError):
        return {"raw": str(response)}


def _patch() -> None:
    """Monkey-patch Anthropic's Messages.create and AsyncMessages.create."""
    global _original_create, _original_acreate

    try:
        from anthropic.resources.messages import Messages
    except ImportError:
        logger.debug("anthropic not installed, skipping integration")
        return

    _original_create = Messages.create

    @functools.wraps(_original_create)
    def patched_create(self: Any, *args: Any, **kwargs: Any) -> Any:
        client = get_client()
        if not client:
            return _original_create(self, *args, **kwargs)

        span = client.start_span("anthropic.messages", kind=SpanKind.LLM)
        span.set_input(_extract_input(kwargs))
        try:
            response = _original_create(self, *args, **kwargs)
            span.set_output(_extract_output(response))
            client.end_span_sync(span, status=SpanStatus.OK)
            return response
        except Exception as exc:
            span.set_output({"error": str(exc)})
            client.end_span_sync(span, status=SpanStatus.ERROR)
            raise

    Messages.create = patched_create  # type: ignore[method-assign]

    # Patch async variant
    try:
        from anthropic.resources.messages import AsyncMessages

        _original_acreate = AsyncMessages.create

        @functools.wraps(_original_acreate)
        async def patched_acreate(self: Any, *args: Any, **kwargs: Any) -> Any:
            client = get_client()
            if not client:
                return await _original_acreate(self, *args, **kwargs)

            span = client.start_span("anthropic.messages", kind=SpanKind.LLM)
            span.set_input(_extract_input(kwargs))
            try:
                response = await _original_acreate(self, *args, **kwargs)
                span.set_output(_extract_output(response))
                await client.end_span(span, status=SpanStatus.OK)
                return response
            except Exception as exc:
                span.set_output({"error": str(exc)})
                await client.end_span(span, status=SpanStatus.ERROR)
                raise

        AsyncMessages.create = patched_acreate  # type: ignore[method-assign]
    except ImportError:
        pass

    logger.info("Anthropic integration activated")


register("anthropic", _patch)

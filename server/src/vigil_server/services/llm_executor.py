"""LLM executor — raw httpx calls to OpenAI and Anthropic APIs.

Uses httpx directly (no provider SDKs) to avoid version conflicts
with SDK monkey-patching and keep the server lean.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger("vigil_server.services.llm_executor")

# Rough token estimation: ~4 chars per token
CHARS_PER_TOKEN = 4

# Cost per million tokens (approximate, as of 2024)
COST_PER_M_TOKENS = {
    "openai": {"input": 2.50, "output": 10.00},  # GPT-4o
    "anthropic": {"input": 3.00, "output": 15.00},  # Claude Sonnet
}


def detect_provider(span_input: dict[str, Any] | None, span_name: str = "") -> str | None:
    """Determine OpenAI vs Anthropic from span name or input structure.

    Returns 'openai', 'anthropic', or None if undetectable.
    """
    name_lower = (span_name or "").lower()

    # Check span name
    if any(k in name_lower for k in ("openai", "gpt", "chatgpt")):
        return "openai"
    if any(k in name_lower for k in ("anthropic", "claude")):
        return "anthropic"

    if not span_input:
        return None

    # Check input structure
    model = str(span_input.get("model", "")).lower()
    if model.startswith(("gpt", "o1", "o3")):
        return "openai"
    if model.startswith("claude"):
        return "anthropic"

    # Check for OpenAI-style messages
    if "messages" in span_input and isinstance(span_input.get("messages"), list):
        msgs = span_input["messages"]
        if msgs and isinstance(msgs[0], dict) and "role" in msgs[0]:
            return "openai"

    return None


def estimate_cost(span_input: dict[str, Any] | None, provider: str) -> float:
    """Rough cost estimation from message content (USD)."""
    if not span_input:
        return 0.0

    # Estimate input tokens from message content
    text = _extract_text(span_input)
    input_tokens = max(len(text) / CHARS_PER_TOKEN, 100)

    # Assume output is ~50% of input for estimation
    output_tokens = input_tokens * 0.5

    rates = COST_PER_M_TOKENS.get(provider, COST_PER_M_TOKENS["openai"])
    cost = (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000_000
    return round(cost, 6)


def _extract_text(data: dict[str, Any]) -> str:
    """Recursively extract text content from span input."""
    parts: list[str] = []

    if "messages" in data and isinstance(data["messages"], list):
        for msg in data["messages"]:
            if isinstance(msg, dict):
                content = msg.get("content", "")
                if isinstance(content, str):
                    parts.append(content)
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and "text" in item:
                            parts.append(item["text"])

    if "prompt" in data:
        parts.append(str(data["prompt"]))

    return " ".join(parts)


async def execute_llm_call(
    span_input: dict[str, Any],
    provider: str,
    api_key: str,
    model: str | None = None,
) -> dict[str, Any]:
    """Execute an LLM call and return the response.

    Makes raw HTTP calls to provider APIs.
    """
    if provider == "openai":
        return await _call_openai(span_input, api_key, model)
    elif provider == "anthropic":
        return await _call_anthropic(span_input, api_key, model)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


async def _call_openai(
    span_input: dict[str, Any], api_key: str, model: str | None
) -> dict[str, Any]:
    """Call OpenAI Chat Completions API."""
    payload: dict[str, Any] = {}

    # Use model from input or override
    payload["model"] = model or span_input.get("model", "gpt-4o")

    # Forward messages
    if "messages" in span_input:
        payload["messages"] = span_input["messages"]
    else:
        # Wrap raw content as user message
        payload["messages"] = [{"role": "user", "content": str(span_input)}]

    # Forward optional params
    for key in ("temperature", "max_tokens", "top_p", "stop"):
        if key in span_input:
            payload[key] = span_input[key]

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    return {
        "provider": "openai",
        "model": data.get("model"),
        "content": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
        "usage": data.get("usage", {}),
        "raw": data,
    }


async def _call_anthropic(
    span_input: dict[str, Any], api_key: str, model: str | None
) -> dict[str, Any]:
    """Call Anthropic Messages API."""
    payload: dict[str, Any] = {}

    payload["model"] = model or span_input.get("model", "claude-sonnet-4-5-20250929")
    payload["max_tokens"] = span_input.get("max_tokens", 4096)

    # Forward messages — convert from OpenAI format if needed
    if "messages" in span_input:
        messages = span_input["messages"]
        # Filter out system messages (Anthropic uses top-level system param)
        anthropic_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                if msg.get("role") == "system":
                    payload["system"] = msg.get("content", "")
                else:
                    anthropic_messages.append(msg)
        payload["messages"] = anthropic_messages or [{"role": "user", "content": str(span_input)}]
    else:
        payload["messages"] = [{"role": "user", "content": str(span_input)}]

    for key in ("temperature", "top_p", "stop_sequences"):
        if key in span_input:
            payload[key] = span_input[key]

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    content_parts = data.get("content", [])
    text = ""
    for part in content_parts:
        if isinstance(part, dict) and part.get("type") == "text":
            text += part.get("text", "")

    return {
        "provider": "anthropic",
        "model": data.get("model"),
        "content": text,
        "usage": data.get("usage", {}),
        "raw": data,
    }

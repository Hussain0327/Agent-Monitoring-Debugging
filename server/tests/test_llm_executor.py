"""Tests for LLM executor service."""

from __future__ import annotations

import pytest

from vigil_server.services.llm_executor import detect_provider, estimate_cost


class TestDetectProvider:
    def test_openai_from_name(self):
        assert detect_provider(None, "openai-chat") == "openai"
        assert detect_provider(None, "GPT-4 call") == "openai"

    def test_anthropic_from_name(self):
        assert detect_provider(None, "claude-chat") == "anthropic"
        assert detect_provider(None, "Anthropic API") == "anthropic"

    def test_openai_from_model(self):
        assert detect_provider({"model": "gpt-4o"}, "") == "openai"
        assert detect_provider({"model": "gpt-3.5-turbo"}, "") == "openai"

    def test_anthropic_from_model(self):
        assert detect_provider({"model": "claude-sonnet-4-5-20250929"}, "") == "anthropic"
        assert detect_provider({"model": "claude-3-opus-20240229"}, "") == "anthropic"

    def test_openai_from_messages_structure(self):
        inp = {"messages": [{"role": "user", "content": "hello"}]}
        assert detect_provider(inp, "") == "openai"

    def test_unknown_returns_none(self):
        assert detect_provider(None, "") is None
        assert detect_provider({}, "") is None
        assert detect_provider({"foo": "bar"}, "my-custom-tool") is None

    def test_empty_input(self):
        assert detect_provider(None, "") is None


class TestEstimateCost:
    def test_basic_estimation(self):
        inp = {"messages": [{"role": "user", "content": "Hello, world!"}]}
        cost = estimate_cost(inp, "openai")
        assert cost > 0
        assert cost < 0.01  # Should be very small for a short message

    def test_longer_message_costs_more(self):
        short = {"messages": [{"role": "user", "content": "Hi"}]}
        long = {"messages": [{"role": "user", "content": "x" * 10000}]}
        assert estimate_cost(long, "openai") > estimate_cost(short, "openai")

    def test_empty_input_returns_zero(self):
        assert estimate_cost(None, "openai") == 0.0
        assert estimate_cost({}, "openai") == 0.0

    def test_anthropic_cost(self):
        inp = {"messages": [{"role": "user", "content": "Hello"}]}
        cost = estimate_cost(inp, "anthropic")
        assert cost > 0

    def test_prompt_field(self):
        inp = {"prompt": "Tell me a joke about programming"}
        cost = estimate_cost(inp, "openai")
        assert cost > 0

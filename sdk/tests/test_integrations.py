"""Tests for integration registry and activation."""

from __future__ import annotations

from vigil.integrations import activate, activate_all, available, register


class TestIntegrationRegistry:
    def test_register_and_available(self):
        """Registering an integration makes it available."""
        activated = []
        register("test-lib", lambda: activated.append("test-lib"))
        assert "test-lib" in available()

    def test_activate_calls_function(self):
        """Activating a registered integration invokes its callback."""
        activated = []
        register("activate-test", lambda: activated.append("done"))
        activate("activate-test")
        assert activated == ["done"]

    def test_activate_unknown_does_nothing(self):
        """Activating an unknown integration does not raise."""
        activate("nonexistent-integration")  # should not raise

    def test_activate_all_invokes_all(self):
        """activate_all calls every registered integration."""
        count = {"value": 0}
        register("all-test-1", lambda: count.__setitem__("value", count["value"] + 1))
        register("all-test-2", lambda: count.__setitem__("value", count["value"] + 1))
        activate_all()
        assert count["value"] >= 2

    def test_builtin_integrations_registered(self):
        """OpenAI and Anthropic integrations should be auto-registered."""
        names = available()
        assert "openai" in names
        assert "anthropic" in names

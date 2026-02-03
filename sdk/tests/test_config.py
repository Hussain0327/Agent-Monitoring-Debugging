"""Tests for SDK configuration validation."""

from __future__ import annotations

import pytest

from vigil._config import SDKConfig


class TestConfigValidation:
    """Config validation rejects invalid values and accepts valid ones."""

    def test_defaults_are_valid(self):
        config = SDKConfig()
        assert config.endpoint == "http://localhost:8000"
        assert config.batch_size == 100
        assert config.enabled is True

    def test_empty_endpoint_rejected(self):
        with pytest.raises(ValueError, match="endpoint"):
            SDKConfig(endpoint="")

    def test_whitespace_endpoint_rejected(self):
        with pytest.raises(ValueError, match="endpoint"):
            SDKConfig(endpoint="   ")

    def test_batch_size_zero_rejected(self):
        with pytest.raises(ValueError, match="batch_size"):
            SDKConfig(batch_size=0)

    def test_batch_size_negative_rejected(self):
        with pytest.raises(ValueError, match="batch_size"):
            SDKConfig(batch_size=-1)

    def test_flush_interval_too_low_rejected(self):
        with pytest.raises(ValueError, match="flush_interval_ms"):
            SDKConfig(flush_interval_ms=5)

    def test_timeout_zero_rejected(self):
        with pytest.raises(ValueError, match="timeout_seconds"):
            SDKConfig(timeout_seconds=0)

    def test_timeout_negative_rejected(self):
        with pytest.raises(ValueError, match="timeout_seconds"):
            SDKConfig(timeout_seconds=-1.0)

    def test_valid_custom_config(self):
        config = SDKConfig(
            endpoint="https://vigil.example.com",
            api_key="my-key",
            project_id="proj-1",
            batch_size=50,
            flush_interval_ms=1000,
            timeout_seconds=30.0,
        )
        assert config.endpoint == "https://vigil.example.com"
        assert config.project_id == "proj-1"


class TestConfigProperties:
    """Derived properties compute correctly."""

    def test_ingest_url(self):
        config = SDKConfig(endpoint="http://localhost:8000")
        assert config.ingest_url == "http://localhost:8000/v1/traces"

    def test_ingest_url_strips_trailing_slash(self):
        config = SDKConfig(endpoint="http://localhost:8000/")
        assert config.ingest_url == "http://localhost:8000/v1/traces"

    def test_auth_headers_with_key(self):
        config = SDKConfig(api_key="test-key")
        headers = config.auth_headers
        assert headers["Authorization"] == "Bearer test-key"

    def test_auth_headers_without_key(self):
        config = SDKConfig(api_key="")
        headers = config.auth_headers
        assert "Authorization" not in headers

    def test_auth_headers_include_custom(self):
        config = SDKConfig(api_key="key", headers={"X-Custom": "val"})
        headers = config.auth_headers
        assert headers["X-Custom"] == "val"
        assert headers["Authorization"] == "Bearer key"

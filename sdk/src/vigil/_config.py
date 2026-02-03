"""SDK configuration with sensible defaults and validation."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SDKConfig:
    """Configuration for the Vigil SDK.

    All fields are validated in ``__post_init__`` so that invalid
    configurations fail fast at initialisation time.
    """

    endpoint: str = "http://localhost:8000"
    api_key: str = ""
    project_id: str = "default"
    batch_size: int = 100
    flush_interval_ms: int = 500
    max_queue_size: int = 10_000
    timeout_seconds: float = 10.0
    enabled: bool = True
    headers: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if not self.endpoint or not self.endpoint.strip():
            raise ValueError("endpoint must be a non-empty string")
        if self.batch_size < 1:
            raise ValueError("batch_size must be >= 1")
        if self.flush_interval_ms < 10:
            raise ValueError("flush_interval_ms must be >= 10")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be > 0")

    @property
    def ingest_url(self) -> str:
        """Full URL for the span ingestion endpoint."""
        return f"{self.endpoint.rstrip('/')}/v1/traces"

    @property
    def auth_headers(self) -> dict[str, str]:
        """HTTP headers including the Bearer token when an API key is set."""
        headers = {**self.headers}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

# Server Source Files

Every file in `server/src/vigil_server/` explained in plain language.

## `main.py` — The Front Door
Creates the FastAPI application. On startup, it creates database tables (in SQLite dev mode), sets up CORS, and wires in all the API routes. On shutdown, it closes the database connection pool.

## `config.py` — The Control Panel
Uses `pydantic-settings` to read configuration from environment variables (prefixed with `VIGIL_`) or a `.env` file. Defines database URL, Redis URL, server host/port, CORS origins, and the default API key.

## `dependencies.py` — The Supply Closet
FastAPI dependency injection. `get_db()` provides a database session for each request. `get_current_project()` extracts the project ID from the Bearer token in the Authorization header. These are injected automatically into route handlers.

## `middleware/auth.py` — The Security Guard
Validates API keys from the Authorization header. Public paths (health, docs) skip auth. For other requests, it checks the key against the configured dev key or looks it up in the database.

## `api/router.py` — The Switchboard
Connects all route modules under the `/v1` prefix. Health routes have no prefix. This is the single place where all endpoints are registered.

## `api/health.py` — The Pulse Check
Two endpoints: `/health` always returns OK, `/ready` actually tests the database connection and reports if the server is truly ready to handle requests.

## `api/v1/traces.py` — The Inbox
Handles trace ingestion (POST) and querying (GET). The POST endpoint receives batches of spans from the SDK and passes them to the trace service. GET endpoints return paginated trace lists or single traces with their spans.

## `api/v1/spans.py` — The Search Engine
Lets you query spans across all traces with filters (kind, status, trace_id) and pagination.

## `api/v1/projects.py` — The Project Manager
CRUD for projects plus API key rotation. Creating a project automatically generates an API key. Key rotation deactivates old keys and creates a fresh one.

## `api/v1/replay.py` — The Time Machine
Takes a trace ID and input mutations, then computes what would change. It loads the original trace, applies your mutations to span inputs, and returns diffs showing original vs. mutated data.

## `api/v1/drift.py` — The Weather Station
Serves drift alerts and summary statistics. Drift detection compares recent span latencies against a baseline to spot when your agents start behaving differently.

## `services/trace_service.py` — The Filing Clerk
Business logic for trace operations. `ingest_spans` creates/updates traces and inserts spans. `list_traces` handles pagination. `build_trace_response` converts database models to API response format.

## `services/replay_engine.py` — The What-If Calculator
Loads a trace from the database, deep-copies span inputs, applies your mutations, and computes diffs. The `ReplayResult` class packages everything for the API response.

## `services/drift_detector.py` — The Anomaly Detector
Uses Population Stability Index (PSI) to compare latency distributions. Spans are grouped by kind, split into baseline (24h) and current (1h) windows, and their distributions are compared. PSI >= 0.1 triggers an alert.

## `models/base.py` — The Blueprint Base
SQLAlchemy declarative base with two mixins: `UUIDMixin` adds an auto-generated hex UUID primary key, `TimestampMixin` adds `created_at` and `updated_at` columns.

## `models/trace.py` — The Trace Record
Database model for traces. Each trace has an ID, project reference, name, status, metadata, timing, and a relationship to its spans.

## `models/span.py` — The Span Record
Database model for spans. Linked to a trace via foreign key (cascade delete). Stores kind, status, input/output JSON, events, and timing.

## `models/project.py` — The Project Record
Database models for projects and API keys. A project has many API keys. Keys are generated with a `vgl_` prefix and can be deactivated without deletion.

## `models/drift.py` — The Alert Record
Database model for drift alerts. Stores the span kind, metric name, baseline/current values, PSI score, severity level, and resolved status.

## `db/session.py` — The Connection Pool
Creates the async SQLAlchemy engine and session factory. The engine connects to whatever database URL is configured (PostgreSQL or SQLite).

## `db/repository.py` — The Generic Toolbox
A generic CRUD repository that works with any SQLAlchemy model. Provides `create`, `get`, `list`, and `delete` operations with basic filtering.

## `schemas/traces.py` — The Trace Contracts
Pydantic schemas defining the shape of trace API requests and responses. `IngestRequest` validates incoming spans, `TraceResponse` formats outgoing data.

## `schemas/spans.py` — The Span Contracts
Pydantic schemas for span query responses, including a tree node structure for hierarchical visualization.

## `schemas/projects.py` — The Project Contracts
Pydantic schemas for project CRUD operations and API key responses.

## `schemas/drift.py` — The Drift Contracts
Pydantic schemas for drift alert responses and summary statistics.

## `exceptions.py` — The Error Catalog
Custom exception hierarchy for structured error handling. `VigilError` is the base, with `NotFoundError`, `ValidationError`, and `AuthenticationError` subclasses. Includes global FastAPI error handlers that return consistent JSON responses.

## `logging_config.py` — The Log Formatter
Structured JSON logging configuration. Formats log output with timestamp, level, logger name, message, and request ID for correlation.

## `middleware/request_id.py` — The Ticket Stamper
Middleware that assigns a unique request ID to every incoming request. Reads `X-Request-ID` from the header or generates a UUID. Makes the ID available via `contextvars` for log correlation.

# API Reference

Base URL: `http://localhost:8000`

All endpoints (except health and auth) require authentication via `Authorization: Bearer <api_key>` or `Authorization: Bearer <jwt_token>` header.

## Health

### GET /health
Check server status.

**Auth:** None

**Response 200:**
```json
{"status": "ok"}
```

### GET /ready
Check database connectivity.

**Auth:** None

**Response 200:**
```json
{"status": "ready"}
```

**Response 503:**
```json
{"status": "not_ready", "detail": "..."}
```

---

## Authentication

### POST /v1/auth/register
Register a new user account.

**Auth:** None

**Request Body:**
```json
{"email": "user@example.com", "password": "securepass123"}
```

**Response 201:**
```json
{"id": "abc123", "email": "user@example.com", "is_active": true, "created_at": "..."}
```

**Response 409:** Email already registered.

### POST /v1/auth/login
Authenticate and receive a JWT token.

**Auth:** None

**Request Body:**
```json
{"email": "user@example.com", "password": "securepass123"}
```

**Response 200:**
```json
{"access_token": "eyJ...", "token_type": "bearer"}
```

**Response 401:** Invalid credentials.

---

## Traces

### POST /v1/traces
Ingest a batch of spans.

**Auth:** Required

**Request Body:**
```json
{
  "spans": [
    {
      "span_id": "abc123",
      "trace_id": "trace-001",
      "parent_span_id": null,
      "name": "llm-call",
      "kind": "llm",
      "status": "ok",
      "input": {"model": "gpt-4", "messages": [...]},
      "output": {"content": "Hello"},
      "metadata": {},
      "events": [],
      "start_time": "2024-01-01T00:00:00Z",
      "end_time": "2024-01-01T00:00:01Z"
    }
  ],
  "project_id": "my-project",
  "trace_name": "my-pipeline",
  "trace_metadata": {},
  "external_id": "ext-123"
}
```

**Response 201:**
```json
{"trace_id": "trace-001", "span_count": 1}
```

### GET /v1/traces
List traces with pagination and filtering.

**Auth:** Required

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `offset` | int | 0 | Pagination offset |
| `limit` | int | 50 | Items per page (1-200) |
| `status` | string | null | Filter by status (ok, error, unset) |
| `start_date` | datetime | null | Filter traces after this date |
| `end_date` | datetime | null | Filter traces before this date |

**Response 200:**
```json
{
  "traces": [...],
  "total": 42,
  "offset": 0,
  "limit": 50
}
```

### GET /v1/traces/{trace_id}
Get a single trace with all spans.

**Auth:** Required

**Response 200:** Full trace object with spans array and `external_id` field.

**Response 404:**
```json
{"detail": "Trace not found"}
```

### PATCH /v1/traces/{trace_id}
Update a trace's status and/or metadata.

**Auth:** Required

**Request Body:**
```json
{"status": "ok", "metadata": {"key": "value"}}
```

**Response 200:** Updated trace object.

**Response 404:** Trace not found.

### POST /v1/traces/{trace_id}/events/{span_id}
Append an event to a span within a trace.

**Auth:** Required

**Request Body:**
```json
{"name": "cache-hit", "attributes": {"key": "abc"}}
```

**Response 201:**
```json
{"name": "cache-hit", "timestamp": "...", "attributes": {"key": "abc"}}
```

**Response 404:** Trace or span not found.

---

## Spans

### GET /v1/spans
Query spans across traces.

**Auth:** Required

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `kind` | string | Filter by span kind |
| `status` | string | Filter by status |
| `trace_id` | string | Filter by trace |
| `offset` | int | Pagination offset |
| `limit` | int | Items per page |

**Response 200:**
```json
{
  "spans": [...],
  "total": 100,
  "offset": 0,
  "limit": 50
}
```

---

## Projects

### POST /v1/projects
Create a new project.

**Auth:** Required

**Request Body:**
```json
{"name": "My Project", "description": "Optional description"}
```

**Response 201:** Project object with generated API key.

### GET /v1/projects
List all projects.

**Auth:** Required

**Response 200:**
```json
{"projects": [...], "total": 5}
```

### GET /v1/projects/{project_id}
Get a single project.

**Auth:** Required

**Response 200:** Project object with API keys.

### POST /v1/projects/{project_id}/rotate-key
Rotate API key — deactivates old keys and creates a new one.

**Auth:** Required

**Response 201:**
```json
{"key": "vgl_new_key_here"}
```

---

## Replay

### POST /v1/traces/{trace_id}/replay
Replay a trace with input mutations. Persists a ReplayRun record.

**Auth:** Required

**Request Body:**
```json
{
  "mutations": {
    "span-id-1": {"model": "gpt-4-turbo"},
    "span-id-2": {"temperature": 0.5}
  }
}
```

**Response 200:**
```json
{
  "original_trace_id": "trace-001",
  "mutations": {...},
  "diffs": [
    {
      "span_id": "span-id-1",
      "span_name": "llm-call",
      "original_input": {...},
      "mutated_input": {...},
      "original_output": {...}
    }
  ],
  "replay_run_id": "run-abc"
}
```

### GET /v1/traces/{trace_id}/replay/{replay_id}
Get the status of a replay run.

**Auth:** Required

**Response 200:**
```json
{
  "id": "run-abc",
  "original_trace_id": "trace-001",
  "status": "completed",
  "created_by": null,
  "config": {...},
  "result_trace_id": null,
  "created_at": "..."
}
```

### GET /v1/traces/{trace_id}/replay/{replay_id}/diff
Get the diff output from a completed replay run.

**Auth:** Required

**Response 200:**
```json
{
  "original_trace_id": "trace-001",
  "mutations": {...},
  "diffs": [...]
}
```

---

## Drift Detection

### GET /v1/drift/alerts
List drift alerts.

**Auth:** Required

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `include_resolved` | bool | false | Include resolved alerts |

**Response 200:** Array of drift alert objects.

### GET /v1/drift/summary
Get drift summary statistics.

**Auth:** Required

**Response 200:**
```json
{
  "total_alerts": 15,
  "unresolved": 3,
  "by_severity": {"low": 1, "medium": 1, "high": 1},
  "recent_alerts": [...]
}
```

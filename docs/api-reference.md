# API Reference

Base URL: `http://localhost:8000`

All endpoints (except health) require authentication via `Authorization: Bearer <api_key>` header.

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
  "trace_metadata": {}
}
```

**Response 201:**
```json
{"trace_id": "trace-001", "span_count": 1}
```

### GET /v1/traces
List traces with pagination.

**Auth:** Required

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `offset` | int | 0 | Pagination offset |
| `limit` | int | 50 | Items per page (1-200) |

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

**Response 200:** Full trace object with spans array.

**Response 404:**
```json
{"detail": "Trace not found"}
```

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
Replay a trace with input mutations.

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
  ]
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

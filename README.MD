# Vigil

Real-time observability platform for agentic AI systems. Trace every decision an agent makes, detect drift, replay failures, and debug production issues before customers notice.

## Architecture

```
┌─────────────────┐     HTTP/WebSocket     ┌──────────────────┐     SQL      ┌────────────┐
│   vigil SDK     │ ──────────────────────> │  vigil server    │ ──────────> │ PostgreSQL │
│  (Python pkg)   │    POST /v1/traces      │  (FastAPI)       │             │            │
│                 │                         │                  │             │            │
│ @trace, spans,  │                         │ Ingest, query,   │             │ traces,    │
│ auto-instrument │                         │ replay, drift    │             │ spans,     │
│ OpenAI/Anthropic│                         │ detection, WS    │             │ events,    │
│ LangChain/Crew  │                         │ live streaming   │             │ metrics    │
└─────────────────┘                         └──────┬───────────┘             └────────────┘
                                                   │
                                                   │ REST API
                                                   │
                                            ┌──────▼───────────┐
                                            │  Dashboard       │
                                            │  (React/Next.js) │
                                            │                  │
                                            │ Trace viewer,    │
                                            │ span tree,       │
                                            │ replay debugger, │
                                            │ drift alerts     │
                                            └──────────────────┘
```

## Core Concepts

**Trace**: A complete agent execution from input to output. One user query that triggers an agent produces one trace.

**Span**: A unit of work within a trace. An LLM call is a span. A tool call is a span. A retrieval step is a span. Spans nest (a parent "agent_run" span contains child "llm_call" and "tool_call" spans).

**Event**: A point-in-time occurrence within a span (token streamed, error thrown, confidence score computed).

**Drift**: When an agent's decision patterns change over time. Same input class, different output distribution. Vigil detects this automatically.

## Data Flow

1. Developer wraps their agent code with `@vigil.trace()`
2. SDK captures every LLM call, tool invocation, and retrieval as spans
3. Spans are batched and shipped to the Vigil server via HTTP
4. Server stores traces in PostgreSQL, runs drift detection async
5. Dashboard renders trace trees, metrics, and replay interface
6. Replay engine lets devs re-run a failed trace with modified prompts

## Build Order (What to Build When)

### Week 1-2: SDK + Ingestion

- [ ] SDK: Trace/Span data classes, context propagation
- [ ] SDK: `@trace` decorator for wrapping agent functions
- [ ] SDK: OpenAI auto-instrumentation (monkey-patch client)
- [ ] SDK: HTTP exporter (batch spans, POST to server)
- [ ] Server: FastAPI app with `/v1/traces` ingest endpoint
- [ ] Server: SQLAlchemy models for traces/spans
- [ ] Server: SQLite for local dev (swap to Postgres later)

### Week 3-4: Query API + Basic Dashboard

- [ ] Server: GET `/v1/traces` with filtering (status, time range, agent name)
- [ ] Server: GET `/v1/traces/{id}` with full span tree
- [ ] Server: GET `/v1/metrics` (latency p50/p95/p99, error rate, cost)
- [ ] Dashboard: Trace list view
- [ ] Dashboard: Span tree visualization (collapsible nested view)
- [ ] Dashboard: Basic metrics charts

### Week 5-6: Replay Debugger

- [ ] Server: Replay engine (re-execute a trace with modified params)
- [ ] Server: Diff engine (compare original vs. replayed trace)
- [ ] Dashboard: Replay interface (select span, edit prompt, re-run)
- [ ] SDK: Anthropic auto-instrumentation

### Week 7-8: Drift Detection + Multi-Framework

- [ ] Server: Drift detection service (statistical comparison of span outputs over time)
- [ ] Server: Alerting (webhook + email when drift exceeds threshold)
- [ ] SDK: LangChain/LangGraph integration
- [ ] SDK: CrewAI integration

### Week 9-10: Production Hardening

- [ ] Server: PostgreSQL migration
- [ ] Server: WebSocket endpoint for live trace streaming
- [ ] Server: Auth (API keys per project)
- [ ] Dashboard: Live trace view
- [ ] SDK: Async batching with retry/backoff
- [ ] Packaging: Docker Compose for one-command deploy

## Tech Stack

| Component  | Technology                   | Why                                |
| ---------- | ---------------------------- | ---------------------------------- |
| SDK        | Python 3.11+                 | Target audience is Python AI devs  |
| Server     | FastAPI + SQLAlchemy         | Async, fast, good ORM              |
| Database   | PostgreSQL (SQLite for dev)  | JSONB for flexible span attributes |
| Dashboard  | Next.js + Tailwind           | Fast to build, good DX             |
| Task Queue | None initially, Celery later | Drift detection runs async         |

## Local Development

```bash
# Start everything
make dev

# SDK only
cd sdk && pip install -e ".[dev]"

# Server only
cd server && pip install -e ".[dev]" && uvicorn vigil_server.main:app --reload

# Run tests
make test
```

## Example Usage

```python
import vigil
from openai import OpenAI

# Initialize (points to your Vigil server)
vigil.init(api_key="vgl_xxx", endpoint="http://localhost:8787")

# Auto-instrument OpenAI
vigil.integrations.openai.patch()

client = OpenAI()

@vigil.trace(name="customer_support_agent")
def handle_ticket(ticket_text: str):
    # This LLM call is automatically captured as a span
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a support agent."},
            {"role": "user", "content": ticket_text}
        ]
    )

    # Manual span for custom logic
    with vigil.span(name="classify_intent", kind="REASONING"):
        intent = classify(response.choices[0].message.content)
        vigil.current_span().set_attribute("intent", intent)

    return response.choices[0].message.content
```

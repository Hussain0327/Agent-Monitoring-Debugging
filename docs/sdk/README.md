# Vigil SDK

The Vigil SDK is a Python library that instruments your AI agent code to capture traces, spans, and events. It sends them to the Vigil server for storage and analysis.

## Installation

```bash
pip install vigil-sdk

# With auto-instrumentation
pip install vigil-sdk[openai]
pip install vigil-sdk[anthropic]
```

## Quick Start

```python
import vigil

# Initialize
await vigil.init(
    endpoint="http://localhost:8000",
    api_key="your-api-key",
    project_id="my-project",
)

# Decorate your functions
@vigil.trace()
async def my_pipeline():
    @vigil.span(kind=vigil.SpanKind.LLM)
    async def call_llm(prompt):
        return await openai_client.chat.completions.create(...)

    return await call_llm("Hello")

# Run
await my_pipeline()

# Shutdown cleanly
await vigil.shutdown()
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `endpoint` | str | `http://localhost:8000` | Server URL |
| `api_key` | str | `""` | Authentication key |
| `project_id` | str | `"default"` | Project identifier |
| `batch_size` | int | `100` | Spans per batch |
| `flush_interval_ms` | int | `500` | Flush interval in ms |
| `max_queue_size` | int | `10000` | Max queued spans |
| `timeout_seconds` | float | `10.0` | HTTP timeout |
| `enabled` | bool | `True` | Enable/disable SDK |

## Decorators

### @trace()
Wraps a function as a new trace (top-level operation).

```python
@vigil.trace(name="my-pipeline", metadata={"version": "1.0"})
async def pipeline():
    ...
```

### @span()
Wraps a function as a span within the current trace.

```python
@vigil.span(name="retrieve-docs", kind=vigil.SpanKind.RETRIEVER)
async def retrieve(query):
    ...
```

## Context Manager

Use `trace_context` for manual trace lifecycle management with automatic cleanup:

```python
from vigil import trace_context, get_client

client = vigil.get_client()

# Async
async with trace_context(client, "my-operation", metadata={"k": "v"}) as trace:
    # trace is active here
    ...
# trace is automatically ended (with error status on exception)

# Sync
with trace_context(client, "sync-operation") as trace:
    ...
```

## Convenience Functions

High-level helpers that no-op gracefully when no client is active:

```python
import vigil

# Add an event to the current span
vigil.log_event("cache-hit", {"key": "user:123"})

# Attach metadata to the current span or trace
vigil.attach_metadata("user_id", "u123")

# Log an LLM call (creates and ends an LLM span)
vigil.log_llm_call("gpt-4", input={"prompt": "Hi"}, output={"text": "Hello"})

# Log a tool call (creates and ends a TOOL span)
vigil.log_tool_call("search", input={"query": "foo"}, output={"results": [...]})
```

## Span Kinds

| Kind | Use Case |
|------|----------|
| `llm` | LLM API calls |
| `tool` | Tool/function invocations |
| `chain` | Sequential processing steps |
| `retriever` | RAG retrieval operations |
| `agent` | Agent decision points |
| `custom` | Anything else |

## Integrations

Auto-instrument third-party LLM libraries:

```python
import vigil

# Activate specific integration
vigil.activate_integration("openai")
vigil.activate_integration("anthropic")

# Or activate all registered integrations
vigil.activate_all_integrations()

# List available integrations
print(vigil.available_integrations())  # ["openai", "anthropic"]
```

### OpenAI
Patches `Completions.create` and `AsyncCompletions.create` to automatically capture LLM spans with model, messages, and usage data.

### Anthropic
Patches `Messages.create` and `AsyncMessages.create` to automatically capture LLM spans with model, messages, and usage data.

## Public API

All exports available from `import vigil`:

| Export | Type | Description |
|--------|------|-------------|
| `init()` | async function | Initialize the SDK |
| `shutdown()` | async function | Shut down the SDK |
| `get_client()` | function | Get the global client |
| `trace()` | decorator | Create a new trace |
| `span()` | decorator | Create a new span |
| `trace_context` | context manager | Manual trace lifecycle |
| `current_span()` | function | Get the current span |
| `current_trace()` | function | Get the current trace |
| `log_event()` | function | Add event to current span |
| `attach_metadata()` | function | Attach metadata to span/trace |
| `log_llm_call()` | function | Log an LLM call as a span |
| `log_tool_call()` | function | Log a tool call as a span |
| `activate_integration()` | function | Activate a named integration |
| `activate_all_integrations()` | function | Activate all integrations |
| `available_integrations()` | function | List registered integrations |
| `Trace` | class | Trace data model |
| `Span` | class | Span data model |
| `Event` | class | Event data model |
| `SpanKind` | enum | Span kind constants |
| `SpanStatus` | enum | Span status constants |

See [SDK Files](files.md) for details on every source file.

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

```python
from vigil.integrations import activate

# Auto-instrument OpenAI calls
activate("openai")

# Auto-instrument Anthropic calls
activate("anthropic")
```

See [SDK Files](files.md) for details on every source file.

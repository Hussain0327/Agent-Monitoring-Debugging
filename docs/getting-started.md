# Getting Started

Get Vigil running and capture your first trace in 5 minutes.

## Prerequisites

- Python 3.11+
- Node.js 18+ (for dashboard)
- Docker (optional, for PostgreSQL + Redis)

## 1. Clone and Install

```bash
git clone <repo-url>
cd vigil

# Install all packages
make install
```

Or install individually:

```bash
# SDK
cd sdk && pip install -e ".[dev]"

# Server
cd server && pip install -e ".[dev]"

# Dashboard
cd dashboard && npm install
```

## 2. Start the Server

**Option A: Local (SQLite)**
```bash
make dev-server
# Server runs at http://localhost:8000
```

**Option B: Docker (PostgreSQL + Redis)**
```bash
make docker-up
```

## 3. Start the Dashboard

```bash
make dev-dashboard
# Dashboard runs at http://localhost:3000
```

## 4. Instrument Your Code

```python
import asyncio
import vigil

async def main():
    # Initialize the SDK
    await vigil.init(
        endpoint="http://localhost:8000",
        api_key="dev-api-key-change-me",
        project_id="my-project",
    )

    # Decorate your pipeline
    @vigil.trace()
    async def my_pipeline():

        @vigil.span(kind=vigil.SpanKind.LLM)
        async def call_llm(prompt: str):
            # Your LLM call here
            return {"response": "Hello!"}

        result = await call_llm("Say hello")
        return result

    await my_pipeline()
    await vigil.shutdown()

asyncio.run(main())
```

## 5. View in Dashboard

Open http://localhost:3000 — you should see your trace with its spans.

## Auto-Instrumentation

Vigil can automatically capture OpenAI and Anthropic calls:

```python
import vigil
from vigil.integrations import activate

await vigil.init(endpoint="http://localhost:8000", api_key="dev-api-key-change-me")

# Activate auto-instrumentation
activate("openai")     # Patches openai.ChatCompletion.create
activate("anthropic")  # Patches anthropic.Messages.create
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Default | Description |
|----------|---------|-------------|
| `VIGIL_DATABASE_URL` | `sqlite+aiosqlite:///./vigil.db` | Database connection |
| `VIGIL_REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `VIGIL_API_KEY` | `dev-api-key-change-me` | Server API key |
| `VIGIL_HOST` | `0.0.0.0` | Server bind host |
| `VIGIL_PORT` | `8000` | Server bind port |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Dashboard API URL |

## Next Steps

- [Architecture](architecture.md) — Understand the full system
- [API Reference](api-reference.md) — All endpoints documented
- [SDK Reference](sdk/README.md) — Decorators, integrations, configuration

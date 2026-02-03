# Vigil Server

The Vigil Server is a FastAPI application that receives traces from the SDK, stores them in a database, and serves them to the dashboard.

## Running

**Development (SQLite):**
```bash
cd server
pip install -e ".[dev]"
uvicorn vigil_server.main:app --reload --port 8000
```

**Production (PostgreSQL):**
```bash
export VIGIL_DATABASE_URL="postgresql+asyncpg://user:pass@host/vigil"
uvicorn vigil_server.main:app --host 0.0.0.0 --port 8000
```

## Configuration

All settings use the `VIGIL_` environment prefix:

| Variable | Default | Description |
|----------|---------|-------------|
| `VIGIL_DATABASE_URL` | `sqlite+aiosqlite:///./vigil.db` | Database connection |
| `VIGIL_REDIS_URL` | `redis://localhost:6379/0` | Redis URL |
| `VIGIL_HOST` | `0.0.0.0` | Bind host |
| `VIGIL_PORT` | `8000` | Bind port |
| `VIGIL_LOG_LEVEL` | `info` | Logging level |
| `VIGIL_CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed origins |
| `VIGIL_API_KEY` | `dev-api-key-change-me` | Default API key |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/ready` | Readiness check |
| POST | `/v1/traces` | Ingest spans |
| GET | `/v1/traces` | List traces |
| GET | `/v1/traces/{id}` | Get trace |
| GET | `/v1/spans` | Query spans |
| POST | `/v1/projects` | Create project |
| GET | `/v1/projects` | List projects |
| GET | `/v1/projects/{id}` | Get project |
| POST | `/v1/projects/{id}/rotate-key` | Rotate API key |
| POST | `/v1/traces/{id}/replay` | Replay trace |
| GET | `/v1/drift/alerts` | Drift alerts |
| GET | `/v1/drift/summary` | Drift summary |

## Database Migrations

```bash
# Run migrations
cd server && alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

See [Server Files](files.md) for details on every source file.

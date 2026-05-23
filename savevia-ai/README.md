# savevia-ai

Python rewrite of `savevia-optimizer`. See design spec at
`docs/superpowers/specs/2026-05-23-python-rewrite-design.md` and the
implementation plans under `docs/superpowers/plans/`.

## Local dev

### Prerequisites
- Python 3.12+
- uv (https://docs.astral.sh/uv/)
- Docker (for MySQL/Redis)

### Setup
```bash
cd savevia-ai
uv sync
cp .env.example .env  # edit values for your local setup
```

### Start dependencies (from repo root)
```bash
docker compose up -d mysql redis
```

### Run the service
```bash
cd savevia-ai
uv run uvicorn app.main:app --reload --port 8002
```

### Tests
```bash
# Unit tests only (fast, no external deps)
uv run pytest

# Full suite including integration (requires MySQL + Redis running)
INTEGRATION_TESTS=1 DB_NAME=savevia DB_USER=savevia DB_PASSWORD=savevia123 \
  uv run pytest
```

### Lint / format
```bash
uv run ruff check app/ tests/
uv run ruff format app/ tests/
```

### Docker build
```bash
docker build -t savevia-ai:dev .
```

### Database migrations (Alembic)
```bash
# View current state
uv run alembic current
uv run alembic history

# Create a new migration after model changes
uv run alembic revision -m "add_xxx" --autogenerate

# Apply migrations
uv run alembic upgrade head
```

The baseline migration (`20260523_2129_baseline_existing_schema.py`) is a no-op
because the schema is established by `docker/mysql/init/*.sql`. All future
schema changes go through Alembic.

## Endpoints (foundation)

- `GET /health` — liveness
- `GET /ready` — readiness (pings MySQL + Redis)
- `GET /docs` — OpenAPI UI (disabled in production)

Business endpoints arrive in subsequent plans:
- Plan 02: Chat / Agent (LangGraph + 6 tools + SSE streaming)
- Plan 03: Memory (extraction + injection)
- Plan 04: Transactions / Flinks / SavedResults / Optimizer
- Plan 05: Gateway routing + cutover

## Project structure

```
savevia-ai/
├── app/
│   ├── core/           # config, db, redis, security, logging
│   ├── clients/        # HTTP clients (UserServiceClient, CardServiceClient)
│   ├── models/         # 8 SQLAlchemy ORM models for owned tables
│   ├── repositories/   # data access (BaseRepository + per-model repos)
│   ├── api/            # FastAPI routers
│   └── main.py         # FastAPI app factory + lifespan
├── alembic/            # Alembic migrations
├── tests/              # pytest suite
├── Dockerfile
└── pyproject.toml
```

## Service contract notes

### Calling Java services (savevia-user, savevia-card)
- Auth: `X-User-Id` header (matches the gateway pattern where the gateway
  extracts user_id from a validated JWT and forwards it as a trusted header).
  **No JWT pass-through** to internal Java services.
- Response shape: All Java endpoints return a `Result<T>` envelope
  `{code, message, data, timestamp}` — clients unwrap to return `data` and
  raise `JavaServiceError` if `code != 200`.
- Retries: GET requests retry once on 5xx or timeout. POSTs do not retry.

### Inbound auth
- Gateway already validates JWT before routing.
- This service re-validates the JWT (defense-in-depth) using the same
  `JWT_SECRET` as Java services. HS256, requires `sub` and `exp` claims.

## Known production caveats

- `pool_pre_ping=False` in `app/core/db.py` is a workaround for an
  aiomysql/SQLAlchemy 2.0 compatibility quirk where `pool_pre_ping=True`
  raises `TypeError: ping() missing 1 required positional argument: 'reconnect'`
  on every checkout. `pool_recycle=3600` mitigates stale connections.
  Track upstream; re-enable when fixed.

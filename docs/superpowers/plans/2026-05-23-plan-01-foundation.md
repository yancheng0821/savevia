# savevia-ai Foundation — Implementation Plan (Phase 0 + Phase 1)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up a Python 3.12 / FastAPI / SQLAlchemy 2.0 async / LangGraph-ready `savevia-ai` service skeleton with database access, Redis, JWT verification, HTTP clients to the existing Java `savevia-user` and `savevia-card` services, ORM models for 8 owned tables, and 2 working repositories — but **no business endpoints yet**. Subsequent plans add the agent, chat, memory, Flinks, etc.

**Architecture:** New Python service `savevia-ai/` at the repo root, separate from the Java services. Uses `uv` for dependency management. FastAPI app factory with module-based routing (each module = router + service + repository + schema + models). Shares the existing MySQL and Redis. Inbound JWT verified with the same `JWT_SECRET` used by Java. Outbound HTTP to Java services uses `httpx` with the user's JWT passed through unchanged.

**Tech Stack:** Python 3.12, uv, FastAPI, Pydantic v2, pydantic-settings, SQLAlchemy 2.0 (async), aiomysql, Alembic, redis (async), httpx, PyJWT, structlog, pytest, pytest-asyncio, testcontainers.

**Reference spec:** `docs/superpowers/specs/2026-05-23-python-rewrite-design.md`

**Estimated effort:** 8 person-days (1 week solo).

---

## File Structure

After this plan completes, the following structure exists:

```
savevia-ai/
├── pyproject.toml                         # uv project root
├── uv.lock
├── .python-version                        # 3.12
├── Dockerfile
├── .env.example
├── README.md
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/                          # empty initially (baseline already-applied schema)
├── app/
│   ├── __init__.py
│   ├── main.py                            # FastAPI app factory + lifespan
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                      # pydantic-settings
│   │   ├── logging.py                     # structlog setup
│   │   ├── db.py                          # async SQLAlchemy engine + session dep
│   │   ├── redis_client.py                # async redis client
│   │   └── security.py                    # JWT decode dep
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── user_client.py                 # → savevia-user
│   │   └── card_client.py                 # → savevia-card
│   ├── models/                            # all SQLAlchemy ORM models (one Base shared)
│   │   ├── __init__.py
│   │   ├── base.py                        # DeclarativeBase
│   │   ├── transaction.py
│   │   ├── saved_result.py
│   │   ├── bank_connection.py
│   │   ├── bank_account.py
│   │   ├── connection_history.py
│   │   ├── merchant_category.py
│   │   ├── missed_cashback_report.py
│   │   └── user_connection_limit.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py                        # generic CRUD base
│   │   ├── transaction_repository.py
│   │   └── saved_result_repository.py
│   └── api/
│       ├── __init__.py
│       └── health.py                      # GET /health, GET /ready
└── tests/
    ├── __init__.py
    ├── conftest.py                        # shared fixtures (db, http client, etc.)
    ├── test_health.py
    ├── test_config.py
    ├── test_security.py
    ├── test_user_client.py
    ├── test_card_client.py
    ├── test_transaction_repository.py
    └── test_saved_result_repository.py
```

Also modified at the repo root:

- `docker-compose.yml` — add `savevia-ai` service entry (commented out by default to avoid breaking current Java dev)
- `.env.example` — add Python-specific vars

---

## Task 1: Initialize uv project and directory structure

**Files:**
- Create: `savevia-ai/pyproject.toml`
- Create: `savevia-ai/.python-version`
- Create: `savevia-ai/.gitignore`
- Create: `savevia-ai/README.md`
- Create: `savevia-ai/app/__init__.py`
- Create: `savevia-ai/tests/__init__.py`

- [ ] **Step 1: Verify uv is installed**

Run: `uv --version`

Expected: `uv 0.4.x` or later. If not installed, run `curl -LsSf https://astral.sh/uv/install.sh | sh` (per [uv install docs](https://docs.astral.sh/uv/getting-started/installation/)).

- [ ] **Step 2: Create directory and initialize uv project**

Run:
```bash
mkdir -p savevia-ai/app savevia-ai/tests
cd savevia-ai
uv init --name savevia-ai --python 3.12 --no-readme --bare
```

This creates `pyproject.toml` and `.python-version`. We override the empty `pyproject.toml` in the next step.

- [ ] **Step 3: Write the full pyproject.toml**

Create `savevia-ai/pyproject.toml` with this exact content:

```toml
[project]
name = "savevia-ai"
version = "0.1.0"
description = "SaveVia AI service (Python rewrite of savevia-optimizer)"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.6.0",
    "sqlalchemy[asyncio]>=2.0.36",
    "aiomysql>=0.2.0",
    "alembic>=1.13.0",
    "redis>=5.2.0",
    "httpx>=0.27.0",
    "pyjwt[crypto]>=2.10.0",
    "structlog>=24.4.0",
    "python-multipart>=0.0.12",
]

[dependency-groups]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "httpx>=0.27.0",
    "testcontainers[mysql]>=4.8.0",
    "ruff>=0.7.0",
    "mypy>=1.13.0",
    "respx>=0.21.0",
]

[tool.uv]
package = false

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-v --tb=short --strict-markers"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM", "ASYNC"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.12"
strict = true
plugins = ["pydantic.mypy"]
```

- [ ] **Step 4: Write `.python-version`**

Create `savevia-ai/.python-version`:
```
3.12
```

- [ ] **Step 5: Write `.gitignore`**

Create `savevia-ai/.gitignore`:
```
__pycache__/
*.py[cod]
.venv/
.env
.env.local
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
```

- [ ] **Step 6: Write `README.md` (minimal placeholder)**

Create `savevia-ai/README.md`:
```markdown
# savevia-ai

Python rewrite of `savevia-optimizer`. See `docs/superpowers/specs/2026-05-23-python-rewrite-design.md`.

## Dev

```bash
cd savevia-ai
uv sync
uv run uvicorn app.main:app --reload --port 8002
```

## Test

```bash
uv run pytest
```
```

- [ ] **Step 7: Create empty `__init__.py` files**

Run from repo root:
```bash
touch savevia-ai/app/__init__.py savevia-ai/tests/__init__.py
```

- [ ] **Step 8: Install dependencies**

Run from `savevia-ai/`:
```bash
uv sync
```

Expected: creates `.venv/` and `uv.lock`. No errors.

- [ ] **Step 9: Verify import works**

Run from `savevia-ai/`:
```bash
uv run python -c "import fastapi, sqlalchemy, redis, httpx, jwt, structlog; print('OK')"
```

Expected: `OK`

- [ ] **Step 10: Commit**

```bash
git add savevia-ai/
git commit -m "feat(savevia-ai): initialize uv project skeleton"
```

---

## Task 2: Configuration with pydantic-settings

**Files:**
- Create: `savevia-ai/app/core/__init__.py`
- Create: `savevia-ai/app/core/config.py`
- Create: `savevia-ai/tests/test_config.py`
- Create: `savevia-ai/.env.example`

- [ ] **Step 1: Write failing test**

Create `savevia-ai/tests/test_config.py`:
```python
import os
from unittest.mock import patch

import pytest


def test_settings_loads_from_env():
    from app.core.config import Settings

    with patch.dict(
        os.environ,
        {
            "DB_HOST": "db.example.com",
            "DB_PORT": "3307",
            "DB_NAME": "mydb",
            "DB_USER": "u",
            "DB_PASSWORD": "p",
            "REDIS_HOST": "redis.example.com",
            "REDIS_PORT": "6380",
            "JWT_SECRET": "secret-at-least-32-chars-long-xxxxxx",
            "USER_SERVICE_URL": "http://user:8081",
            "CARD_SERVICE_URL": "http://card:8082",
            "OPENAI_API_KEY": "sk-test",
        },
        clear=True,
    ):
        s = Settings()
        assert s.db_host == "db.example.com"
        assert s.db_port == 3307
        assert s.db_url.startswith("mysql+aiomysql://u:p@db.example.com:3307/mydb")
        assert s.redis_url == "redis://redis.example.com:6380/0"
        assert s.jwt_secret == "secret-at-least-32-chars-long-xxxxxx"
        assert s.user_service_url == "http://user:8081"
        assert s.card_service_url == "http://card:8082"
        assert s.openai_api_key == "sk-test"


def test_settings_rejects_short_jwt_secret():
    from app.core.config import Settings
    from pydantic import ValidationError

    with patch.dict(
        os.environ,
        {
            "DB_HOST": "x", "DB_PORT": "3306", "DB_NAME": "x", "DB_USER": "x",
            "DB_PASSWORD": "x", "REDIS_HOST": "x", "REDIS_PORT": "6379",
            "JWT_SECRET": "too-short",
            "USER_SERVICE_URL": "http://x", "CARD_SERVICE_URL": "http://x",
            "OPENAI_API_KEY": "x",
        },
        clear=True,
    ):
        with pytest.raises(ValidationError):
            Settings()
```

- [ ] **Step 2: Run the test — should fail with `ModuleNotFoundError`**

Run from `savevia-ai/`:
```bash
uv run pytest tests/test_config.py -v
```
Expected: `ModuleNotFoundError: No module named 'app.core'`

- [ ] **Step 3: Implement `app/core/__init__.py` and `app/core/config.py`**

Create `savevia-ai/app/core/__init__.py` (empty file).

Create `savevia-ai/app/core/config.py`:
```python
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    db_host: str = Field(alias="DB_HOST")
    db_port: int = Field(alias="DB_PORT", default=3306)
    db_name: str = Field(alias="DB_NAME")
    db_user: str = Field(alias="DB_USER")
    db_password: str = Field(alias="DB_PASSWORD")
    db_pool_size: int = Field(default=10, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=5, alias="DB_MAX_OVERFLOW")
    db_echo: bool = Field(default=False, alias="DB_ECHO")

    # Redis
    redis_host: str = Field(alias="REDIS_HOST")
    redis_port: int = Field(alias="REDIS_PORT", default=6379)
    redis_db: int = Field(default=0, alias="REDIS_DB")

    # JWT
    jwt_secret: str = Field(alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")

    # Java service URLs
    user_service_url: str = Field(alias="USER_SERVICE_URL")
    card_service_url: str = Field(alias="CARD_SERVICE_URL")
    http_timeout_seconds: float = Field(default=10.0, alias="HTTP_TIMEOUT_SECONDS")
    http_connect_timeout_seconds: float = Field(default=2.0, alias="HTTP_CONNECT_TIMEOUT_SECONDS")

    # OpenAI / LangGraph (used in later phases — declared now for completeness)
    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_base_url: str = Field(default="https://api.openai.com", alias="OPENAI_BASE_URL")

    # Service identity
    service_name: str = Field(default="savevia-ai", alias="SERVICE_NAME")
    service_port: int = Field(default=8002, alias="SERVICE_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    @field_validator("jwt_secret")
    @classmethod
    def jwt_secret_must_be_strong(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        return v

    @property
    def db_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
```

- [ ] **Step 4: Run the test — should pass**

Run:
```bash
uv run pytest tests/test_config.py -v
```
Expected: both tests pass.

- [ ] **Step 5: Write `.env.example`**

Create `savevia-ai/.env.example`:
```bash
# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=savevia
DB_USER=savevia
DB_PASSWORD=savevia123
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=5
DB_ECHO=false

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# JWT (MUST match Java services — use the same value as savevia-user/.env)
JWT_SECRET=savevia-jwt-secret-key-2024-must-be-at-least-256-bits-long
JWT_ALGORITHM=HS256

# Java service URLs (Docker DNS in dev, internal DNS in prod)
USER_SERVICE_URL=http://localhost:8081
CARD_SERVICE_URL=http://localhost:8082
HTTP_TIMEOUT_SECONDS=10.0
HTTP_CONNECT_TIMEOUT_SECONDS=2.0

# OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com

# Service
SERVICE_NAME=savevia-ai
SERVICE_PORT=8002
LOG_LEVEL=INFO
ENVIRONMENT=development
```

- [ ] **Step 6: Commit**

```bash
git add savevia-ai/
git commit -m "feat(savevia-ai): add pydantic-settings configuration"
```

---

## Task 3: Structured logging with structlog

**Files:**
- Create: `savevia-ai/app/core/logging.py`
- Create: `savevia-ai/tests/test_logging.py`

- [ ] **Step 1: Write failing test**

Create `savevia-ai/tests/test_logging.py`:
```python
import json
import logging

import structlog


def test_logger_outputs_json(capsys):
    from app.core.logging import configure_logging, get_logger

    configure_logging(log_level="INFO", json_output=True)
    log = get_logger("test")
    log.info("hello", user_id=42, request_id="abc")

    captured = capsys.readouterr()
    line = captured.out.strip().splitlines()[-1]
    payload = json.loads(line)

    assert payload["event"] == "hello"
    assert payload["user_id"] == 42
    assert payload["request_id"] == "abc"
    assert payload["level"] == "info"
    assert "timestamp" in payload


def test_logger_respects_log_level(capsys):
    from app.core.logging import configure_logging, get_logger

    configure_logging(log_level="WARNING", json_output=True)
    log = get_logger("test")
    log.info("should-not-appear")
    log.warning("should-appear")

    captured = capsys.readouterr()
    out = captured.out
    assert "should-not-appear" not in out
    assert "should-appear" in out
```

- [ ] **Step 2: Run — should fail with `ModuleNotFoundError`**

```bash
uv run pytest tests/test_logging.py -v
```
Expected: `ModuleNotFoundError: No module named 'app.core.logging'`

- [ ] **Step 3: Implement `app/core/logging.py`**

Create `savevia-ai/app/core/logging.py`:
```python
import logging
import sys
from typing import Any

import structlog


def configure_logging(log_level: str = "INFO", json_output: bool = True) -> None:
    """Configure structlog and stdlib logging for the application."""
    level = getattr(logging, log_level.upper(), logging.INFO)

    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        timestamper,
    ]

    if json_output:
        renderer: Any = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
```

- [ ] **Step 4: Run test — should pass**

```bash
uv run pytest tests/test_logging.py -v
```
Expected: both tests pass.

- [ ] **Step 5: Commit**

```bash
git add savevia-ai/
git commit -m "feat(savevia-ai): add structlog-based logging"
```

---

## Task 4: FastAPI app factory + health endpoint

**Files:**
- Create: `savevia-ai/app/main.py`
- Create: `savevia-ai/app/api/__init__.py`
- Create: `savevia-ai/app/api/health.py`
- Create: `savevia-ai/tests/test_health.py`
- Create: `savevia-ai/tests/conftest.py`

- [ ] **Step 1: Write failing test**

Create `savevia-ai/tests/conftest.py`:
```python
import os

# Test environment defaults — set BEFORE importing app
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "3306")
os.environ.setdefault("DB_NAME", "test")
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("JWT_SECRET", "test-secret-at-least-32-characters-long-xxxx")
os.environ.setdefault("USER_SERVICE_URL", "http://user-test:8081")
os.environ.setdefault("CARD_SERVICE_URL", "http://card-test:8082")
os.environ.setdefault("OPENAI_API_KEY", "sk-test")
os.environ.setdefault("ENVIRONMENT", "test")

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def http_client():
    from app.main import create_app

    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
```

Create `savevia-ai/tests/test_health.py`:
```python
async def test_health_endpoint_returns_ok(http_client):
    response = await http_client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "savevia-ai"
    assert "version" in body


async def test_root_redirects_to_docs(http_client):
    response = await http_client.get("/", follow_redirects=False)
    assert response.status_code in (200, 307, 308)
```

- [ ] **Step 2: Run — should fail with `ModuleNotFoundError: No module named 'app.main'`**

```bash
uv run pytest tests/test_health.py -v
```
Expected: import error.

- [ ] **Step 3: Implement `app/api/__init__.py` and `app/api/health.py`**

Create `savevia-ai/app/api/__init__.py` (empty file).

Create `savevia-ai/app/api/health.py`:
```python
from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.service_name,
        "version": "0.1.0",
        "environment": settings.environment,
    }


@router.get("/ready")
async def ready() -> dict[str, str]:
    """Liveness probe placeholder. Wired to DB/Redis pings in Task 5 and Task 6."""
    return {"status": "ready"}
```

- [ ] **Step 4: Implement `app/main.py`**

Create `savevia-ai/app/main.py`:
```python
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api import health
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(
        log_level=settings.log_level,
        json_output=(settings.environment != "development"),
    )
    log = get_logger("savevia-ai")
    log.info("service_starting", service=settings.service_name, port=settings.service_port)
    yield
    log.info("service_stopping")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="savevia-ai",
        description="SaveVia AI service",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url=None,
    )

    app.include_router(health.router)

    @app.get("/", include_in_schema=False)
    async def root() -> RedirectResponse:
        return RedirectResponse(url="/docs")

    return app


app = create_app()
```

- [ ] **Step 5: Run tests — should pass**

```bash
uv run pytest tests/test_health.py -v
```
Expected: both tests pass.

- [ ] **Step 6: Smoke-test the dev server**

Run:
```bash
uv run uvicorn app.main:app --port 8002 &
sleep 2
curl http://localhost:8002/health
kill %1
```
Expected: JSON response with `"status":"ok"`.

- [ ] **Step 7: Commit**

```bash
git add savevia-ai/
git commit -m "feat(savevia-ai): FastAPI app factory + /health endpoint"
```

---

## Task 5: SQLAlchemy async engine + session dependency

**Files:**
- Create: `savevia-ai/app/core/db.py`
- Create: `savevia-ai/app/models/__init__.py`
- Create: `savevia-ai/app/models/base.py`
- Create: `savevia-ai/tests/test_db.py`
- Modify: `savevia-ai/app/api/health.py`

- [ ] **Step 1: Write failing test**

Create `savevia-ai/tests/test_db.py`:
```python
import pytest
from sqlalchemy import text


@pytest.mark.skipif(
    not __import__("os").environ.get("INTEGRATION_TESTS"),
    reason="requires running MySQL — set INTEGRATION_TESTS=1 to enable",
)
async def test_engine_executes_simple_query():
    from app.core.db import get_engine

    engine = get_engine()
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1 AS one"))
        row = result.one()
        assert row.one == 1


def test_base_class_exists():
    from app.models.base import Base
    from sqlalchemy.orm import DeclarativeBase

    assert issubclass(Base, DeclarativeBase)


def test_session_dependency_is_async_generator():
    import inspect

    from app.core.db import get_db

    assert inspect.isasyncgenfunction(get_db)
```

- [ ] **Step 2: Run — should fail**

```bash
uv run pytest tests/test_db.py -v
```
Expected: `ModuleNotFoundError` for `app.core.db` and `app.models.base`.

- [ ] **Step 3: Implement `app/models/__init__.py` and `app/models/base.py`**

Create `savevia-ai/app/models/__init__.py` (empty for now — models added in Task 12):
```python
from app.models.base import Base

__all__ = ["Base"]
```

Create `savevia-ai/app/models/base.py`:
```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all SQLAlchemy ORM models."""
    pass
```

- [ ] **Step 4: Implement `app/core/db.py`**

Create `savevia-ai/app/core/db.py`:
```python
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.db_url,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=settings.db_echo,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
            autoflush=False,
        )
    return _session_factory


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that yields an AsyncSession per request."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def dispose_engine() -> None:
    """Call from FastAPI lifespan shutdown."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None
```

- [ ] **Step 5: Update `app/api/health.py` to ping DB in `/ready`**

Replace `savevia-ai/app/api/health.py` with:
```python
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.service_name,
        "version": "0.1.0",
        "environment": settings.environment,
    }


@router.get("/ready")
async def ready(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    """Readiness probe — verifies DB connectivity."""
    try:
        await db.execute(text("SELECT 1"))
        return JSONResponse({"status": "ready", "db": "ok"})
    except Exception as e:
        return JSONResponse(
            {"status": "not_ready", "db": "error", "error": str(e)},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
```

- [ ] **Step 6: Update lifespan to dispose engine on shutdown**

Edit `savevia-ai/app/main.py` — replace the `lifespan` function with:
```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(
        log_level=settings.log_level,
        json_output=(settings.environment != "development"),
    )
    log = get_logger("savevia-ai")
    log.info("service_starting", service=settings.service_name, port=settings.service_port)
    try:
        yield
    finally:
        from app.core.db import dispose_engine
        await dispose_engine()
        log.info("service_stopping")
```

- [ ] **Step 7: Run unit tests — pass**

```bash
uv run pytest tests/test_db.py -v -k "not test_engine_executes_simple_query"
```
Expected: 2 unit tests pass; 1 integration test skipped.

- [ ] **Step 8 (optional): Run integration test against local MySQL**

Requires `docker compose up -d mysql` first. Then:
```bash
INTEGRATION_TESTS=1 uv run pytest tests/test_db.py -v
```
Expected: all 3 tests pass. Skip this if MySQL isn't running locally.

- [ ] **Step 9: Commit**

```bash
git add savevia-ai/
git commit -m "feat(savevia-ai): SQLAlchemy 2.0 async engine + session dependency"
```

---

## Task 6: Async Redis client

**Files:**
- Create: `savevia-ai/app/core/redis_client.py`
- Create: `savevia-ai/tests/test_redis_client.py`
- Modify: `savevia-ai/app/api/health.py`

- [ ] **Step 1: Write failing test**

Create `savevia-ai/tests/test_redis_client.py`:
```python
import os

import pytest


def test_get_redis_returns_client():
    from app.core.redis_client import get_redis

    client = get_redis()
    assert client is not None
    # Same instance returned on second call
    assert get_redis() is client


@pytest.mark.skipif(
    not os.environ.get("INTEGRATION_TESTS"),
    reason="requires running Redis — set INTEGRATION_TESTS=1 to enable",
)
async def test_redis_ping_works():
    from app.core.redis_client import get_redis

    client = get_redis()
    pong = await client.ping()
    assert pong is True
```

- [ ] **Step 2: Run — fail with `ModuleNotFoundError`**

```bash
uv run pytest tests/test_redis_client.py -v -k "not test_redis_ping_works"
```
Expected: import error.

- [ ] **Step 3: Implement `app/core/redis_client.py`**

Create `savevia-ai/app/core/redis_client.py`:
```python
from redis.asyncio import Redis, from_url

from app.core.config import get_settings

_redis: Redis | None = None


def get_redis() -> Redis:
    global _redis
    if _redis is None:
        settings = get_settings()
        _redis = from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=30,
            socket_connect_timeout=2.0,
            socket_timeout=5.0,
        )
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None
```

- [ ] **Step 4: Update `app/api/health.py` to ping Redis in `/ready`**

Replace `savevia-ai/app/api/health.py` with:
```python
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_db
from app.core.redis_client import get_redis

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.service_name,
        "version": "0.1.0",
        "environment": settings.environment,
    }


@router.get("/ready")
async def ready(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> JSONResponse:
    """Readiness probe — verifies DB + Redis connectivity."""
    db_ok = False
    redis_ok = False
    errors: dict[str, str] = {}

    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        errors["db"] = str(e)

    try:
        pong = await redis.ping()
        redis_ok = bool(pong)
    except Exception as e:
        errors["redis"] = str(e)

    if db_ok and redis_ok:
        return JSONResponse({"status": "ready", "db": "ok", "redis": "ok"})

    return JSONResponse(
        {
            "status": "not_ready",
            "db": "ok" if db_ok else "error",
            "redis": "ok" if redis_ok else "error",
            "errors": errors,
        },
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    )
```

- [ ] **Step 5: Update lifespan to close redis on shutdown**

Edit `savevia-ai/app/main.py` — update the `lifespan` block to also close redis:
```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(
        log_level=settings.log_level,
        json_output=(settings.environment != "development"),
    )
    log = get_logger("savevia-ai")
    log.info("service_starting", service=settings.service_name, port=settings.service_port)
    try:
        yield
    finally:
        from app.core.db import dispose_engine
        from app.core.redis_client import close_redis
        await dispose_engine()
        await close_redis()
        log.info("service_stopping")
```

- [ ] **Step 6: Run unit tests — pass**

```bash
uv run pytest tests/test_redis_client.py -v -k "not test_redis_ping_works"
```
Expected: 1 unit test pass; 1 integration test skipped.

- [ ] **Step 7: Commit**

```bash
git add savevia-ai/
git commit -m "feat(savevia-ai): async Redis client + readiness check"
```

---

## Task 7: JWT decode dependency (defense-in-depth inbound auth)

**Files:**
- Create: `savevia-ai/app/core/security.py`
- Create: `savevia-ai/tests/test_security.py`

**Context:** Spring Cloud Gateway already verifies JWT before routing. Python re-verifies for defense in depth. Must use **same `JWT_SECRET`** and **HS256** algorithm. Java's `JwtService` claims include `userId` (Long), `email`, `exp`, `iat`. We extract `userId` and `email`.

- [ ] **Step 1: Write failing test**

Create `savevia-ai/tests/test_security.py`:
```python
import time

import jwt
import pytest
from fastapi import HTTPException, Request

from app.core.config import get_settings


def _build_request(headers: dict[str, str]) -> Request:
    scope = {
        "type": "http",
        "headers": [
            (k.lower().encode(), v.encode()) for k, v in headers.items()
        ],
        "method": "GET",
        "path": "/",
    }
    return Request(scope)


def _make_token(claims: dict, secret: str | None = None, alg: str = "HS256") -> str:
    settings = get_settings()
    return jwt.encode(claims, secret or settings.jwt_secret, algorithm=alg)


def test_decode_valid_token_returns_principal():
    from app.core.security import current_user

    token = _make_token({"userId": 42, "email": "u@example.com", "exp": int(time.time()) + 3600})
    req = _build_request({"Authorization": f"Bearer {token}"})

    principal = current_user(req)
    assert principal.user_id == 42
    assert principal.email == "u@example.com"


def test_missing_header_raises_401():
    from app.core.security import current_user

    req = _build_request({})
    with pytest.raises(HTTPException) as exc:
        current_user(req)
    assert exc.value.status_code == 401


def test_malformed_header_raises_401():
    from app.core.security import current_user

    req = _build_request({"Authorization": "NotBearer xxx"})
    with pytest.raises(HTTPException) as exc:
        current_user(req)
    assert exc.value.status_code == 401


def test_expired_token_raises_401():
    from app.core.security import current_user

    token = _make_token({"userId": 1, "exp": int(time.time()) - 10})
    req = _build_request({"Authorization": f"Bearer {token}"})
    with pytest.raises(HTTPException) as exc:
        current_user(req)
    assert exc.value.status_code == 401


def test_wrong_secret_raises_401():
    from app.core.security import current_user

    token = _make_token(
        {"userId": 1, "exp": int(time.time()) + 3600},
        secret="some-other-wrong-secret-that-is-also-32-chars-long",
    )
    req = _build_request({"Authorization": f"Bearer {token}"})
    with pytest.raises(HTTPException) as exc:
        current_user(req)
    assert exc.value.status_code == 401


def test_missing_user_id_raises_401():
    from app.core.security import current_user

    token = _make_token({"email": "x@x.com", "exp": int(time.time()) + 3600})
    req = _build_request({"Authorization": f"Bearer {token}"})
    with pytest.raises(HTTPException) as exc:
        current_user(req)
    assert exc.value.status_code == 401
```

- [ ] **Step 2: Run — fails on import**

```bash
uv run pytest tests/test_security.py -v
```
Expected: `ModuleNotFoundError: No module named 'app.core.security'`.

- [ ] **Step 3: Implement `app/core/security.py`**

Create `savevia-ai/app/core/security.py`:
```python
from dataclasses import dataclass

import jwt
from fastapi import HTTPException, Request, status

from app.core.config import get_settings


@dataclass(frozen=True)
class Principal:
    user_id: int
    email: str | None


def _extract_bearer_token(request: Request) -> str:
    auth = request.headers.get("Authorization") or request.headers.get("authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing or malformed Authorization header",
        )
    return auth.split(" ", 1)[1].strip()


def current_user(request: Request) -> Principal:
    """FastAPI dependency that verifies the inbound JWT and returns the Principal."""
    token = _extract_bearer_token(request)
    settings = get_settings()
    try:
        claims = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token: {e}",
        ) from e

    user_id = claims.get("userId")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token missing userId claim",
        )

    return Principal(user_id=int(user_id), email=claims.get("email"))


def get_raw_token(request: Request) -> str:
    """Returns the raw bearer token (for pass-through to Java services)."""
    return _extract_bearer_token(request)
```

- [ ] **Step 4: Run tests — pass**

```bash
uv run pytest tests/test_security.py -v
```
Expected: all 6 tests pass.

- [ ] **Step 5: Commit**

```bash
git add savevia-ai/
git commit -m "feat(savevia-ai): JWT decode dependency (defense-in-depth auth)"
```

---

## Task 8: HTTP clients to Java user/card services

**Files:**
- Create: `savevia-ai/app/clients/__init__.py`
- Create: `savevia-ai/app/clients/_base.py`
- Create: `savevia-ai/app/clients/user_client.py`
- Create: `savevia-ai/app/clients/card_client.py`
- Create: `savevia-ai/tests/test_user_client.py`
- Create: `savevia-ai/tests/test_card_client.py`

**Context:** Python AI service calls Java user/card via httpx. Always forward the inbound user's JWT in `Authorization` header. Default timeout matches current Java Feign defaults (10s read / 5s connect rounded down to 2s for safety). Network errors raised as `JavaServiceError` so callers can render a user-friendly fallback.

- [ ] **Step 1: Write failing test (base client)**

Create `savevia-ai/tests/test_user_client.py`:
```python
import httpx
import pytest
import respx


@pytest.fixture
def user_client():
    from app.clients.user_client import UserServiceClient

    return UserServiceClient(base_url="http://user-test:8081", jwt_token="abc.def.ghi")


@respx.mock
async def test_get_user_cards_returns_parsed_json(user_client):
    route = respx.get("http://user-test:8081/api/v1/users/42/cards").mock(
        return_value=httpx.Response(200, json=[{"id": 1, "cardName": "TD Cash"}]),
    )
    cards = await user_client.get_user_cards(user_id=42)
    assert route.called
    assert cards == [{"id": 1, "cardName": "TD Cash"}]
    assert route.calls.last.request.headers["Authorization"] == "Bearer abc.def.ghi"


@respx.mock
async def test_get_user_cards_raises_on_5xx(user_client):
    from app.clients._base import JavaServiceError

    respx.get("http://user-test:8081/api/v1/users/42/cards").mock(
        return_value=httpx.Response(503),
    )
    with pytest.raises(JavaServiceError) as exc:
        await user_client.get_user_cards(user_id=42)
    assert exc.value.status_code == 503


@respx.mock
async def test_get_user_cards_raises_on_timeout(user_client):
    respx.get("http://user-test:8081/api/v1/users/42/cards").mock(
        side_effect=httpx.TimeoutException("timeout"),
    )
    from app.clients._base import JavaServiceError

    with pytest.raises(JavaServiceError) as exc:
        await user_client.get_user_cards(user_id=42)
    assert "timeout" in str(exc.value).lower()


@respx.mock
async def test_get_user_memory_returns_list(user_client):
    respx.get("http://user-test:8081/api/v1/memory/users/42").mock(
        return_value=httpx.Response(200, json=[{"id": 1, "content": "likes Costco"}]),
    )
    memory = await user_client.get_user_memory(user_id=42)
    assert memory == [{"id": 1, "content": "likes Costco"}]


@respx.mock
async def test_get_chat_history_returns_list(user_client):
    respx.get(
        "http://user-test:8081/api/v1/chat/conversations/conv-1/messages"
    ).mock(return_value=httpx.Response(200, json=[{"role": "user", "content": "hi"}]))
    msgs = await user_client.get_chat_history(conversation_id="conv-1")
    assert msgs == [{"role": "user", "content": "hi"}]
```

Create `savevia-ai/tests/test_card_client.py`:
```python
import httpx
import pytest
import respx


@pytest.fixture
def card_client():
    from app.clients.card_client import CardServiceClient

    return CardServiceClient(base_url="http://card-test:8082", jwt_token="abc.def.ghi")


@respx.mock
async def test_search_cards(card_client):
    respx.get("http://card-test:8082/api/v1/cards/search").mock(
        return_value=httpx.Response(
            200, json=[{"id": 1, "cardName": "Costco Mastercard"}]
        ),
    )
    cards = await card_client.search_cards(query="costco", category=None)
    assert cards[0]["cardName"] == "Costco Mastercard"


@respx.mock
async def test_get_cards_batch(card_client):
    route = respx.post("http://card-test:8082/api/v1/cards/batch").mock(
        return_value=httpx.Response(
            200, json=[{"id": 1}, {"id": 2}, {"id": 3}]
        ),
    )
    cards = await card_client.get_cards_batch(card_ids=[1, 2, 3])
    assert route.called
    assert len(cards) == 3
    assert route.calls.last.request.read() == b'{"ids":[1,2,3]}'


@respx.mock
async def test_get_card_usage_tips(card_client):
    respx.get("http://card-test:8082/api/v1/cards/5/usage-tips").mock(
        return_value=httpx.Response(200, json=[{"tip": "Use at gas stations"}]),
    )
    tips = await card_client.get_card_usage_tips(card_id=5)
    assert tips[0]["tip"] == "Use at gas stations"
```

- [ ] **Step 2: Run — fails on import**

```bash
uv run pytest tests/test_user_client.py tests/test_card_client.py -v
```
Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement base client**

Create `savevia-ai/app/clients/__init__.py` (empty file).

Create `savevia-ai/app/clients/_base.py`:
```python
from typing import Any

import httpx

from app.core.config import get_settings


class JavaServiceError(Exception):
    def __init__(self, service: str, status_code: int | None, message: str):
        super().__init__(f"[{service}] {message}")
        self.service = service
        self.status_code = status_code
        self.message = message


class BaseJavaClient:
    """Async HTTP client base for calls to Java services."""

    service_name: str = "unknown"

    def __init__(self, base_url: str, jwt_token: str):
        settings = get_settings()
        self._base_url = base_url.rstrip("/")
        self._jwt_token = jwt_token
        self._timeout = httpx.Timeout(
            settings.http_timeout_seconds,
            connect=settings.http_connect_timeout_seconds,
        )

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {self._jwt_token}",
                "Accept": "application/json",
            },
            timeout=self._timeout,
        )

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        try:
            async with self._client() as c:
                r = await c.get(path, params=params)
                self._raise_for_status(r)
                return r.json()
        except httpx.TimeoutException as e:
            raise JavaServiceError(self.service_name, None, f"timeout: {e}") from e
        except httpx.RequestError as e:
            raise JavaServiceError(self.service_name, None, f"network error: {e}") from e

    async def _post(self, path: str, json: dict[str, Any] | None = None) -> Any:
        try:
            async with self._client() as c:
                r = await c.post(path, json=json)
                self._raise_for_status(r)
                return r.json()
        except httpx.TimeoutException as e:
            raise JavaServiceError(self.service_name, None, f"timeout: {e}") from e
        except httpx.RequestError as e:
            raise JavaServiceError(self.service_name, None, f"network error: {e}") from e

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.status_code >= 400:
            try:
                body = response.json()
                msg = body.get("message") or body.get("error") or response.text
            except Exception:
                msg = response.text
            raise JavaServiceError(self.service_name, response.status_code, msg)
```

- [ ] **Step 4: Implement user client**

Create `savevia-ai/app/clients/user_client.py`:
```python
from typing import Any

from app.clients._base import BaseJavaClient


class UserServiceClient(BaseJavaClient):
    service_name = "savevia-user"

    async def get_user_cards(self, user_id: int) -> list[dict[str, Any]]:
        return await self._get(f"/api/v1/users/{user_id}/cards")

    async def get_user_profile(self, user_id: int) -> dict[str, Any]:
        return await self._get(f"/api/v1/users/{user_id}")

    async def get_user_memory(self, user_id: int) -> list[dict[str, Any]]:
        return await self._get(f"/api/v1/memory/users/{user_id}")

    async def get_chat_history(self, conversation_id: str) -> list[dict[str, Any]]:
        return await self._get(f"/api/v1/chat/conversations/{conversation_id}/messages")

    async def get_ai_usage_limit(self, user_id: int) -> dict[str, Any]:
        return await self._get(f"/api/v1/ai-usage/users/{user_id}")
```

- [ ] **Step 5: Implement card client**

Create `savevia-ai/app/clients/card_client.py`:
```python
from typing import Any

from app.clients._base import BaseJavaClient


class CardServiceClient(BaseJavaClient):
    service_name = "savevia-card"

    async def search_cards(
        self,
        query: str | None = None,
        category: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"limit": limit}
        if query:
            params["query"] = query
        if category:
            params["category"] = category
        return await self._get("/api/v1/cards/search", params=params)

    async def get_card(self, card_id: int) -> dict[str, Any]:
        return await self._get(f"/api/v1/cards/{card_id}")

    async def get_cards_batch(self, card_ids: list[int]) -> list[dict[str, Any]]:
        return await self._post("/api/v1/cards/batch", json={"ids": card_ids})

    async def get_card_usage_tips(self, card_id: int) -> list[dict[str, Any]]:
        return await self._get(f"/api/v1/cards/{card_id}/usage-tips")
```

- [ ] **Step 6: Run tests — pass**

```bash
uv run pytest tests/test_user_client.py tests/test_card_client.py -v
```
Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add savevia-ai/
git commit -m "feat(savevia-ai): httpx clients for savevia-user and savevia-card"
```

---

## Task 9: Dockerfile + docker-compose entry

**Files:**
- Create: `savevia-ai/Dockerfile`
- Create: `savevia-ai/.dockerignore`
- Modify: `docker-compose.yml` (repo root)

- [ ] **Step 1: Write `Dockerfile`**

Create `savevia-ai/Dockerfile`:
```dockerfile
FROM python:3.12-slim AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.4 /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# --- deps stage: cache layer for dependencies only ---
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# --- final stage: copy source ---
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

RUN uv sync --frozen --no-dev

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "2"]
```

- [ ] **Step 2: Write `.dockerignore`**

Create `savevia-ai/.dockerignore`:
```
.venv/
__pycache__/
*.py[cod]
.env
.env.local
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/
tests/
docs/
.git/
.gitignore
README.md
```

- [ ] **Step 3: Add `savevia-ai` to `docker-compose.yml`**

Append to `docker-compose.yml` (repo root) **before** the `volumes:` section. The service is commented out so it doesn't break current Java-only workflows — uncomment when ready to run:

```yaml
  # savevia-ai:
  #   build:
  #     context: ./savevia-ai
  #     dockerfile: Dockerfile
  #   container_name: savevia-ai
  #   ports:
  #     - "8002:8002"
  #   environment:
  #     DB_HOST: mysql
  #     DB_PORT: 3306
  #     DB_NAME: ${MYSQL_DATABASE:-savevia}
  #     DB_USER: ${MYSQL_USER:-savevia}
  #     DB_PASSWORD: ${MYSQL_PASSWORD:-savevia123}
  #     REDIS_HOST: redis
  #     REDIS_PORT: 6379
  #     JWT_SECRET: ${JWT_SECRET}
  #     USER_SERVICE_URL: http://host.docker.internal:8081
  #     CARD_SERVICE_URL: http://host.docker.internal:8082
  #     OPENAI_API_KEY: ${OPENAI_API_KEY}
  #     OPENAI_MODEL: ${OPENAI_MODEL:-gpt-4o-mini}
  #     SERVICE_PORT: 8002
  #     ENVIRONMENT: development
  #     LOG_LEVEL: INFO
  #   depends_on:
  #     mysql:
  #       condition: service_healthy
  #     redis:
  #       condition: service_healthy
  #   extra_hosts:
  #     - "host.docker.internal:host-gateway"
```

Note: `USER_SERVICE_URL`/`CARD_SERVICE_URL` use `host.docker.internal` for **dev** so Python in Docker reaches Java running on host. In production these become internal DNS names.

- [ ] **Step 4: Test the Docker build**

```bash
cd savevia-ai
docker build -t savevia-ai:dev .
```
Expected: build succeeds in 2-4 minutes (first build). No errors.

- [ ] **Step 5: Smoke-test the container**

```bash
docker run --rm \
  -e DB_HOST=stub -e DB_PORT=3306 -e DB_NAME=x -e DB_USER=x -e DB_PASSWORD=x \
  -e REDIS_HOST=stub -e REDIS_PORT=6379 \
  -e JWT_SECRET=test-secret-at-least-32-characters-long-xxxx \
  -e USER_SERVICE_URL=http://x -e CARD_SERVICE_URL=http://x \
  -e OPENAI_API_KEY=sk-stub \
  -p 8002:8002 \
  savevia-ai:dev &
sleep 3
curl http://localhost:8002/health
docker stop $(docker ps -lq)
```
Expected: `{"status":"ok","service":"savevia-ai",...}`

- [ ] **Step 6: Commit**

```bash
git add savevia-ai/Dockerfile savevia-ai/.dockerignore docker-compose.yml
git commit -m "feat(savevia-ai): Dockerfile + docker-compose entry (commented out)"
```

---

## Task 10: Alembic init and schema baseline

**Files:**
- Create: `savevia-ai/alembic.ini`
- Create: `savevia-ai/alembic/env.py`
- Create: `savevia-ai/alembic/script.py.mako`
- Create: `savevia-ai/alembic/versions/.gitkeep`

**Context:** All 29 existing SQL migrations under `docker/mysql/init/` already define the schema. We baseline Alembic at the current state — future schema changes go through Alembic (Python service is the only one that needs to track its owned tables, but for safety we baseline the entire DB).

- [ ] **Step 1: Run `alembic init`**

From `savevia-ai/`:
```bash
uv run alembic init alembic
```

This generates `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`, and `alembic/versions/`.

- [ ] **Step 2: Replace `alembic.ini` with our version**

Replace `savevia-ai/alembic.ini` with this (DB URL pulled from env at runtime):
```ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(slug)s

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

- [ ] **Step 3: Replace `alembic/env.py`**

Replace `savevia-ai/alembic/env.py` with:
```python
"""Alembic env — async SQLAlchemy + settings from app.core.config."""
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import get_settings
from app.models import Base  # noqa: F401  — ensures all models register

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Inject DB URL from app settings (sync driver swap for offline mode)
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.db_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.db_url.replace("+aiomysql", "+pymysql"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

- [ ] **Step 4: Keep generated `script.py.mako`** (no changes needed)

- [ ] **Step 5: Add `pymysql` for offline migrations**

`pymysql` is needed for the offline `--sql` mode (synchronous driver). Add to `pyproject.toml` dev dependencies:

Edit `savevia-ai/pyproject.toml` — under `[dependency-groups]` `dev = [...]`, add:
```toml
    "pymysql>=1.1.0",
```

Then sync:
```bash
cd savevia-ai && uv sync
```

- [ ] **Step 6: Generate an empty baseline migration**

Run from `savevia-ai/` (requires `INTEGRATION_TESTS` to be unset and `.env` populated for online mode, or use offline):

```bash
uv run alembic revision -m "baseline_existing_schema"
```

Edit the generated file under `alembic/versions/` so both `upgrade()` and `downgrade()` are empty pass-throughs (the schema is already applied by the 29 SQL files):

```python
"""baseline existing schema

Revision ID: <auto>
Revises:
Create Date: <auto>
"""
from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401

revision = "<auto-generated-id>"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """No-op: schema is established by docker/mysql/init/*.sql.
    Alembic is baselined here for future schema changes only."""
    pass


def downgrade() -> None:
    """No-op."""
    pass
```

- [ ] **Step 7: Verify Alembic at least loads**

```bash
uv run alembic check 2>&1 || true
uv run alembic history
```
Expected: history shows the baseline revision. `check` may fail without a live DB — that's OK for this step.

- [ ] **Step 8: Commit**

```bash
git add savevia-ai/alembic.ini savevia-ai/alembic/ savevia-ai/pyproject.toml savevia-ai/uv.lock
git commit -m "feat(savevia-ai): Alembic init + baseline migration"
```

---

## Task 11: Reverse-engineer SQLAlchemy models for 8 owned tables

**Files:**
- Create: `savevia-ai/app/models/transaction.py`
- Create: `savevia-ai/app/models/saved_result.py`
- Create: `savevia-ai/app/models/bank_connection.py`
- Create: `savevia-ai/app/models/bank_account.py`
- Create: `savevia-ai/app/models/connection_history.py`
- Create: `savevia-ai/app/models/merchant_category.py`
- Create: `savevia-ai/app/models/missed_cashback_report.py`
- Create: `savevia-ai/app/models/user_connection_limit.py`
- Modify: `savevia-ai/app/models/__init__.py`
- Create: `savevia-ai/tests/test_models.py`

**Reference SQL files** (do NOT modify these — read for column definitions):
- `docker/mysql/init/06-v2-transaction-upgrade.sql` — transactions, bank_connections, bank_accounts, merchant_categories
- `docker/mysql/init/07-connection-limits.sql` — user_connection_limits, connection_history
- `docker/mysql/init/saved_results.sql` — saved_results
- `docker/mysql/init/28-merchant-rules.sql` — merchant rules additions
- Read `savevia-optimizer/src/main/java/com/savevia/optimizer/entity/*.java` for Java field mappings (camelCase → snake_case)

**Approach:** Use `sqlacodegen` against a running local MySQL to generate a first draft, then manually polish each file (consistent naming, type hints, relationships).

- [ ] **Step 1: Start local MySQL with existing schema**

From repo root:
```bash
docker compose up -d mysql
sleep 15
docker exec savevia-mysql mysql -uroot -proot123 -e "SHOW TABLES IN savevia;"
```
Expected: lists all tables including `transactions`, `bank_connections`, `bank_accounts`, `saved_results`, `merchant_categories`, `user_connection_limits`, `connection_history`, `missed_cashback_reports`.

- [ ] **Step 2: Install sqlacodegen as dev tool**

```bash
cd savevia-ai
uv add --dev sqlacodegen
```

- [ ] **Step 3: Generate model drafts**

```bash
cd savevia-ai
uv run sqlacodegen --generator declarative \
  "mysql+pymysql://savevia:savevia123@localhost:3306/savevia" \
  --tables transactions,saved_results,bank_connections,bank_accounts,connection_history,merchant_categories,missed_cashback_reports,user_connection_limits \
  > /tmp/raw_models.py
cat /tmp/raw_models.py | head -50
```
Expected: a Python file with `class Transaction(Base): ...` style definitions. Use as reference only.

- [ ] **Step 4: Write the polished `transaction.py`**

Create `savevia-ai/app/models/transaction.py`:
```python
from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    account_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    flinks_transaction_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    merchant: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    mcc: Mapped[str | None] = mapped_column(String(10), nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    transaction_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    card_used_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    best_card_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    actual_cashback: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), default=Decimal("0"))
    optimal_cashback: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), default=Decimal("0"))
    missed_cashback: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), default=Decimal("0"))
    is_analyzed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
```

- [ ] **Step 5: Write `saved_result.py`**

Inspect `docker/mysql/init/saved_results.sql` to confirm columns. Create `savevia-ai/app/models/saved_result.py`:
```python
from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SavedResult(Base):
    __tablename__ = "saved_results"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    best_card_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    cashback_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    result_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )
```

If your `saved_results` SQL has different columns, adjust to match — the sqlacodegen output in `/tmp/raw_models.py` is the source of truth for actual columns.

- [ ] **Step 6: Write `bank_connection.py`**

Create `savevia-ai/app/models/bank_connection.py`:
```python
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import BigInteger, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class BankConnectionStatus(str, PyEnum):
    PENDING = "PENDING"
    CONNECTED = "CONNECTED"
    REFRESHING = "REFRESHING"
    ERROR = "ERROR"
    DISCONNECTED = "DISCONNECTED"


class BankConnection(Base):
    __tablename__ = "bank_connections"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    flinks_login_id: Mapped[str] = mapped_column(String(255), nullable=False)
    institution_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[BankConnectionStatus] = mapped_column(
        Enum(BankConnectionStatus), default=BankConnectionStatus.PENDING, index=True
    )
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )
```

- [ ] **Step 7: Write `bank_account.py`**

Create `savevia-ai/app/models/bank_account.py`:
```python
from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    connection_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    flinks_account_id: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type: Mapped[str] = mapped_column(String(50), default="OTHER")
    account_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    account_number_masked: Mapped[str | None] = mapped_column(String(20), nullable=True)
    institution_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    linked_card_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )
```

- [ ] **Step 8: Write the remaining 4 model files**

Use sqlacodegen output (`/tmp/raw_models.py`) as the column source. For each table, create the file in `savevia-ai/app/models/` following the same pattern as above (typed `mapped_column`, snake_case names, proper SQL types).

Files to create:
- `connection_history.py` (class `ConnectionHistory`)
- `merchant_category.py` (class `MerchantCategory`)
- `missed_cashback_report.py` (class `MissedCashbackReport`)
- `user_connection_limit.py` (class `UserConnectionLimit`)

**For each file**, follow exactly this template — fill column declarations from the sqlacodegen output:

```python
from datetime import datetime  # if needed
from decimal import Decimal    # if needed

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class <Name>(Base):
    __tablename__ = "<table_name>"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    # ... columns from sqlacodegen output, snake_case, typed ...
```

- [ ] **Step 9: Update `app/models/__init__.py` to export all models**

Replace `savevia-ai/app/models/__init__.py` with:
```python
from app.models.base import Base
from app.models.bank_account import BankAccount
from app.models.bank_connection import BankConnection, BankConnectionStatus
from app.models.connection_history import ConnectionHistory
from app.models.merchant_category import MerchantCategory
from app.models.missed_cashback_report import MissedCashbackReport
from app.models.saved_result import SavedResult
from app.models.transaction import Transaction
from app.models.user_connection_limit import UserConnectionLimit

__all__ = [
    "Base",
    "BankAccount",
    "BankConnection",
    "BankConnectionStatus",
    "ConnectionHistory",
    "MerchantCategory",
    "MissedCashbackReport",
    "SavedResult",
    "Transaction",
    "UserConnectionLimit",
]
```

- [ ] **Step 10: Write test asserting models match the live schema**

Create `savevia-ai/tests/test_models.py`:
```python
import os

import pytest
from sqlalchemy import inspect


@pytest.mark.skipif(
    not os.environ.get("INTEGRATION_TESTS"),
    reason="requires running MySQL — set INTEGRATION_TESTS=1 to enable",
)
async def test_all_models_match_live_schema():
    """Verify each declared model maps to a real table with matching columns."""
    from app.core.db import get_engine
    from app.models import (
        BankAccount, BankConnection, ConnectionHistory, MerchantCategory,
        MissedCashbackReport, SavedResult, Transaction, UserConnectionLimit,
    )

    engine = get_engine()
    async with engine.connect() as conn:
        def _check(sync_conn):
            insp = inspect(sync_conn)
            for model in (
                Transaction, SavedResult, BankConnection, BankAccount,
                ConnectionHistory, MerchantCategory, MissedCashbackReport,
                UserConnectionLimit,
            ):
                table = model.__tablename__
                assert insp.has_table(table), f"missing table: {table}"
                live_cols = {c["name"] for c in insp.get_columns(table)}
                model_cols = {c.name for c in model.__table__.columns}
                missing = model_cols - live_cols
                extra = model_cols - live_cols
                assert not missing, f"{table}: model has columns not in DB: {missing}"

        await conn.run_sync(_check)


def test_models_register_with_base():
    from app.models import Base, Transaction, SavedResult

    tablenames = set(Base.metadata.tables.keys())
    assert "transactions" in tablenames
    assert "saved_results" in tablenames
    assert len(tablenames) >= 8
```

- [ ] **Step 11: Run unit test (skip integration)**

```bash
cd savevia-ai
uv run pytest tests/test_models.py -v -k "not test_all_models_match_live_schema"
```
Expected: `test_models_register_with_base` passes.

- [ ] **Step 12: Run integration test against MySQL**

```bash
INTEGRATION_TESTS=1 uv run pytest tests/test_models.py -v
```
Expected: both tests pass. If column mismatches surface, fix the model files to match the live schema (the live schema is authoritative).

- [ ] **Step 13: Commit**

```bash
git add savevia-ai/app/models/ savevia-ai/tests/test_models.py savevia-ai/pyproject.toml savevia-ai/uv.lock
git commit -m "feat(savevia-ai): SQLAlchemy ORM models for 8 owned tables"
```

---

## Task 12: Repository base class

**Files:**
- Create: `savevia-ai/app/repositories/__init__.py`
- Create: `savevia-ai/app/repositories/base.py`
- Create: `savevia-ai/tests/test_repository_base.py`

- [ ] **Step 1: Write failing test**

Create `savevia-ai/tests/test_repository_base.py`:
```python
import os

import pytest


@pytest.mark.skipif(
    not os.environ.get("INTEGRATION_TESTS"),
    reason="requires running MySQL — set INTEGRATION_TESTS=1 to enable",
)
async def test_base_repository_crud_roundtrip():
    """Sanity: create, read, update, delete on saved_results."""
    from decimal import Decimal

    from app.core.db import get_session_factory
    from app.models import SavedResult
    from app.repositories.base import BaseRepository

    factory = get_session_factory()
    async with factory() as session:
        repo: BaseRepository[SavedResult] = BaseRepository(session, SavedResult)

        # CREATE
        item = SavedResult(
            user_id=999_999,
            title="test-row-please-delete",
            category="grocery",
            amount=Decimal("100.00"),
        )
        created = await repo.add(item)
        await session.commit()
        assert created.id is not None

        # READ
        fetched = await repo.get_by_id(created.id)
        assert fetched is not None
        assert fetched.title == "test-row-please-delete"

        # UPDATE (set attribute + commit)
        fetched.title = "updated-title"
        await session.commit()
        again = await repo.get_by_id(created.id)
        assert again is not None
        assert again.title == "updated-title"

        # DELETE
        await repo.delete(again)
        await session.commit()
        gone = await repo.get_by_id(created.id)
        assert gone is None


def test_base_repository_signature():
    import inspect

    from app.repositories.base import BaseRepository

    # Verify the public methods exist with the expected signatures
    assert hasattr(BaseRepository, "add")
    assert hasattr(BaseRepository, "get_by_id")
    assert hasattr(BaseRepository, "delete")
    assert hasattr(BaseRepository, "list")
    assert inspect.iscoroutinefunction(BaseRepository.get_by_id)
```

- [ ] **Step 2: Run — fails on import**

```bash
uv run pytest tests/test_repository_base.py -v -k "not test_base_repository_crud_roundtrip"
```
Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement base**

Create `savevia-ai/app/repositories/__init__.py` (empty file).

Create `savevia-ai/app/repositories/base.py`:
```python
from typing import Any, Generic, TypeVar

from sqlalchemy import delete as sa_delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic CRUD repository. Subclass per-model to add query methods."""

    def __init__(self, session: AsyncSession, model: type[ModelT]):
        self.session = session
        self.model = model

    async def add(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def add_all(self, instances: list[ModelT]) -> list[ModelT]:
        self.session.add_all(instances)
        await self.session.flush()
        return instances

    async def get_by_id(self, id_: Any) -> ModelT | None:
        return await self.session.get(self.model, id_)

    async def list(self, limit: int = 100, offset: int = 0) -> list[ModelT]:
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, instance: ModelT) -> None:
        await self.session.delete(instance)
        await self.session.flush()

    async def delete_by_id(self, id_: Any) -> int:
        stmt = sa_delete(self.model).where(self.model.id == id_)  # type: ignore[attr-defined]
        result = await self.session.execute(stmt)
        return result.rowcount or 0
```

- [ ] **Step 4: Run unit tests**

```bash
uv run pytest tests/test_repository_base.py -v -k "not test_base_repository_crud_roundtrip"
```
Expected: signature test passes.

- [ ] **Step 5: Run integration test (optional)**

```bash
INTEGRATION_TESTS=1 uv run pytest tests/test_repository_base.py -v
```
Expected: full CRUD round-trip succeeds on a real MySQL.

- [ ] **Step 6: Commit**

```bash
git add savevia-ai/app/repositories/ savevia-ai/tests/test_repository_base.py
git commit -m "feat(savevia-ai): BaseRepository with generic CRUD"
```

---

## Task 13: TransactionRepository (translates TransactionMapper.xml)

**Files:**
- Create: `savevia-ai/app/repositories/transaction_repository.py`
- Create: `savevia-ai/tests/test_transaction_repository.py`

**Reference:** `savevia-optimizer/src/main/resources/mapper/TransactionMapper.xml` — translate each `<select>` / `<update>` / `<insert>` to a Python method.

The XML defines these operations:
- `insert(Transaction)` → use base `add`
- `batchInsert(List<Transaction>)` → use base `add_all`
- `updateAnalysis(...)` → update specific fields by id
- `resetAnalysisByUserId(userId)` → bulk clear flags
- `findByUserIdAndDateRange(userId, startDate, endDate)`
- `findUnanalyzedByUserId(userId)`
- `findRecentByUserId(userId, limit)`
- Category aggregation queries

- [ ] **Step 1: Write failing test**

Create `savevia-ai/tests/test_transaction_repository.py`:
```python
import os
from datetime import datetime, timedelta
from decimal import Decimal

import pytest


@pytest.fixture
async def db_session():
    from app.core.db import get_session_factory

    factory = get_session_factory()
    async with factory() as session:
        yield session


@pytest.mark.skipif(
    not os.environ.get("INTEGRATION_TESTS"),
    reason="requires running MySQL — set INTEGRATION_TESTS=1 to enable",
)
async def test_insert_and_find_recent(db_session):
    from app.models import Transaction
    from app.repositories.transaction_repository import TransactionRepository

    repo = TransactionRepository(db_session)
    user_id = 88_888_888

    t = Transaction(
        user_id=user_id,
        amount=Decimal("42.50"),
        merchant="Test Coffee",
        category="DINING",
        transaction_date=datetime.utcnow(),
    )
    await repo.add(t)
    await db_session.commit()

    recent = await repo.find_recent_by_user_id(user_id=user_id, limit=10)
    assert any(x.id == t.id for x in recent)

    # cleanup
    await repo.delete(t)
    await db_session.commit()


@pytest.mark.skipif(
    not os.environ.get("INTEGRATION_TESTS"),
    reason="requires running MySQL",
)
async def test_find_by_date_range(db_session):
    from app.models import Transaction
    from app.repositories.transaction_repository import TransactionRepository

    repo = TransactionRepository(db_session)
    user_id = 88_888_889
    now = datetime.utcnow()

    inside = Transaction(
        user_id=user_id, amount=Decimal("10"), merchant="A",
        transaction_date=now,
    )
    outside = Transaction(
        user_id=user_id, amount=Decimal("20"), merchant="B",
        transaction_date=now - timedelta(days=60),
    )
    await repo.add_all([inside, outside])
    await db_session.commit()

    found = await repo.find_by_user_and_date_range(
        user_id=user_id,
        start=now - timedelta(days=7),
        end=now + timedelta(days=1),
    )
    ids = {t.id for t in found}
    assert inside.id in ids
    assert outside.id not in ids

    await repo.delete(inside)
    await repo.delete(outside)
    await db_session.commit()


def test_repository_signature():
    from app.repositories.transaction_repository import TransactionRepository

    for name in (
        "find_by_user_and_date_range",
        "find_unanalyzed_by_user_id",
        "find_recent_by_user_id",
        "update_analysis",
        "reset_analysis_by_user_id",
        "batch_insert",
    ):
        assert hasattr(TransactionRepository, name), f"missing method: {name}"
```

- [ ] **Step 2: Run — fail on import**

```bash
uv run pytest tests/test_transaction_repository.py -v -k "test_repository_signature"
```
Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement repository**

Create `savevia-ai/app/repositories/transaction_repository.py`:
```python
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Transaction)

    async def find_by_user_and_date_range(
        self,
        user_id: int,
        start: datetime,
        end: datetime,
    ) -> list[Transaction]:
        stmt = (
            select(Transaction)
            .where(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start,
                Transaction.transaction_date < end,
            )
            .order_by(Transaction.transaction_date.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_unanalyzed_by_user_id(self, user_id: int) -> list[Transaction]:
        stmt = select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.is_analyzed.is_(False),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_recent_by_user_id(
        self, user_id: int, limit: int = 50
    ) -> list[Transaction]:
        stmt = (
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.transaction_date.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_analysis(
        self,
        transaction_id: int,
        *,
        best_card_id: int | None,
        actual_cashback: Decimal,
        optimal_cashback: Decimal,
        missed_cashback: Decimal,
        category: str | None,
        is_analyzed: bool = True,
    ) -> int:
        stmt = (
            update(Transaction)
            .where(Transaction.id == transaction_id)
            .values(
                best_card_id=best_card_id,
                actual_cashback=actual_cashback,
                optimal_cashback=optimal_cashback,
                missed_cashback=missed_cashback,
                category=category,
                is_analyzed=is_analyzed,
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount or 0

    async def reset_analysis_by_user_id(self, user_id: int) -> int:
        stmt = (
            update(Transaction)
            .where(Transaction.user_id == user_id)
            .values(
                is_analyzed=False,
                best_card_id=None,
                actual_cashback=None,
                optimal_cashback=None,
                missed_cashback=None,
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount or 0

    async def batch_insert(self, transactions: list[Transaction]) -> list[Transaction]:
        return await self.add_all(transactions)
```

- [ ] **Step 4: Run unit + integration tests**

```bash
uv run pytest tests/test_transaction_repository.py -v -k "test_repository_signature"
INTEGRATION_TESTS=1 uv run pytest tests/test_transaction_repository.py -v
```
Expected: signature test passes always; integration tests pass when MySQL is up.

- [ ] **Step 5: Commit**

```bash
git add savevia-ai/app/repositories/transaction_repository.py savevia-ai/tests/test_transaction_repository.py
git commit -m "feat(savevia-ai): TransactionRepository (translates TransactionMapper.xml)"
```

---

## Task 14: SavedResultRepository (translates SavedResultMapper.xml)

**Files:**
- Create: `savevia-ai/app/repositories/saved_result_repository.py`
- Create: `savevia-ai/tests/test_saved_result_repository.py`

**Reference:** `savevia-optimizer/src/main/resources/mapper/SavedResultMapper.xml` and `savevia-optimizer/src/main/java/com/savevia/optimizer/entity/SavedResult.java`.

Read the XML first to enumerate operations. Typical ops: `insert`, `findByUserId`, `findById`, `deleteByUserIdAndId`.

- [ ] **Step 1: Read the Java mapper to enumerate methods**

```bash
cat savevia-optimizer/src/main/resources/mapper/SavedResultMapper.xml
```

List the `<select>` / `<insert>` / `<update>` / `<delete>` operations to translate.

- [ ] **Step 2: Write failing test**

Create `savevia-ai/tests/test_saved_result_repository.py`:
```python
import os
from decimal import Decimal

import pytest


@pytest.fixture
async def db_session():
    from app.core.db import get_session_factory

    factory = get_session_factory()
    async with factory() as session:
        yield session


def test_repository_signature():
    from app.repositories.saved_result_repository import SavedResultRepository

    for name in ("find_by_user_id", "delete_by_user_and_id"):
        assert hasattr(SavedResultRepository, name), f"missing method: {name}"


@pytest.mark.skipif(
    not os.environ.get("INTEGRATION_TESTS"),
    reason="requires running MySQL — set INTEGRATION_TESTS=1 to enable",
)
async def test_saved_result_crud(db_session):
    from app.models import SavedResult
    from app.repositories.saved_result_repository import SavedResultRepository

    repo = SavedResultRepository(db_session)
    user_id = 77_777_777

    item = SavedResult(
        user_id=user_id,
        title="test-saved",
        category="gas",
        amount=Decimal("80.00"),
    )
    await repo.add(item)
    await db_session.commit()

    items = await repo.find_by_user_id(user_id)
    assert any(i.id == item.id for i in items)

    deleted = await repo.delete_by_user_and_id(user_id=user_id, saved_id=item.id)
    await db_session.commit()
    assert deleted == 1

    after = await repo.find_by_user_id(user_id)
    assert all(i.id != item.id for i in after)
```

- [ ] **Step 3: Run — fail on import**

```bash
uv run pytest tests/test_saved_result_repository.py -v -k "test_repository_signature"
```
Expected: `ModuleNotFoundError`.

- [ ] **Step 4: Implement repository**

Create `savevia-ai/app/repositories/saved_result_repository.py`:
```python
from sqlalchemy import delete as sa_delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.saved_result import SavedResult
from app.repositories.base import BaseRepository


class SavedResultRepository(BaseRepository[SavedResult]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SavedResult)

    async def find_by_user_id(
        self, user_id: int, limit: int = 100
    ) -> list[SavedResult]:
        stmt = (
            select(SavedResult)
            .where(SavedResult.user_id == user_id)
            .order_by(SavedResult.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_user_and_id(self, user_id: int, saved_id: int) -> int:
        stmt = sa_delete(SavedResult).where(
            SavedResult.id == saved_id,
            SavedResult.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.rowcount or 0
```

If `SavedResultMapper.xml` (Step 1) has additional methods beyond these two, add them here following the same pattern. Common candidates: `count_by_user_id`, `find_by_category`, etc. Implement only the methods that actually exist in the Java mapper.

- [ ] **Step 5: Run tests**

```bash
uv run pytest tests/test_saved_result_repository.py -v -k "test_repository_signature"
INTEGRATION_TESTS=1 uv run pytest tests/test_saved_result_repository.py -v
```
Expected: signature test always passes; integration test passes when MySQL is up.

- [ ] **Step 6: Commit**

```bash
git add savevia-ai/app/repositories/saved_result_repository.py savevia-ai/tests/test_saved_result_repository.py
git commit -m "feat(savevia-ai): SavedResultRepository (translates SavedResultMapper.xml)"
```

---

## Task 15: Final verification + foundation README

**Files:**
- Modify: `savevia-ai/README.md`

- [ ] **Step 1: Run the full test suite (unit tests only)**

```bash
cd savevia-ai
uv run pytest -v
```
Expected: all unit tests pass; integration tests marked `skipped`.

- [ ] **Step 2: Run the full test suite with MySQL/Redis up**

```bash
cd ..  # repo root
docker compose up -d mysql redis
sleep 15
cd savevia-ai
INTEGRATION_TESTS=1 uv run pytest -v
```
Expected: all tests pass (unit + integration).

- [ ] **Step 3: Smoke-test the service end-to-end**

```bash
uv run uvicorn app.main:app --port 8002 &
sleep 2
curl http://localhost:8002/health
curl http://localhost:8002/ready
kill %1
```
Expected:
- `/health` returns `{"status":"ok",...}`
- `/ready` returns `{"status":"ready","db":"ok","redis":"ok"}`

- [ ] **Step 4: Run linter**

```bash
uv run ruff check app/ tests/
uv run ruff format --check app/ tests/
```
Expected: no lint errors. If format errors, run `uv run ruff format app/ tests/` and re-run check.

- [ ] **Step 5: Update README with the dev workflow**

Replace `savevia-ai/README.md` with:
```markdown
# savevia-ai

Python rewrite of `savevia-optimizer`. See design spec at
`docs/superpowers/specs/2026-05-23-python-rewrite-design.md`.

## Local dev

### Prerequisites
- Python 3.12+
- uv (https://docs.astral.sh/uv/)
- Docker (for MySQL/Redis)

### Setup
```bash
cd savevia-ai
uv sync
cp .env.example .env  # edit if needed
```

### Start dependencies (from repo root)
```bash
docker compose up -d mysql redis
```

### Run the service
```bash
uv run uvicorn app.main:app --reload --port 8002
```

### Tests
```bash
# unit tests only (fast)
uv run pytest

# full suite incl. integration (needs MySQL + Redis running)
INTEGRATION_TESTS=1 uv run pytest
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

## Endpoints (foundation)
- `GET /health` — liveness
- `GET /ready` — readiness (pings MySQL + Redis)
- `GET /docs` — OpenAPI UI (disabled in production)

Business endpoints arrive in subsequent plans (chat, transactions, etc.).

## Structure
- `app/core/` — config, db, redis, security, logging
- `app/clients/` — HTTP clients for savevia-user and savevia-card
- `app/models/` — SQLAlchemy ORM models (8 owned tables)
- `app/repositories/` — data access (currently: Transaction, SavedResult)
- `app/api/` — FastAPI routers (currently: health)
- `tests/` — pytest test suite
```

- [ ] **Step 6: Commit and tag**

```bash
git add savevia-ai/README.md
git commit -m "docs(savevia-ai): foundation README + dev workflow"
git tag -a savevia-ai-foundation -m "Foundation complete (Phase 0 + Phase 1)"
```

---

## Definition of Done

This plan is complete when:

- [ ] `uv run pytest` passes (all unit tests) from `savevia-ai/`
- [ ] `INTEGRATION_TESTS=1 uv run pytest` passes against local MySQL+Redis
- [ ] `uv run uvicorn app.main:app --port 8002` starts cleanly
- [ ] `curl http://localhost:8002/health` returns ok
- [ ] `curl http://localhost:8002/ready` returns ready when MySQL+Redis are up
- [ ] `docker build -t savevia-ai:dev .` succeeds
- [ ] `uv run ruff check app/ tests/` reports no errors
- [ ] All 8 ORM models exist and match the live MySQL schema (integration test)
- [ ] `TransactionRepository` and `SavedResultRepository` exist with TDD coverage
- [ ] HTTP clients for `savevia-user` and `savevia-card` exist with mocked HTTP tests
- [ ] Alembic baseline migration committed (no-op upgrade/downgrade)
- [ ] Tag `savevia-ai-foundation` exists on the foundation commit

When all the above check out, the foundation is ready for Phase 2 (LangGraph agent + tools + SSE chat).

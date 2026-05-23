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
import structlog
from httpx import ASGITransport, AsyncClient


@pytest.fixture(autouse=True)
def _reset_structlog():
    """Reset structlog defaults between tests to prevent cross-test contamination."""
    structlog.reset_defaults()
    yield
    structlog.reset_defaults()


@pytest.fixture
async def http_client():
    from app.main import create_app

    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

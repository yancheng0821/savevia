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

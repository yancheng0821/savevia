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

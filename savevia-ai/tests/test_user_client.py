"""Tests for UserServiceClient.

Java returns `Result<T>` envelope; we assert the client unwraps to `data`.
Auth is forwarded as `X-User-Id` header (gateway pattern).
"""

import httpx
import pytest
import respx

USER_BASE = "http://user-test:8081"


def _result(data, code: int = 200, message: str = "success") -> dict:
    """Wrap a payload in the Java `Result<T>` envelope shape."""
    return {"code": code, "message": message, "data": data, "timestamp": 1234567890}


@pytest.fixture
def user_client():
    from app.clients.user_client import UserServiceClient

    return UserServiceClient(base_url=USER_BASE)


@respx.mock
async def test_get_user_profile_unwraps_envelope(user_client):
    route = respx.get(f"{USER_BASE}/api/v1/users/me").mock(
        return_value=httpx.Response(
            200, json=_result({"id": 42, "email": "a@b.com", "nickname": "AC"})
        ),
    )
    profile = await user_client.get_user_profile(user_id=42)
    assert profile == {"id": 42, "email": "a@b.com", "nickname": "AC"}
    assert route.calls.last.request.headers["X-User-Id"] == "42"
    # JWT must NOT be sent to internal Java
    assert "Authorization" not in route.calls.last.request.headers


@respx.mock
async def test_get_user_card_ids_returns_list_of_long(user_client):
    """Java endpoint returns Result<List<Long>> — just the IDs, not full DTOs."""
    route = respx.get(f"{USER_BASE}/api/v1/users/me/cards").mock(
        return_value=httpx.Response(200, json=_result([1, 2, 3])),
    )
    ids = await user_client.get_user_card_ids(user_id=42)
    assert ids == [1, 2, 3]
    assert route.calls.last.request.headers["X-User-Id"] == "42"


@respx.mock
async def test_get_ai_usage_limit_unwraps(user_client):
    respx.get(f"{USER_BASE}/api/v1/users/ai-usage").mock(
        return_value=httpx.Response(200, json=_result({"limit": 100, "used": 7, "remaining": 93})),
    )
    usage = await user_client.get_ai_usage_limit(user_id=42)
    assert usage["remaining"] == 93


@respx.mock
async def test_get_chat_history_uses_long_id(user_client):
    route = respx.get(f"{USER_BASE}/api/v1/chat/conversations/9001/messages").mock(
        return_value=httpx.Response(
            200,
            json=_result([{"id": 1, "role": "user", "content": "hi"}]),
        ),
    )
    msgs = await user_client.get_chat_history(conversation_id=9001, user_id=42)
    assert msgs[0]["role"] == "user"
    assert route.calls.last.request.headers["X-User-Id"] == "42"


@respx.mock
async def test_business_error_inside_http_200_raises(user_client):
    """Java may return HTTP 200 with code=429 (e.g. rate limit). We must raise."""
    from app.clients._base import JavaServiceError

    respx.get(f"{USER_BASE}/api/v1/users/ai-usage").mock(
        return_value=httpx.Response(200, json=_result(None, code=429, message="rate limited")),
    )
    with pytest.raises(JavaServiceError) as exc:
        await user_client.get_ai_usage_limit(user_id=42)
    assert exc.value.status_code == 429
    assert "rate limited" in exc.value.message


@respx.mock
async def test_get_retries_on_5xx_then_succeeds(user_client):
    route = respx.get(f"{USER_BASE}/api/v1/users/me/cards").mock(
        side_effect=[
            httpx.Response(503),
            httpx.Response(200, json=_result([1, 2])),
        ],
    )
    ids = await user_client.get_user_card_ids(user_id=42)
    assert ids == [1, 2]
    assert route.call_count == 2


@respx.mock
async def test_get_retries_on_timeout_then_succeeds(user_client):
    route = respx.get(f"{USER_BASE}/api/v1/users/me").mock(
        side_effect=[
            httpx.TimeoutException("first try timed out"),
            httpx.Response(200, json=_result({"id": 42})),
        ],
    )
    profile = await user_client.get_user_profile(user_id=42)
    assert profile["id"] == 42
    assert route.call_count == 2


@respx.mock
async def test_get_5xx_exhausts_retries_raises(user_client):
    from app.clients._base import JavaServiceError

    route = respx.get(f"{USER_BASE}/api/v1/users/me/cards").mock(
        return_value=httpx.Response(503),
    )
    with pytest.raises(JavaServiceError) as exc:
        await user_client.get_user_card_ids(user_id=42)
    assert exc.value.status_code == 503
    assert route.call_count == 2  # original + 1 retry


@respx.mock
async def test_non_json_response_raises_gracefully(user_client):
    from app.clients._base import JavaServiceError

    respx.get(f"{USER_BASE}/api/v1/users/me").mock(
        return_value=httpx.Response(200, text="<html>oh no</html>"),
    )
    with pytest.raises(JavaServiceError) as exc:
        await user_client.get_user_profile(user_id=42)
    assert "non-JSON" in exc.value.message


@respx.mock
async def test_aclose_releases_client(user_client):
    # Force lazy-init of the client
    respx.get(f"{USER_BASE}/api/v1/users/me").mock(
        return_value=httpx.Response(200, json=_result({"id": 42})),
    )
    await user_client.get_user_profile(user_id=42)
    assert user_client._client is not None and not user_client._client.is_closed
    await user_client.aclose()
    assert user_client._client.is_closed


@respx.mock
async def test_persistent_client_reused_across_calls(user_client):
    """Verify the AsyncClient is created once and reused."""
    respx.get(f"{USER_BASE}/api/v1/users/me").mock(
        return_value=httpx.Response(200, json=_result({"id": 42})),
    )
    await user_client.get_user_profile(user_id=42)
    client_after_first = user_client._client
    await user_client.get_user_profile(user_id=42)
    assert user_client._client is client_after_first

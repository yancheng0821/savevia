"""Tests for chat-related additions to UserServiceClient.

Chat quota uses the `/ai-usage/chat/...` family; userId is on the PATH,
not in X-User-Id. Plan-01 baseline tests live in test_user_client.py.
"""

import httpx
import pytest
import respx

from app.clients._base import JavaServiceError

USER_BASE = "http://user-test:8081"


def _result(data, code: int = 200, message: str = "success") -> dict:
    return {"code": code, "message": message, "data": data, "timestamp": 1234567890}


@pytest.fixture
def user_client():
    from app.clients.user_client import UserServiceClient
    return UserServiceClient(base_url=USER_BASE)


# ---- chat quota ---------------------------------------------------------

@respx.mock
async def test_check_can_use_chat_true(user_client):
    route = respx.get(f"{USER_BASE}/api/v1/users/ai-usage/chat/check/42").mock(
        return_value=httpx.Response(200, json=_result(True)),
    )
    assert await user_client.check_can_use_chat(user_id=42) is True
    # path-param endpoint must NOT also send X-User-Id
    assert "X-User-Id" not in route.calls.last.request.headers


@respx.mock
async def test_check_can_use_chat_false(user_client):
    respx.get(f"{USER_BASE}/api/v1/users/ai-usage/chat/check/42").mock(
        return_value=httpx.Response(200, json=_result(False)),
    )
    assert await user_client.check_can_use_chat(user_id=42) is False


@respx.mock
async def test_record_chat_usage_success(user_client):
    respx.post(f"{USER_BASE}/api/v1/users/ai-usage/chat/record/42").mock(
        return_value=httpx.Response(200, json=_result(True)),
    )
    assert await user_client.record_chat_usage(user_id=42) is True


@respx.mock
async def test_record_chat_usage_post_hoc_quota_exceeded_raises(user_client):
    """Java returns HTTP 200 with code=429 if the chat quota just tipped over.
    Base client raises JavaServiceError; caller is responsible for swallowing
    this (the response has already streamed).
    """
    respx.post(f"{USER_BASE}/api/v1/users/ai-usage/chat/record/42").mock(
        return_value=httpx.Response(200, json=_result(False, code=429, message="Chat usage limit exceeded")),
    )
    with pytest.raises(JavaServiceError) as exc:
        await user_client.record_chat_usage(user_id=42)
    assert exc.value.status_code == 429

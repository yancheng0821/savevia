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


# ---- conversation lifecycle --------------------------------------------

@respx.mock
async def test_create_conversation_sends_title_and_x_user_id(user_client):
    route = respx.post(f"{USER_BASE}/api/v1/chat/conversations").mock(
        return_value=httpx.Response(
            200,
            json=_result({
                "id": 9001, "userId": 42, "title": "New Conversation",
                "createdAt": "2026-05-23T10:00:00", "updatedAt": "2026-05-23T10:00:00",
            }),
        ),
    )
    conv = await user_client.create_conversation(user_id=42, title="New Conversation")
    assert conv["id"] == 9001
    assert route.calls.last.request.headers["X-User-Id"] == "42"
    import json as _json
    assert _json.loads(route.calls.last.request.content) == {"title": "New Conversation"}


@respx.mock
async def test_get_conversation_validates_ownership_returns_dict(user_client):
    route = respx.get(f"{USER_BASE}/api/v1/chat/conversations/9001").mock(
        return_value=httpx.Response(200, json=_result({"id": 9001, "userId": 42, "title": "x"})),
    )
    conv = await user_client.get_conversation(user_id=42, conversation_id=9001)
    assert conv["id"] == 9001
    assert route.calls.last.request.headers["X-User-Id"] == "42"


@respx.mock
async def test_get_conversation_not_found_raises(user_client):
    """Java returns code=500 with message 'Conversation not found' when the
    conversation doesn't exist or isn't owned by the caller."""
    respx.get(f"{USER_BASE}/api/v1/chat/conversations/9999").mock(
        return_value=httpx.Response(200, json=_result(None, code=500, message="Conversation not found")),
    )
    with pytest.raises(JavaServiceError) as exc:
        await user_client.get_conversation(user_id=42, conversation_id=9999)
    assert "Conversation not found" in exc.value.message


@respx.mock
async def test_add_message_posts_role_and_content(user_client):
    route = respx.post(f"{USER_BASE}/api/v1/chat/conversations/9001/messages").mock(
        return_value=httpx.Response(
            200,
            json=_result({
                "id": 1, "conversationId": 9001, "role": "user", "content": "hello",
                "createdAt": "2026-05-23T10:00:01",
            }),
        ),
    )
    saved = await user_client.add_message(
        user_id=42, conversation_id=9001, role="user", content="hello",
    )
    assert saved["id"] == 1
    import json as _json
    assert _json.loads(route.calls.last.request.content) == {"role": "user", "content": "hello"}
    assert route.calls.last.request.headers["X-User-Id"] == "42"


@respx.mock
async def test_get_recent_messages_uses_recent_endpoint_with_limit(user_client):
    route = respx.get(f"{USER_BASE}/api/v1/chat/conversations/9001/messages/recent").mock(
        return_value=httpx.Response(
            200,
            json=_result([
                {"id": 1, "role": "user", "content": "hi"},
                {"id": 2, "role": "assistant", "content": "hello!"},
            ]),
        ),
    )
    msgs = await user_client.get_recent_messages(user_id=42, conversation_id=9001, limit=10)
    assert len(msgs) == 2 and msgs[0]["role"] == "user"
    # ?limit=10 must be in the query string
    assert route.calls.last.request.url.params["limit"] == "10"
    assert route.calls.last.request.headers["X-User-Id"] == "42"


@respx.mock
async def test_get_recent_messages_defaults_limit_to_10(user_client):
    route = respx.get(f"{USER_BASE}/api/v1/chat/conversations/9001/messages/recent").mock(
        return_value=httpx.Response(200, json=_result([])),
    )
    await user_client.get_recent_messages(user_id=42, conversation_id=9001)
    assert route.calls.last.request.url.params["limit"] == "10"


# ---- memory context ----------------------------------------------------

@respx.mock
async def test_get_user_memory_context_no_categories(user_client):
    route = respx.get(f"{USER_BASE}/api/v1/internal/memory/42/context").mock(
        return_value=httpx.Response(
            200,
            json=_result({
                "coreMemory": "User prefers cashback.",
                "extendedMemory": None,
                "recentSummaries": [],
                "structuredFacts": {},
                "hasMemory": True,
            }),
        ),
    )
    ctx = await user_client.get_user_memory_context(user_id=42)
    assert ctx["hasMemory"] is True
    assert ctx["coreMemory"].startswith("User")
    # path-param endpoint must NOT also send X-User-Id
    assert "X-User-Id" not in route.calls.last.request.headers
    # no categories => no query param at all
    assert route.calls.last.request.url.params.get("categories") is None


@respx.mock
async def test_get_user_memory_context_with_categories(user_client):
    route = respx.get(f"{USER_BASE}/api/v1/internal/memory/42/context").mock(
        return_value=httpx.Response(
            200,
            json=_result({"coreMemory": "", "hasMemory": False, "recentSummaries": []}),
        ),
    )
    await user_client.get_user_memory_context(
        user_id=42, categories=["spending", "lifestyle"]
    )
    assert route.calls.last.request.url.params["categories"] == "spending,lifestyle"


@respx.mock
async def test_get_user_memory_context_returns_none_friendly_when_no_memory(user_client):
    """Empty/no memory is a valid response — the dict's hasMemory flag tells us."""
    respx.get(f"{USER_BASE}/api/v1/internal/memory/42/context").mock(
        return_value=httpx.Response(
            200,
            json=_result({"hasMemory": False, "recentSummaries": []}),
        ),
    )
    ctx = await user_client.get_user_memory_context(user_id=42)
    assert ctx["hasMemory"] is False


# ---- admin tracking ----------------------------------------------------

@respx.mock
async def test_track_event_sends_body_and_x_user_id(user_client):
    route = respx.post(f"{USER_BASE}/api/v1/admin/track").mock(
        return_value=httpx.Response(200, json=_result(None)),
    )
    await user_client.track_event(event_type="ai_chat", user_id=42)
    import json as _json
    assert _json.loads(route.calls.last.request.content) == {"eventType": "ai_chat"}
    assert route.calls.last.request.headers["X-User-Id"] == "42"


@respx.mock
async def test_track_event_without_user_id_omits_header(user_client):
    route = respx.post(f"{USER_BASE}/api/v1/admin/track").mock(
        return_value=httpx.Response(200, json=_result(None)),
    )
    await user_client.track_event(event_type="ai_chat", user_id=None)
    assert "X-User-Id" not in route.calls.last.request.headers


# ---- memory extraction writeback ---------------------------------------

@respx.mock
async def test_post_extracted_memory_sends_body_and_conversation_id(user_client):
    route = respx.post(f"{USER_BASE}/api/v1/internal/memory/42/extracted").mock(
        return_value=httpx.Response(200, json=_result(None)),
    )
    payload = {
        "identity": {"userType": "new_immigrant"},
        "summary": "test",
    }
    await user_client.post_extracted_memory(
        user_id=42, conversation_id=9001, extraction=payload,
    )
    assert route.calls.last.request.url.params["conversationId"] == "9001"
    assert "X-User-Id" not in route.calls.last.request.headers
    import json as _json
    assert _json.loads(route.calls.last.request.content) == payload


@respx.mock
async def test_post_extracted_memory_without_conversation_id_omits_param(user_client):
    route = respx.post(f"{USER_BASE}/api/v1/internal/memory/42/extracted").mock(
        return_value=httpx.Response(200, json=_result(None)),
    )
    await user_client.post_extracted_memory(
        user_id=42, conversation_id=None, extraction={"summary": "x"},
    )
    assert route.calls.last.request.url.params.get("conversationId") is None

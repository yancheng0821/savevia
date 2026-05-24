"""Tests for the chat router (HTTP / SSE wiring)."""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def app():
    """Build a test FastAPI app with the chat router wired and a fake service."""
    from fastapi import FastAPI
    from app.modules.chat.router import build_chat_router

    class _FakeService:
        async def stream(self, **kwargs):
            yield 'event:message\ndata:{"t":"hi"}\n\n'
            yield "event:done\ndata:\n\n"

    fake_service = _FakeService()
    app = FastAPI()
    app.include_router(build_chat_router(lambda: fake_service))
    return app


@pytest.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test",
    ) as c:
        yield c


async def test_stream_returns_sse_content_type_and_frames(client):
    resp = await client.post(
        "/api/v1/chat/stream",
        headers={"X-User-Id": "42"},
        json={"message": "hi", "locale": "en"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")
    assert resp.headers.get("cache-control") == "no-cache"
    body = resp.text
    assert 'event:message\ndata:{"t":"hi"}\n\n' in body
    assert "event:done" in body


async def test_stream_rejects_missing_user_id_header(client):
    resp = await client.post(
        "/api/v1/chat/stream", json={"message": "hi", "locale": "en"},
    )
    assert resp.status_code == 401


async def test_stream_accepts_camel_case_conversation_id(client):
    resp = await client.post(
        "/api/v1/chat/stream",
        headers={"X-User-Id": "42"},
        json={"message": "hi", "locale": "en", "conversationId": 7777},
    )
    assert resp.status_code == 200


async def test_suggestions_returns_envelope(client):
    resp = await client.get("/api/v1/chat/suggestions?locale=en")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 200 and "data" in body and len(body["data"]) == 4

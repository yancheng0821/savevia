"""Integration smoke test — exercises main.py wiring end-to-end with a
fake agent (no real LLM call)."""

import pytest
import respx
import httpx
from httpx import ASGITransport, AsyncClient


def _result(data, code: int = 200, message: str = "success") -> dict:
    return {"code": code, "message": message, "data": data, "timestamp": 1}


@pytest.fixture(autouse=True)
def _stub_agent(monkeypatch):
    """Replace build_agent() + build_extraction_chain() so the app starts
    without any OpenAI traffic."""
    class _Agent:
        async def astream_events(self, *args, version, config=None):
            from langchain_core.messages import AIMessageChunk
            yield {
                "event": "on_chat_model_stream",
                "data": {"chunk": AIMessageChunk(content="Hi!")},
            }

    class _StubChain:
        async def ainvoke(self, _):
            from app.modules.memory.schema import MemoryExtractionResult
            return MemoryExtractionResult(summary="stub")

    import app.main
    monkeypatch.setattr(app.main, "build_agent", lambda *a, **kw: _Agent())
    monkeypatch.setattr(app.main, "build_extraction_chain", lambda *a, **kw: _StubChain())


@pytest.fixture
async def client():
    from app.main import create_app
    app = create_app()
    # Manually drive the FastAPI lifespan so app.state.chat_service is bound.
    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test",
        ) as c:
            yield c


@respx.mock
async def test_post_stream_full_happy_path(client):
    USER = "http://user-test:8081"
    respx.get(f"{USER}/api/v1/users/ai-usage/chat/check/42").mock(
        return_value=httpx.Response(200, json=_result(True)),
    )
    respx.post(f"{USER}/api/v1/chat/conversations").mock(
        return_value=httpx.Response(200, json=_result(
            {"id": 9001, "userId": 42, "title": "New Conversation"},
        )),
    )
    respx.post(f"{USER}/api/v1/chat/conversations/9001/messages").mock(
        return_value=httpx.Response(200, json=_result(
            {"id": 1, "conversationId": 9001, "role": "user", "content": "hi"},
        )),
    )
    respx.get(f"{USER}/api/v1/users/me/cards").mock(
        return_value=httpx.Response(200, json=_result([])),
    )
    respx.get(f"{USER}/api/v1/chat/conversations/9001/messages/recent").mock(
        return_value=httpx.Response(200, json=_result([])),
    )
    respx.get(f"{USER}/api/v1/internal/memory/42/context").mock(
        return_value=httpx.Response(200, json=_result({"hasMemory": False})),
    )
    respx.post(f"{USER}/api/v1/users/ai-usage/chat/record/42").mock(
        return_value=httpx.Response(200, json=_result(True)),
    )
    respx.post(f"{USER}/api/v1/admin/track").mock(
        return_value=httpx.Response(200, json=_result(None)),
    )

    resp = await client.post(
        "/api/v1/chat/stream",
        headers={"X-User-Id": "42"},
        json={"message": "hi", "locale": "en"},
    )
    body = resp.text
    assert resp.status_code == 200
    assert "event:conversation\ndata:9001\n\n" in body
    assert 'event:message\ndata:{"t":"Hi!"}\n\n' in body
    assert "event:done" in body


async def test_get_suggestions_via_real_app(client):
    resp = await client.get("/api/v1/chat/suggestions?locale=en")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 200 and len(body["data"]) == 4

"""SSE regression suite: replay the recorded Java SSE for each canonical prompt
through Python (with a stubbed LLM that mimics the original turn) and assert
byte-for-byte equality of the resulting SSE stream.

Fixtures must be recorded from a live Java instance — see
`tests/fixtures/sse_replay/README.md`. When `cases.json` is empty (no fixtures
recorded yet), the test is skipped rather than failing.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import respx
import httpx
from httpx import ASGITransport, AsyncClient

FIXTURES = Path(__file__).parent.parent.parent / "fixtures" / "sse_replay"
CASES = json.loads((FIXTURES / "cases.json").read_text())


def _result(data, code: int = 200, message: str = "success") -> dict:
    return {"code": code, "message": message, "data": data, "timestamp": 1}


def _build_stub_agent(case: dict):
    """Build a stub agent whose astream_events yields LangGraph-style events
    mirroring the scripted `stub_llm` sequence for this case."""
    from langchain_core.messages import AIMessageChunk

    events: list[dict] = []
    for step in case["stub_llm"]:
        if step["type"] == "text":
            events.append({
                "event": "on_chat_model_stream",
                "data": {"chunk": AIMessageChunk(content=step["text"])},
            })
        elif step["type"] == "tool_call":
            events.append({
                "event": "on_tool_start",
                "name": step["name"],
                "data": {"input": step.get("args") or {}},
            })
            events.append({
                "event": "on_tool_end",
                "name": step["name"],
                "data": {"output": step.get("output") or {
                    "success": True, "content": "...", "data": None,
                }},
            })

    class _Agent:
        async def astream_events(self, *args, version, config=None):
            for ev in events:
                yield ev
    return _Agent()


@pytest.mark.skipif(not CASES, reason="no fixtures recorded yet (see fixtures/sse_replay/README.md)")
@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
@respx.mock
async def test_sse_byte_match(case, monkeypatch):
    import app.main
    monkeypatch.setattr(app.main, "build_agent", lambda *a, **kw: _build_stub_agent(case))

    USER = "http://user-test:8081"
    respx.get(f"{USER}/api/v1/users/ai-usage/chat/check/{case['user_id']}").mock(
        return_value=httpx.Response(200, json=_result(case.get("quota_allowed", True))),
    )
    respx.post(f"{USER}/api/v1/chat/conversations").mock(
        return_value=httpx.Response(200, json=_result(
            {"id": case.get("conversation_id", 9001), "userId": case["user_id"],
             "title": "New Conversation"},
        )),
    )
    respx.post(
        f"{USER}/api/v1/chat/conversations/{case.get('conversation_id', 9001)}/messages"
    ).mock(return_value=httpx.Response(200, json=_result({"id": 1})))
    respx.get(f"{USER}/api/v1/users/me/cards").mock(
        return_value=httpx.Response(200, json=_result(case.get("user_cards", []))),
    )
    respx.get(
        f"{USER}/api/v1/chat/conversations/{case.get('conversation_id', 9001)}/messages/recent"
    ).mock(return_value=httpx.Response(200, json=_result([])))
    respx.get(f"{USER}/api/v1/internal/memory/{case['user_id']}/context").mock(
        return_value=httpx.Response(200, json=_result({"hasMemory": False})),
    )
    respx.post(f"{USER}/api/v1/users/ai-usage/chat/record/{case['user_id']}").mock(
        return_value=httpx.Response(200, json=_result(True)),
    )
    respx.post(f"{USER}/api/v1/admin/track").mock(
        return_value=httpx.Response(200, json=_result(None)),
    )

    from app.main import create_app
    app = create_app()
    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test",
        ) as c:
            resp = await c.post(
                "/api/v1/chat/stream",
                headers={"X-User-Id": str(case["user_id"])},
                json={
                    "message": case["message"],
                    "locale": case["locale"],
                    "conversationId": case.get("input_conversation_id"),
                },
            )

    actual = resp.text
    expected = (FIXTURES / f"{case['id']}.expected.txt").read_text()
    assert actual.rstrip("\n") == expected.rstrip("\n"), (
        f"\n--- expected ---\n{expected}\n--- actual ---\n{actual}\n"
    )

"""Tests for ChatService orchestration. Covers each branch from the
ChatService.streamResponse contract; LLM streaming is faked via a stub agent.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest


# ---- fakes -------------------------------------------------------------

class _FakeAgent:
    """Yields a scripted sequence of LangGraph-style events."""
    def __init__(self, events: list[dict[str, Any]]):
        self._events = events

    async def astream_events(self, inputs, *, version, config=None):
        for ev in self._events:
            yield ev


def _text_chunk(text: str) -> dict[str, Any]:
    from langchain_core.messages import AIMessageChunk
    return {
        "event": "on_chat_model_stream",
        "data": {"chunk": AIMessageChunk(content=text)},
    }


def _tool_start(name: str, args: dict) -> dict[str, Any]:
    return {
        "event": "on_tool_start",
        "name": name,
        "data": {"input": args},
    }


def _tool_end(name: str, output: dict) -> dict[str, Any]:
    return {
        "event": "on_tool_end",
        "name": name,
        "data": {"output": output},
    }


@pytest.fixture
def fake_clients():
    return AsyncMock(), AsyncMock()


def _conv(id: int = 9001) -> dict:
    return {"id": id, "userId": 42, "title": "x"}


def _build_service(*, user, card, agent):
    from app.modules.chat.service import ChatService
    return ChatService(user_client=user, card_client=card, agent=agent)


async def _collect(stream) -> list[str]:
    return [chunk async for chunk in stream]


# ---- input validation --------------------------------------------------

async def test_empty_message_emits_invalid_input_error(fake_clients):
    user, card = fake_clients
    svc = _build_service(user=user, card=card, agent=_FakeAgent([]))
    frames = await _collect(svc.stream(
        user_id=42, message="", locale="en", conversation_id=None,
    ))
    out = "".join(frames)
    assert "INVALID_INPUT" in out
    user.check_can_use_chat.assert_not_called()


async def test_too_long_message_emits_error(fake_clients):
    user, card = fake_clients
    svc = _build_service(user=user, card=card, agent=_FakeAgent([]))
    frames = await _collect(svc.stream(
        user_id=42, message="x" * 1001, locale="en", conversation_id=None,
    ))
    assert "MESSAGE_TOO_LONG" in "".join(frames)


# ---- quota -------------------------------------------------------------

async def test_quota_exceeded_emits_chat_quota_exceeded(fake_clients):
    user, card = fake_clients
    user.check_can_use_chat.return_value = False
    svc = _build_service(user=user, card=card, agent=_FakeAgent([]))
    frames = await _collect(svc.stream(
        user_id=42, message="hi", locale="en", conversation_id=None,
    ))
    out = "".join(frames)
    assert "CHAT_QUOTA_EXCEEDED" in out
    assert "Monthly chat limit reached" in out


async def test_quota_exceeded_in_chinese_uses_zh_message(fake_clients):
    user, card = fake_clients
    user.check_can_use_chat.return_value = False
    svc = _build_service(user=user, card=card, agent=_FakeAgent([]))
    frames = await _collect(svc.stream(
        user_id=42, message="你好", locale="zh", conversation_id=None,
    ))
    assert "本月对话次数已用完" in "".join(frames)


# ---- conversation lifecycle --------------------------------------------

async def test_creates_new_conversation_when_none_provided(fake_clients):
    user, card = fake_clients
    user.check_can_use_chat.return_value = True
    user.create_conversation.return_value = _conv(9001)
    user.get_user_card_ids.return_value = []
    user.get_recent_messages.return_value = []
    user.get_user_memory_context.return_value = {"hasMemory": False}

    svc = _build_service(
        user=user, card=card,
        agent=_FakeAgent([_text_chunk("hello!")]),
    )
    frames = await _collect(svc.stream(
        user_id=42, message="hi", locale="en", conversation_id=None,
    ))
    out = "".join(frames)
    assert "event:conversation\ndata:9001\n\n" in out
    user.create_conversation.assert_awaited_once()


async def test_uses_existing_conversation_when_valid(fake_clients):
    user, card = fake_clients
    user.check_can_use_chat.return_value = True
    user.get_conversation.return_value = _conv(7777)
    user.get_user_card_ids.return_value = []
    user.get_recent_messages.return_value = []
    user.get_user_memory_context.return_value = {"hasMemory": False}

    svc = _build_service(
        user=user, card=card, agent=_FakeAgent([_text_chunk("hi back")]),
    )
    frames = await _collect(svc.stream(
        user_id=42, message="hi", locale="en", conversation_id=7777,
    ))
    out = "".join(frames)
    assert "event:conversation" not in out
    user.create_conversation.assert_not_called()


async def test_falls_back_to_create_when_existing_conversation_invalid(fake_clients):
    from app.clients._base import JavaServiceError

    user, card = fake_clients
    user.check_can_use_chat.return_value = True
    user.get_conversation.side_effect = JavaServiceError(
        "savevia-user", 500, "Conversation not found", path="/x", method="GET",
    )
    user.create_conversation.return_value = _conv(9001)
    user.get_user_card_ids.return_value = []
    user.get_recent_messages.return_value = []
    user.get_user_memory_context.return_value = {"hasMemory": False}

    svc = _build_service(
        user=user, card=card, agent=_FakeAgent([_text_chunk("ok")]),
    )
    frames = await _collect(svc.stream(
        user_id=42, message="hi", locale="en", conversation_id=9999,
    ))
    out = "".join(frames)
    assert "event:conversation\ndata:9001\n\n" in out
    user.create_conversation.assert_awaited_once()


# ---- agent streaming ---------------------------------------------------

async def test_streams_message_then_done(fake_clients):
    user, card = fake_clients
    user.check_can_use_chat.return_value = True
    user.create_conversation.return_value = _conv()
    user.get_user_card_ids.return_value = []
    user.get_recent_messages.return_value = []
    user.get_user_memory_context.return_value = {"hasMemory": False}

    svc = _build_service(
        user=user, card=card,
        agent=_FakeAgent([_text_chunk("hello "), _text_chunk("world")]),
    )
    frames = await _collect(svc.stream(
        user_id=42, message="hi", locale="en", conversation_id=None,
    ))
    out = "".join(frames)
    assert 'event:message\ndata:{"t":"hello "}\n\n' in out
    assert 'event:message\ndata:{"t":"world"}\n\n' in out
    assert "event:done\ndata:\n\n" in out


async def test_emits_tool_call_and_tool_result_events(fake_clients):
    user, card = fake_clients
    user.check_can_use_chat.return_value = True
    user.create_conversation.return_value = _conv()
    user.get_user_card_ids.return_value = []
    user.get_recent_messages.return_value = []
    user.get_user_memory_context.return_value = {"hasMemory": False}

    tool_output = {"success": True, "content": "ok", "data": {"x": 1}}
    svc = _build_service(
        user=user, card=card,
        agent=_FakeAgent([
            _tool_start("get_user_cards", {}),
            _tool_end("get_user_cards", tool_output),
            _text_chunk("done"),
        ]),
    )
    frames = await _collect(svc.stream(
        user_id=42, message="show my cards", locale="en", conversation_id=None,
    ))
    out = "".join(frames)
    assert 'event:tool_call\ndata:{"name":"get_user_cards","args":{}}\n\n' in out
    assert '"name":"get_user_cards","success":true,"content":"ok","data":{"x":1}' in out


async def test_saves_assistant_message_after_streaming(fake_clients):
    user, card = fake_clients
    user.check_can_use_chat.return_value = True
    user.create_conversation.return_value = _conv()
    user.get_user_card_ids.return_value = []
    user.get_recent_messages.return_value = []
    user.get_user_memory_context.return_value = {"hasMemory": False}

    svc = _build_service(
        user=user, card=card,
        agent=_FakeAgent([_text_chunk("hello "), _text_chunk("world")]),
    )
    await _collect(svc.stream(
        user_id=42, message="hi", locale="en", conversation_id=None,
    ))

    save_calls = user.add_message.await_args_list
    roles_contents = [(c.kwargs.get("role"), c.kwargs.get("content")) for c in save_calls]
    assert ("user", "hi") in roles_contents
    assert ("assistant", "hello world") in roles_contents


async def test_record_chat_usage_called_even_when_quota_429_does_not_propagate(fake_clients):
    from app.clients._base import JavaServiceError

    user, card = fake_clients
    user.check_can_use_chat.return_value = True
    user.create_conversation.return_value = _conv()
    user.get_user_card_ids.return_value = []
    user.get_recent_messages.return_value = []
    user.get_user_memory_context.return_value = {"hasMemory": False}
    user.record_chat_usage.side_effect = JavaServiceError(
        "savevia-user", 429, "Chat usage limit exceeded", path="/x", method="POST",
    )

    svc = _build_service(
        user=user, card=card, agent=_FakeAgent([_text_chunk("hi")]),
    )
    frames = await _collect(svc.stream(
        user_id=42, message="hi", locale="en", conversation_id=None,
    ))
    out = "".join(frames)
    assert "event:done" in out
    assert "INTERNAL_ERROR" not in out


async def test_track_event_failure_does_not_break_stream(fake_clients):
    from app.clients._base import JavaServiceError

    user, card = fake_clients
    user.check_can_use_chat.return_value = True
    user.create_conversation.return_value = _conv()
    user.get_user_card_ids.return_value = []
    user.get_recent_messages.return_value = []
    user.get_user_memory_context.return_value = {"hasMemory": False}
    user.track_event.side_effect = JavaServiceError(
        "savevia-user", 500, "down", path="/x", method="POST",
    )

    svc = _build_service(
        user=user, card=card, agent=_FakeAgent([_text_chunk("hi")]),
    )
    frames = await _collect(svc.stream(
        user_id=42, message="hi", locale="en", conversation_id=None,
    ))
    assert "event:done" in "".join(frames)


async def test_max_iterations_no_text_emits_fallback_then_done(fake_clients):
    """If the agent finishes without emitting any text, emit FALLBACK_MESSAGE."""
    user, card = fake_clients
    user.check_can_use_chat.return_value = True
    user.create_conversation.return_value = _conv()
    user.get_user_card_ids.return_value = []
    user.get_recent_messages.return_value = []
    user.get_user_memory_context.return_value = {"hasMemory": False}

    svc = _build_service(
        user=user, card=card, agent=_FakeAgent([]),
    )
    frames = await _collect(svc.stream(
        user_id=42, message="hi", locale="en", conversation_id=None,
    ))
    out = "".join(frames)
    assert "I apologize" in out
    assert "event:done" in out


async def test_uncaught_exception_emits_internal_error(fake_clients):
    user, card = fake_clients
    user.check_can_use_chat.side_effect = RuntimeError("boom")
    svc = _build_service(user=user, card=card, agent=_FakeAgent([]))
    frames = await _collect(svc.stream(
        user_id=42, message="hi", locale="en", conversation_id=None,
    ))
    assert "INTERNAL_ERROR" in "".join(frames)

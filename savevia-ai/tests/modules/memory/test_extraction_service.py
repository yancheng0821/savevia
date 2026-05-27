"""Tests for ExtractionService orchestration."""

from unittest.mock import AsyncMock

import pytest


def _msg(role: str, content: str) -> dict:
    return {"role": role, "content": content}


@pytest.fixture
def user_client():
    return AsyncMock()


@pytest.fixture
def chain():
    """A chain stub whose ainvoke() returns a canned MemoryExtractionResult."""
    from app.modules.memory.schema import MemoryExtractionResult

    canned = MemoryExtractionResult.model_validate({
        "identity": {"user_type": "student"},
        "summary": "Student user.",
    })
    c = AsyncMock()
    c.ainvoke = AsyncMock(return_value=canned)
    return c


def _build(user_client, chain):
    from app.modules.memory.extraction_service import ExtractionService
    return ExtractionService(user_client=user_client, chain=chain)


async def test_skips_when_fewer_than_four_messages(user_client, chain):
    svc = _build(user_client, chain)
    await svc.extract_and_save(
        user_id=42, conversation_id=9001,
        messages=[_msg("user", "hi"), _msg("assistant", "hello")],
    )
    chain.ainvoke.assert_not_called()
    user_client.post_extracted_memory.assert_not_called()


async def test_runs_chain_and_posts_camelcase_payload(user_client, chain):
    svc = _build(user_client, chain)
    await svc.extract_and_save(
        user_id=42, conversation_id=9001,
        messages=[
            _msg("user", "I'm a student"),
            _msg("assistant", "Got it."),
            _msg("user", "I spend $400 on groceries"),
            _msg("assistant", "Best card is..."),
        ],
    )

    sent = chain.ainvoke.await_args.args[0]
    assert "User: I'm a student" in sent["conversation"]
    assert "Assistant: Got it." in sent["conversation"]

    call = user_client.post_extracted_memory.await_args
    assert call.kwargs["user_id"] == 42
    assert call.kwargs["conversation_id"] == 9001
    payload = call.kwargs["extraction"]
    assert payload["identity"]["userType"] == "student"
    assert payload["summary"] == "Student user."


async def test_swallows_chain_exception(user_client, chain):
    chain.ainvoke = AsyncMock(side_effect=RuntimeError("LLM down"))
    svc = _build(user_client, chain)
    await svc.extract_and_save(
        user_id=42, conversation_id=9001,
        messages=[_msg("user", "a"), _msg("assistant", "b")] * 3,
    )
    user_client.post_extracted_memory.assert_not_called()


async def test_swallows_writeback_exception(user_client, chain):
    from app.clients._base import JavaServiceError

    user_client.post_extracted_memory.side_effect = JavaServiceError(
        "savevia-user", 500, "down", path="/x", method="POST",
    )
    svc = _build(user_client, chain)
    await svc.extract_and_save(
        user_id=42, conversation_id=9001,
        messages=[_msg("user", "a"), _msg("assistant", "b")] * 3,
    )


async def test_omits_conversation_id_when_none(user_client, chain):
    svc = _build(user_client, chain)
    await svc.extract_and_save(
        user_id=42, conversation_id=None,
        messages=[_msg("user", "a"), _msg("assistant", "b")] * 3,
    )
    assert user_client.post_extracted_memory.await_args.kwargs["conversation_id"] is None

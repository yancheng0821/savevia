"""Tests for the per-request tool context."""

import asyncio

import pytest


@pytest.fixture
def fake_clients():
    return object(), object()


def test_get_context_outside_request_raises(fake_clients):
    from app.modules.agent.context import get_tool_context
    with pytest.raises(LookupError):
        get_tool_context()


def test_use_tool_context_sets_and_resets(fake_clients):
    from app.modules.agent.context import get_tool_context, use_tool_context

    uc, cc = fake_clients
    with use_tool_context(user_id=42, locale="zh-CN", user_client=uc, card_client=cc):
        ctx = get_tool_context()
        assert ctx.user_id == 42
        assert ctx.locale == "zh-CN"
        assert ctx.user_client is uc
        assert ctx.card_client is cc

    with pytest.raises(LookupError):
        get_tool_context()


async def test_tool_context_is_isolated_between_concurrent_tasks(fake_clients):
    """Two concurrent requests must not see each other's context."""
    from app.modules.agent.context import get_tool_context, use_tool_context

    uc, cc = fake_clients
    seen: list[int] = []

    async def task(user_id: int) -> None:
        with use_tool_context(user_id=user_id, locale="en", user_client=uc, card_client=cc):
            await asyncio.sleep(0)
            seen.append(get_tool_context().user_id)

    await asyncio.gather(task(1), task(2), task(3))
    assert sorted(seen) == [1, 2, 3]


def test_nested_use_tool_context_restores_outer(fake_clients):
    from app.modules.agent.context import get_tool_context, use_tool_context

    uc, cc = fake_clients
    with use_tool_context(user_id=1, locale="en", user_client=uc, card_client=cc):
        with use_tool_context(user_id=2, locale="zh", user_client=uc, card_client=cc):
            assert get_tool_context().user_id == 2
        assert get_tool_context().user_id == 1

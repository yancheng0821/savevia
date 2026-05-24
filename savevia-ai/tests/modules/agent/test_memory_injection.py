"""Tests for the memory injection helper."""

from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def user_client():
    return AsyncMock()


# ---- determine_extended_categories -------------------------------------

def test_determines_no_categories_for_plain_question():
    from app.modules.agent.memory_injection import determine_extended_categories
    assert determine_extended_categories("Hi") == set()


@pytest.mark.parametrize(
    "msg",
    [
        "How much do I spend on groceries?",
        "What's my monthly budget?",
        "买菜用哪张卡好?",
        "每月加油花多少?",
    ],
)
def test_spending_keyword_triggers_spending_category(msg):
    from app.modules.agent.memory_injection import determine_extended_categories
    assert "spending" in determine_extended_categories(msg)


@pytest.mark.parametrize(
    "msg",
    [
        "Going on a flight to Europe next month",
        "Best card for hotel bookings?",
        "下个月出差用哪张卡?",
        "What car should I get for commute?",
    ],
)
def test_lifestyle_keyword_triggers_lifestyle_category(msg):
    from app.modules.agent.memory_injection import determine_extended_categories
    assert "lifestyle" in determine_extended_categories(msg)


def test_can_trigger_both_categories():
    from app.modules.agent.memory_injection import determine_extended_categories
    cats = determine_extended_categories("How much should I budget for travel?")
    assert cats == {"spending", "lifestyle"}


# ---- format_memory_for_prompt ------------------------------------------

def test_format_returns_empty_when_no_memory():
    from app.modules.agent.memory_injection import format_memory_for_prompt
    assert format_memory_for_prompt({"hasMemory": False}) == ""
    assert format_memory_for_prompt(None) == ""


def test_format_includes_core_extended_and_summaries():
    from app.modules.agent.memory_injection import format_memory_for_prompt

    out = format_memory_for_prompt({
        "hasMemory": True,
        "coreMemory": "[Core] cashback preferred.",
        "extendedMemory": "[Spending] groceries $500/mo.",
        "recentSummaries": ["Talked about TD card", "Asked about travel"],
    })
    assert "USER MEMORY" in out
    assert "[Core] cashback preferred." in out
    assert "[Spending] groceries $500/mo." in out
    assert "[Previous Interactions]" in out
    assert "Talked about TD card" in out
    assert out.rstrip().endswith("preferences and exclusions.")


# ---- build_memory_block (composite) ------------------------------------

async def test_build_memory_block_no_categories_passes_empty_list(user_client):
    from app.modules.agent.memory_injection import build_memory_block

    user_client.get_user_memory_context.return_value = {
        "hasMemory": True, "coreMemory": "ok", "recentSummaries": [],
    }
    block = await build_memory_block(
        user_client=user_client, user_id=42, user_message="hi",
    )
    user_client.get_user_memory_context.assert_awaited_once_with(
        user_id=42, categories=[],
    )
    assert "ok" in block


async def test_build_memory_block_passes_keyword_derived_categories(user_client):
    from app.modules.agent.memory_injection import build_memory_block

    user_client.get_user_memory_context.return_value = {
        "hasMemory": True, "coreMemory": "x", "recentSummaries": [],
    }
    await build_memory_block(
        user_client=user_client, user_id=42, user_message="I travel a lot",
    )
    call = user_client.get_user_memory_context.await_args
    # both 'spending' (travel is in spending set) and 'lifestyle'
    assert set(call.kwargs["categories"]) == {"spending", "lifestyle"}


async def test_build_memory_block_returns_empty_when_no_memory(user_client):
    from app.modules.agent.memory_injection import build_memory_block

    user_client.get_user_memory_context.return_value = {"hasMemory": False}
    assert await build_memory_block(
        user_client=user_client, user_id=42, user_message="hi",
    ) == ""


async def test_build_memory_block_swallows_java_errors_returns_empty(user_client):
    from app.clients._base import JavaServiceError
    from app.modules.agent.memory_injection import build_memory_block

    user_client.get_user_memory_context.side_effect = JavaServiceError(
        "savevia-user", 500, "down", path="/x", method="GET",
    )
    assert await build_memory_block(
        user_client=user_client, user_id=42, user_message="hi",
    ) == ""

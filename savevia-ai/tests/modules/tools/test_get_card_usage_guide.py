"""Tests for the get_card_usage_guide tool."""

from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def fake_clients():
    return AsyncMock(), AsyncMock()


def _bind(user, card, locale: str = "en"):
    from app.modules.agent.context import use_tool_context
    return use_tool_context(
        user_id=42, locale=locale, user_client=user, card_client=card,
    )


async def test_passes_lang_derived_from_locale(fake_clients):
    from app.modules.tools.get_card_usage_guide import get_card_usage_guide

    user, card = fake_clients
    card.get_card_usage_guide.return_value = {"rewardType": "POINTS"}
    with _bind(user, card, locale="zh-CN"):
        await get_card_usage_guide.ainvoke({"card_id": 101})
    card.get_card_usage_guide.assert_awaited_once_with(101, lang="zh")


async def test_friendly_message_when_no_guide(fake_clients):
    from app.modules.tools.get_card_usage_guide import get_card_usage_guide

    user, card = fake_clients
    card.get_card_usage_guide.return_value = None
    with _bind(user, card):
        result = await get_card_usage_guide.ainvoke({"card_id": 101})
    assert result["success"] is True
    assert "No usage guide" in result["content"]


async def test_renders_all_sections_when_present(fake_clients):
    from app.modules.tools.get_card_usage_guide import get_card_usage_guide

    user, card = fake_clients
    card.get_card_usage_guide.return_value = {
        "rewardType": "POINTS",
        "pointProgram": "Aeroplan",
        "pointValue": "1.5",
        "transferPartners": [
            {"name": "Star Alliance", "ratio": "1:1", "value": "1.5 cpp"},
        ],
        "tips": [
            {"title": "Sign-up bonus", "content": "Earn 50K", "tipType": "PERK"},
            {"title": "Travel insurance", "content": "Trip cancel", "tipType": "INSURANCE"},
        ],
    }
    with _bind(user, card):
        result = await get_card_usage_guide.ainvoke({"card_id": 101})
    c = result["content"]
    assert "Aeroplan" in c
    assert "1.5 cents per point" in c
    assert "Star Alliance" in c and "1:1" in c
    assert "Sign-up bonus" in c and "Travel insurance" in c


async def test_returns_error_on_java_failure(fake_clients):
    from app.clients._base import JavaServiceError
    from app.modules.tools.get_card_usage_guide import get_card_usage_guide

    user, card = fake_clients
    card.get_card_usage_guide.side_effect = JavaServiceError(
        "savevia-card", 500, "down", path="/x", method="GET",
    )
    with _bind(user, card):
        result = await get_card_usage_guide.ainvoke({"card_id": 101})
    assert result["success"] is False
    assert "down" in result["content"]

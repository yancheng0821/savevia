"""Tests for the get_user_cards tool."""

from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def fake_clients():
    user = AsyncMock()
    card = AsyncMock()
    return user, card


def _bind_ctx(user, card, user_id: int = 42, locale: str = "en"):
    from app.modules.agent.context import use_tool_context
    return use_tool_context(
        user_id=user_id, locale=locale, user_client=user, card_client=card,
    )


async def test_returns_empty_message_when_user_has_no_cards(fake_clients):
    from app.modules.tools.get_user_cards import get_user_cards

    user, card = fake_clients
    user.get_user_card_ids.return_value = []
    with _bind_ctx(user, card):
        result = await get_user_cards.ainvoke({})
    assert result["success"] is True
    assert "no cards" in result["content"].lower()
    assert result["data"] == []
    card.get_cards_batch.assert_not_called()


async def test_formats_cards_with_bank_name_id_and_rewards(fake_clients):
    from app.modules.tools.get_user_cards import get_user_cards

    user, card = fake_clients
    user.get_user_card_ids.return_value = [101]
    card.get_cards_batch.return_value = [{
        "id": 101, "name": "Cash Visa", "bank": "TD", "cardType": "VISA",
        "annualFee": "0", "baseRewardRate": "0.01",
        "rewardRules": [
            {"category": "GROCERY", "rewardRate": "0.04", "monthlyCapAmount": None},
        ],
        "noFxFee": False,
    }]
    with _bind_ctx(user, card):
        result = await get_user_cards.ainvoke({})
    assert result["success"] is True
    assert "TD Cash Visa" in result["content"]
    assert "ID: 101" in result["content"]
    assert "Grocery" in result["content"] and "4%" in result["content"]
    assert result["data"][0]["id"] == 101


async def test_returns_error_when_user_id_missing(fake_clients):
    from app.modules.tools.get_user_cards import get_user_cards
    result = await get_user_cards.ainvoke({})
    assert result["success"] is False
    assert "User ID" in result["content"] or "context" in result["content"].lower()


async def test_returns_friendly_message_when_java_returns_no_card_details(fake_clients):
    """User has IDs but the card service returned an empty list — treat as no cards."""
    from app.modules.tools.get_user_cards import get_user_cards

    user, card = fake_clients
    user.get_user_card_ids.return_value = [101]
    card.get_cards_batch.return_value = []
    with _bind_ctx(user, card):
        result = await get_user_cards.ainvoke({})
    assert result["success"] is True
    assert "no cards" in result["content"].lower()


async def test_wraps_java_service_error_as_tool_error(fake_clients):
    from app.clients._base import JavaServiceError
    from app.modules.tools.get_user_cards import get_user_cards

    user, card = fake_clients
    user.get_user_card_ids.side_effect = JavaServiceError(
        "savevia-user", 500, "boom", path="/x", method="GET",
    )
    with _bind_ctx(user, card):
        result = await get_user_cards.ainvoke({})
    assert result["success"] is False
    assert "boom" in result["content"]

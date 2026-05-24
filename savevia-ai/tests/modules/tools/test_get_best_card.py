"""Tests for the get_best_card tool."""

from unittest.mock import AsyncMock

import pytest


def _card(*, id: int, name: str, rules: list | None = None, base: str = "0.01") -> dict:
    return {
        "id": id, "name": name, "bank": "TestBank", "annualFee": "0",
        "baseRewardRate": base, "rewardRules": rules or [], "noFxFee": False,
        "cardType": "VISA",
    }


def _rule(cat: str, rate: str, cap: str | None = None) -> dict:
    return {"category": cat, "rewardRate": rate, "monthlyCapAmount": cap}


@pytest.fixture
def fake_clients():
    return AsyncMock(), AsyncMock()


def _bind(user, card):
    from app.modules.agent.context import use_tool_context
    return use_tool_context(user_id=42, locale="en", user_client=user, card_client=card)


async def test_returns_success_with_message_when_user_has_no_cards(fake_clients):
    from app.modules.tools.get_best_card import get_best_card

    user, card = fake_clients
    user.get_user_card_ids.return_value = []
    with _bind(user, card):
        result = await get_best_card.ainvoke({"category": "GROCERY"})
    assert result["success"] is True
    assert "no cards" in result["content"].lower()
    assert result["data"] is None


async def test_returns_error_when_category_missing(fake_clients):
    from app.modules.tools.get_best_card import get_best_card

    user, card = fake_clients
    with _bind(user, card):
        result = await get_best_card.ainvoke({"category": ""})
    assert result["success"] is False


async def test_returns_error_for_invalid_category(fake_clients):
    from app.modules.tools.get_best_card import get_best_card

    user, card = fake_clients
    with _bind(user, card):
        result = await get_best_card.ainvoke({"category": "FAKE"})
    assert result["success"] is False
    assert "Invalid category" in result["content"]


async def test_picks_highest_rate_card_and_lists_others(fake_clients):
    from app.modules.tools.get_best_card import get_best_card

    user, card = fake_clients
    user.get_user_card_ids.return_value = [1, 2]
    card.get_cards_batch.return_value = [
        _card(id=1, name="A", rules=[_rule("GROCERY", "0.02")]),
        _card(id=2, name="B", rules=[_rule("GROCERY", "0.06")]),
    ]
    with _bind(user, card):
        result = await get_best_card.ainvoke({"category": "GROCERY", "amount": 200})
    assert result["success"] is True
    assert result["data"]["bestCardId"] == 2
    from decimal import Decimal
    assert Decimal(str(result["data"]["bestReward"])) == Decimal("12.00")
    assert "B" in result["content"]
    assert "Other cards comparison" in result["content"]


async def test_defaults_amount_to_100_when_omitted(fake_clients):
    from app.modules.tools.get_best_card import get_best_card

    user, card = fake_clients
    user.get_user_card_ids.return_value = [1]
    card.get_cards_batch.return_value = [
        _card(id=1, name="A", rules=[_rule("GROCERY", "0.04")]),
    ]
    with _bind(user, card):
        result = await get_best_card.ainvoke({"category": "GROCERY"})
    from decimal import Decimal
    assert Decimal(str(result["data"]["bestReward"])) == Decimal("4.00")

"""Tests for the calculate_reward tool."""

from unittest.mock import AsyncMock

import pytest


def _card(*, id: int, rules: list | None = None, base: str = "0.01") -> dict:
    return {
        "id": id, "name": "C", "bank": "TestBank", "annualFee": "0",
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


async def test_validates_amount_positive(fake_clients):
    from app.modules.tools.calculate_reward import calculate_reward

    user, card = fake_clients
    with _bind(user, card):
        result = await calculate_reward.ainvoke({
            "card_id": 1, "category": "DINING", "amount": 0,
        })
    assert result["success"] is False
    assert "positive" in result["content"]


async def test_rejects_invalid_category(fake_clients):
    from app.modules.tools.calculate_reward import calculate_reward

    user, card = fake_clients
    with _bind(user, card):
        result = await calculate_reward.ainvoke({
            "card_id": 1, "category": "NOPE", "amount": 100,
        })
    assert result["success"] is False
    assert "Invalid category" in result["content"]


async def test_returns_error_when_card_not_found(fake_clients):
    from app.modules.tools.calculate_reward import calculate_reward

    user, card = fake_clients
    card.get_cards_batch.return_value = []
    with _bind(user, card):
        result = await calculate_reward.ainvoke({
            "card_id": 999, "category": "DINING", "amount": 100,
        })
    assert result["success"] is False
    assert "Card not found" in result["content"]


async def test_calculates_reward_and_returns_data(fake_clients):
    from decimal import Decimal
    from app.modules.tools.calculate_reward import calculate_reward

    user, card = fake_clients
    card.get_cards_batch.return_value = [
        _card(id=1, rules=[_rule("DINING", "0.04")]),
    ]
    with _bind(user, card):
        result = await calculate_reward.ainvoke({
            "card_id": 1, "category": "DINING", "amount": 250,
        })
    assert result["success"] is True
    assert Decimal(str(result["data"]["rewardAmount"])) == Decimal("10.00")
    assert result["data"]["category"] == "DINING"
    assert "$10.00" in result["content"]


async def test_mentions_monthly_cap_when_present(fake_clients):
    from app.modules.tools.calculate_reward import calculate_reward

    user, card = fake_clients
    card.get_cards_batch.return_value = [
        _card(id=1, rules=[_rule("GROCERY", "0.06", cap="500")]),
    ]
    with _bind(user, card):
        result = await calculate_reward.ainvoke({
            "card_id": 1, "category": "GROCERY", "amount": 100,
        })
    assert "monthly spending cap of $500" in result["content"]

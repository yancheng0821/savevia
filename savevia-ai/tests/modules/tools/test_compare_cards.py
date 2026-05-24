"""Tests for the compare_cards tool."""

from unittest.mock import AsyncMock

import pytest


def _card(*, id: int, name: str, bank: str = "TD", annual_fee: str = "0",
          rules: list | None = None, base: str = "0.01") -> dict:
    return {
        "id": id, "name": name, "bank": bank, "annualFee": annual_fee,
        "baseRewardRate": base, "rewardRules": rules or [], "noFxFee": False,
        "cardType": "VISA",
    }


def _rule(cat: str, rate: str) -> dict:
    return {"category": cat, "rewardRate": rate, "monthlyCapAmount": None}


@pytest.fixture
def fake_clients():
    return AsyncMock(), AsyncMock()


def _bind(user, card):
    from app.modules.agent.context import use_tool_context
    return use_tool_context(user_id=42, locale="en", user_client=user, card_client=card)


async def test_requires_at_least_two_cards(fake_clients):
    from app.modules.tools.compare_cards import compare_cards

    user, card = fake_clients
    with _bind(user, card):
        result = await compare_cards.ainvoke({"card_ids": [1]})
    assert result["success"] is False
    assert "at least 2" in result["content"]


async def test_rejects_more_than_five_cards(fake_clients):
    from app.modules.tools.compare_cards import compare_cards

    user, card = fake_clients
    with _bind(user, card):
        result = await compare_cards.ainvoke({"card_ids": [1, 2, 3, 4, 5, 6]})
    assert result["success"] is False
    assert "more than 5" in result["content"]


async def test_uses_default_categories_when_omitted(fake_clients):
    from app.modules.tools.compare_cards import compare_cards

    user, card = fake_clients
    card.get_cards_batch.return_value = [
        _card(id=1, name="A", rules=[_rule("DINING", "0.04")]),
        _card(id=2, name="B", rules=[_rule("DINING", "0.02")]),
    ]
    with _bind(user, card):
        result = await compare_cards.ainvoke({"card_ids": [1, 2]})
    assert result["success"] is True
    cats = {row["category"] for row in result["data"]["comparison"]}
    assert {"DINING", "GROCERY", "GAS", "TRAVEL", "ONLINE_SHOPPING", "OTHER"} <= cats


async def test_marks_winner_per_category_with_check_mark(fake_clients):
    from app.modules.tools.compare_cards import compare_cards

    user, card = fake_clients
    card.get_cards_batch.return_value = [
        _card(id=1, name="A", rules=[_rule("DINING", "0.04")]),
        _card(id=2, name="B", rules=[_rule("DINING", "0.02")]),
    ]
    with _bind(user, card):
        result = await compare_cards.ainvoke({"card_ids": [1, 2], "categories": ["DINING"]})
    content = result["content"]
    assert "**4%** ✓" in content
    assert "**2%** ✓" not in content


async def test_summary_lists_best_categories_per_card(fake_clients):
    from app.modules.tools.compare_cards import compare_cards

    user, card = fake_clients
    card.get_cards_batch.return_value = [
        _card(id=1, name="A", rules=[_rule("DINING", "0.04"), _rule("GROCERY", "0.02")]),
        _card(id=2, name="B", rules=[_rule("DINING", "0.02"), _rule("GROCERY", "0.06")]),
    ]
    with _bind(user, card):
        result = await compare_cards.ainvoke({
            "card_ids": [1, 2], "categories": ["DINING", "GROCERY"],
        })
    content = result["content"]
    assert "Best for Dining" in content
    assert "Best for Grocery" in content


async def test_returns_error_when_java_returns_empty(fake_clients):
    from app.modules.tools.compare_cards import compare_cards

    user, card = fake_clients
    card.get_cards_batch.return_value = []
    with _bind(user, card):
        result = await compare_cards.ainvoke({"card_ids": [1, 2]})
    assert result["success"] is False
    assert "Could not find cards" in result["content"]


async def test_invalid_categories_in_list_are_ignored(fake_clients):
    """Java logs warning and continues with the valid ones."""
    from app.modules.tools.compare_cards import compare_cards

    user, card = fake_clients
    card.get_cards_batch.return_value = [
        _card(id=1, name="A"), _card(id=2, name="B"),
    ]
    with _bind(user, card):
        result = await compare_cards.ainvoke({
            "card_ids": [1, 2], "categories": ["DINING", "NOPE", "GAS"],
        })
    assert result["success"] is True
    cats = {row["category"] for row in result["data"]["comparison"]}
    assert cats == {"DINING", "GAS"}

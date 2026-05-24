"""Tests for the search_cards tool."""

from unittest.mock import AsyncMock

import pytest


def _card(*, id: int, bank: str, name: str = "X", annual_fee: str = "0",
          base: str = "0.01", rules: list | None = None, no_fx: bool = False,
          card_type: str = "VISA") -> dict:
    return {
        "id": id, "bank": bank, "name": name, "annualFee": annual_fee,
        "baseRewardRate": base, "rewardRules": rules or [], "noFxFee": no_fx,
        "cardType": card_type,
    }


def _rule(cat: str, rate: str, cap: str | None = None) -> dict:
    return {"category": cat, "rewardRate": rate, "monthlyCapAmount": cap}


@pytest.fixture
def fake_clients():
    return AsyncMock(), AsyncMock()


def _bind(user, card, user_id: int = 42):
    from app.modules.agent.context import use_tool_context
    return use_tool_context(
        user_id=user_id, locale="en", user_client=user, card_client=card,
    )


async def test_excludes_users_existing_cards(fake_clients):
    from app.modules.tools.search_cards import search_cards

    user, card = fake_clients
    user.get_user_card_ids.return_value = [1]
    card.list_all_cards.return_value = [
        _card(id=1, bank="TD"),
        _card(id=2, bank="CIBC"),
    ]
    with _bind(user, card):
        result = await search_cards.ainvoke({})
    assert result["success"] is True
    ids = [c["id"] for c in result["data"]["cards"]]
    assert 1 not in ids and 2 in ids


async def test_filters_by_bank_case_insensitive(fake_clients):
    from app.modules.tools.search_cards import search_cards

    user, card = fake_clients
    user.get_user_card_ids.return_value = []
    card.list_all_cards.return_value = [
        _card(id=1, bank="TD"), _card(id=2, bank="CIBC"), _card(id=3, bank="td bank"),
    ]
    with _bind(user, card):
        result = await search_cards.ainvoke({"bank": "td"})
    ids = {c["id"] for c in result["data"]["cards"]}
    assert ids == {1, 3}


async def test_filters_no_annual_fee(fake_clients):
    from app.modules.tools.search_cards import search_cards

    user, card = fake_clients
    user.get_user_card_ids.return_value = []
    card.list_all_cards.return_value = [
        _card(id=1, bank="TD", annual_fee="0"),
        _card(id=2, bank="TD", annual_fee="120"),
    ]
    with _bind(user, card):
        result = await search_cards.ainvoke({"no_annual_fee": True})
    ids = {c["id"] for c in result["data"]["cards"]}
    assert ids == {1}


async def test_filters_no_fx_fee(fake_clients):
    from app.modules.tools.search_cards import search_cards

    user, card = fake_clients
    user.get_user_card_ids.return_value = []
    card.list_all_cards.return_value = [
        _card(id=1, bank="TD", no_fx=True), _card(id=2, bank="TD", no_fx=False),
    ]
    with _bind(user, card):
        result = await search_cards.ainvoke({"no_fx_fee": True})
    assert {c["id"] for c in result["data"]["cards"]} == {1}


async def test_filters_by_network_via_card_type_substring(fake_clients):
    from app.modules.tools.search_cards import search_cards

    user, card = fake_clients
    user.get_user_card_ids.return_value = []
    card.list_all_cards.return_value = [
        _card(id=1, bank="TD", card_type="VISA Infinite"),
        _card(id=2, bank="TD", card_type="World Elite MASTERCARD"),
        _card(id=3, bank="AMEX", card_type="AMEX Cobalt"),
    ]
    with _bind(user, card):
        result = await search_cards.ainvoke({"network": "VISA"})
    assert {c["id"] for c in result["data"]["cards"]} == {1}


async def test_filters_by_category_requires_min_rate_and_sorts_desc(fake_clients):
    from app.modules.tools.search_cards import search_cards

    user, card = fake_clients
    user.get_user_card_ids.return_value = []
    card.list_all_cards.return_value = [
        _card(id=1, bank="A", rules=[_rule("GROCERY", "0.03")]),
        _card(id=2, bank="B", rules=[_rule("GROCERY", "0.06")]),
        _card(id=3, bank="C", rules=[_rule("GROCERY", "0.005")]),
        _card(id=4, bank="D"),
    ]
    with _bind(user, card):
        result = await search_cards.ainvoke({"category": "GROCERY"})
    ids = [c["id"] for c in result["data"]["cards"]]
    assert ids == [2, 1]


async def test_no_category_sorts_by_base_rate_desc(fake_clients):
    from app.modules.tools.search_cards import search_cards

    user, card = fake_clients
    user.get_user_card_ids.return_value = []
    card.list_all_cards.return_value = [
        _card(id=1, bank="A", base="0.01"),
        _card(id=2, bank="B", base="0.02"),
        _card(id=3, bank="C", base="0.015"),
    ]
    with _bind(user, card):
        result = await search_cards.ainvoke({})
    assert [c["id"] for c in result["data"]["cards"]] == [2, 3, 1]


async def test_caps_results_at_5(fake_clients):
    from app.modules.tools.search_cards import search_cards

    user, card = fake_clients
    user.get_user_card_ids.return_value = []
    card.list_all_cards.return_value = [_card(id=i, bank=f"B{i}") for i in range(1, 11)]
    with _bind(user, card):
        result = await search_cards.ainvoke({})
    assert len(result["data"]["cards"]) == 5
    assert result["data"]["totalFound"] == 10
    assert result["data"]["showing"] == 5


async def test_invalid_category_is_ignored_not_an_error(fake_clients):
    """Java logs a warning and treats the filter as 'no category' — match that."""
    from app.modules.tools.search_cards import search_cards

    user, card = fake_clients
    user.get_user_card_ids.return_value = []
    card.list_all_cards.return_value = [_card(id=1, bank="A", base="0.01")]
    with _bind(user, card):
        result = await search_cards.ainvoke({"category": "NOT_REAL"})
    assert result["success"] is True
    assert len(result["data"]["cards"]) == 1

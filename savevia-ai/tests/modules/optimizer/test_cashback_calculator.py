"""Tests for CashbackCalculator (Python port of Java algorithm)."""

from decimal import Decimal

import pytest


def _rule(category: str, rate: str, cap: str | None = None) -> dict:
    return {
        "category": category,
        "rewardRate": rate,
        "monthlyCapAmount": cap,
    }


def _card(base: str | None = None, rules: list[dict] | None = None) -> dict:
    return {
        "id": 1,
        "name": "Test",
        "bank": "TestBank",
        "annualFee": "0",
        "baseRewardRate": base,
        "rewardRules": rules or [],
        "noFxFee": False,
        "cardType": "VISA",
    }


def test_rate_picks_matching_rule_over_base():
    from app.modules.optimizer.cashback_calculator import get_reward_rate
    from app.modules.locale.categories import SpendingCategory

    card = _card(base="0.01", rules=[_rule("DINING", "0.04")])
    assert get_reward_rate(card, SpendingCategory.DINING) == Decimal("0.04")


def test_rate_falls_back_to_base_when_no_rule_for_category():
    from app.modules.optimizer.cashback_calculator import get_reward_rate
    from app.modules.locale.categories import SpendingCategory

    card = _card(base="0.02", rules=[_rule("DINING", "0.04")])
    assert get_reward_rate(card, SpendingCategory.GAS) == Decimal("0.02")


def test_rate_falls_back_to_one_percent_when_neither_rule_nor_base():
    from app.modules.optimizer.cashback_calculator import get_reward_rate
    from app.modules.locale.categories import SpendingCategory

    card = _card(base=None, rules=[])
    assert get_reward_rate(card, SpendingCategory.OTHER) == Decimal("0.01")


def test_calculate_reward_simple_multiplication_with_2dp_rounding():
    from app.modules.optimizer.cashback_calculator import calculate_reward
    from app.modules.locale.categories import SpendingCategory

    card = _card(base="0.04", rules=[])
    assert calculate_reward(card, SpendingCategory.OTHER, Decimal("123.45")) == Decimal("4.94")


def test_calculate_reward_applies_monthly_cap_clamp():
    from app.modules.optimizer.cashback_calculator import calculate_reward
    from app.modules.locale.categories import SpendingCategory

    card = _card(rules=[_rule("GROCERY", "0.06", cap="500")])
    assert calculate_reward(card, SpendingCategory.GROCERY, Decimal("800")) == Decimal("30.00")


def test_calculate_reward_below_cap_no_clamp():
    from app.modules.optimizer.cashback_calculator import calculate_reward
    from app.modules.locale.categories import SpendingCategory

    card = _card(rules=[_rule("GROCERY", "0.06", cap="500")])
    assert calculate_reward(card, SpendingCategory.GROCERY, Decimal("100")) == Decimal("6.00")


def test_get_monthly_cap_returns_decimal_when_present():
    from app.modules.optimizer.cashback_calculator import get_monthly_cap
    from app.modules.locale.categories import SpendingCategory

    card = _card(rules=[_rule("GROCERY", "0.06", cap="500")])
    assert get_monthly_cap(card, SpendingCategory.GROCERY) == Decimal("500")


def test_get_monthly_cap_returns_none_when_absent():
    from app.modules.optimizer.cashback_calculator import get_monthly_cap
    from app.modules.locale.categories import SpendingCategory

    card = _card(rules=[_rule("GROCERY", "0.06")])
    assert get_monthly_cap(card, SpendingCategory.GROCERY) is None


@pytest.mark.parametrize(
    "rate,expected",
    [
        (Decimal("0.04"), "4%"),
        (Decimal("0.025"), "2.5%"),
        (Decimal("0.01"), "1%"),
        (Decimal("0.0625"), "6.3%"),
        (Decimal("0"), "0%"),
        (None, "0%"),
    ],
)
def test_format_rate_as_percentage(rate, expected):
    from app.modules.optimizer.cashback_calculator import format_rate_as_percentage
    assert format_rate_as_percentage(rate) == expected

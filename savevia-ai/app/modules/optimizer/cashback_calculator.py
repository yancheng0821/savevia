"""Local cashback math — mirrors com.savevia.optimizer.algorithm.CashbackCalculator.

All money/rate values use `decimal.Decimal` for byte-identical results vs
Java's BigDecimal. Inputs are the JSON dicts returned by CardServiceClient
(rates and caps arrive as strings — we cast on read).
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from app.modules.locale.categories import SpendingCategory

_DEFAULT_RATE = Decimal("0.01")
_TWO_DP = Decimal("0.01")
_ONE_DP = Decimal("0.1")
_PERCENT = Decimal("100")


def _as_decimal(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _rules(card: dict[str, Any]) -> list[dict[str, Any]]:
    return card.get("rewardRules") or []


def get_reward_rate(card: dict[str, Any], category: SpendingCategory) -> Decimal:
    """First matching rule's rewardRate; fall back to baseRewardRate; final fallback 0.01."""
    for rule in _rules(card):
        if rule.get("category") == category.name:
            rate = _as_decimal(rule.get("rewardRate"))
            if rate is not None:
                return rate
            break
    base = _as_decimal(card.get("baseRewardRate"))
    return base if base is not None else _DEFAULT_RATE


def get_monthly_cap(card: dict[str, Any], category: SpendingCategory) -> Decimal | None:
    """First matching rule's monthlyCapAmount; None otherwise."""
    for rule in _rules(card):
        if rule.get("category") == category.name:
            return _as_decimal(rule.get("monthlyCapAmount"))
    return None


def calculate_reward(
    card: dict[str, Any], category: SpendingCategory, amount: Decimal
) -> Decimal:
    """amount * rate, rounded HALF_UP to 2dp. Clamps to cap * rate if cap > 0 and exceeded."""
    rate = get_reward_rate(card, category)
    reward = (amount * rate).quantize(_TWO_DP, rounding=ROUND_HALF_UP)
    cap = get_monthly_cap(card, category)
    if cap is not None and cap > 0:
        max_reward = cap * rate
        if reward > max_reward:
            reward = max_reward
    return reward


def format_rate_as_percentage(rate: Decimal | None) -> str:
    """rate * 100, 1dp HALF_UP, trailing zeros stripped, suffixed with '%'.

    Examples: 0.04 -> '4%', 0.025 -> '2.5%', 0.0625 -> '6.3%', None -> '0%'.
    """
    if rate is None:
        return "0%"
    pct = (rate * _PERCENT).quantize(_ONE_DP, rounding=ROUND_HALF_UP)
    s = format(pct, "f").rstrip("0").rstrip(".")
    if s == "" or s == "-":
        s = "0"
    return s + "%"

"""LangChain tool: calculate_reward — reward $ + rate for a card/category/amount.

Mirrors com.savevia.optimizer.agent.tools.CalculateRewardTool.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from langchain_core.tools import tool

from app.clients._base import JavaServiceError
from app.modules.agent.context import get_tool_context
from app.modules.locale.categories import SpendingCategory
from app.modules.optimizer.cashback_calculator import (
    calculate_reward as calc_reward,
    format_rate_as_percentage,
    get_monthly_cap,
    get_reward_rate,
)
from app.modules.tools._format import card_header


def _ok(content: str, data: Any) -> dict[str, Any]:
    return {"success": True, "content": content, "data": data}


def _err(content: str) -> dict[str, Any]:
    return {"success": False, "content": content, "data": None}


@tool
async def calculate_reward(
    card_id: int,
    category: str,
    amount: float,
) -> dict[str, Any]:
    """Calculate the reward/cashback amount for spending a specific amount in
    a category using a specific credit card. Returns the reward amount and rate.

    Args:
        card_id: The ID of the credit card.
        category: Spending category name (one of SpendingCategory enum names).
        amount: Spending amount in dollars (must be > 0).
    """
    try:
        ctx = get_tool_context()
    except LookupError:
        return _err("Tool context unavailable")

    if card_id is None:
        return _err("card_id is required")
    if amount is None or amount <= 0:
        return _err("amount must be a positive number")
    cat = SpendingCategory.from_str(category)
    if cat is None:
        return _err(
            f"Invalid category: {category}. Valid categories are: "
            + ", ".join(SpendingCategory.names())
        )

    try:
        cards = await ctx.card_client.get_cards_batch([card_id])
    except JavaServiceError as e:
        return _err(f"Failed to calculate reward: {e.message}")
    if not cards:
        return _err(f"Card not found with ID: {card_id}")

    card = cards[0]
    spend = Decimal(str(amount))
    rate = get_reward_rate(card, cat)
    reward = calc_reward(card, cat, spend)
    cap = get_monthly_cap(card, cat)

    lines = [
        f"**{card_header(card)}**",
        f"Spending: ${amount:.2f} on {cat.display_name}",
        f"Reward Rate: {format_rate_as_percentage(rate)}",
        f"Reward Amount: **${reward}**",
    ]
    if cap is not None and cap > 0:
        lines.append(f"Note: This category has a monthly spending cap of ${cap}")

    data = {
        "cardId": card_id,
        "cardName": card_header(card),
        "category": cat.name,
        "amount": float(spend),
        "rewardRate": str(rate),
        "rewardAmount": str(reward),
        "monthlyCap": str(cap) if cap is not None else None,
    }
    return _ok("\n".join(lines), data)

"""LangChain tool: get_best_card — best card in user's wallet for a category.

Mirrors com.savevia.optimizer.agent.tools.GetBestCardTool.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from langchain_core.tools import tool

from app.clients._base import JavaServiceError
from app.modules.agent.context import get_tool_context
from app.modules.locale.categories import SpendingCategory
from app.modules.optimizer.cashback_calculator import (
    calculate_reward,
    format_rate_as_percentage,
    get_reward_rate,
)
from app.modules.tools._format import card_header


def _ok(content: str, data: Any) -> dict[str, Any]:
    return {"success": True, "content": content, "data": data}


def _err(content: str) -> dict[str, Any]:
    return {"success": False, "content": content, "data": None}


@tool
async def get_best_card(
    category: str,
    amount: float = 100.0,
) -> dict[str, Any]:
    """Find the best credit card for a specific spending category from the user's cards.
    Returns the card with the highest reward rate for that category, along with
    the expected reward.

    Args:
        category: Spending category name (one of SpendingCategory enum names).
        amount: Optional spending amount in dollars; defaults to 100.
    """
    try:
        ctx = get_tool_context()
    except LookupError:
        return _err("Tool context unavailable")

    if not category:
        return _err("category is required")
    cat = SpendingCategory.from_str(category)
    if cat is None:
        return _err(f"Invalid category: {category}")

    try:
        card_ids = await ctx.user_client.get_user_card_ids(ctx.user_id)
        if not card_ids:
            return _ok(
                f"User has no cards. Cannot determine best card for {cat.display_name}.",
                None,
            )
        cards = await ctx.card_client.get_cards_batch(card_ids)
        if not cards:
            return _ok(
                f"User has no cards. Cannot determine best card for {cat.display_name}.",
                None,
            )
    except JavaServiceError as e:
        return _err(f"Failed to find best card: {e.message}")

    spend = Decimal(str(amount))
    best_card: dict | None = None
    best_rate = Decimal("0")
    best_reward = Decimal("0")
    per_card: list[dict] = []

    for c in cards:
        rate = get_reward_rate(c, cat)
        reward = calculate_reward(c, cat, spend)
        per_card.append({
            "cardId": c.get("id"),
            "cardName": card_header(c),
            "rewardRate": str(rate),
            "rewardAmount": str(reward),
        })
        if rate > best_rate:
            best_rate = rate
            best_reward = reward
            best_card = c

    lines = [f"**Best Card for {cat.display_name}**\n"]
    if best_card is not None:
        lines.append(f"🏆 **{card_header(best_card)}**")
        lines.append(f"Reward Rate: {format_rate_as_percentage(best_rate)}")
        lines.append(
            f"Expected Reward on ${spend:.2f}: **${best_reward}**\n"
        )
        if len(cards) > 1:
            lines.append("Other cards comparison:")
            for c in cards:
                if c.get("id") == best_card.get("id"):
                    continue
                rate = get_reward_rate(c, cat)
                reward = calculate_reward(c, cat, spend)
                lines.append(
                    f"- {card_header(c)}: {format_rate_as_percentage(rate)} → ${reward}"
                )

    data = {
        "category": cat.name,
        "amount": float(spend),
        "bestCardId": best_card.get("id") if best_card else None,
        "bestCardName": card_header(best_card) if best_card else None,
        "bestRate": str(best_rate),
        "bestReward": str(best_reward),
        "allCards": per_card,
    }
    return _ok("\n".join(lines), data)

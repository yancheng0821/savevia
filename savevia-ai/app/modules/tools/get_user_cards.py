"""LangChain tool: get_user_cards — list the cards the user has added.

Mirrors com.savevia.optimizer.agent.tools.GetUserCardsTool.
"""

from __future__ import annotations

from typing import Any

from langchain_core.tools import tool

from app.clients._base import JavaServiceError
from app.modules.agent.context import get_tool_context
from app.modules.locale.categories import SpendingCategory
from app.modules.tools._format import card_header, format_rate


def _ok(content: str, data: Any) -> dict[str, Any]:
    return {"success": True, "content": content, "data": data}


def _err(content: str) -> dict[str, Any]:
    return {"success": False, "content": content, "data": None}


def _format_cards(cards: list[dict[str, Any]]) -> str:
    lines = [f"User has {len(cards)} card(s):\n"]
    for card in cards:
        lines.append(f"- **{card_header(card)}** (ID: {card.get('id')})")
        lines.append(f"  Type: {card.get('cardType')}")
        lines.append(f"  Annual Fee: ${card.get('annualFee')}")
        lines.append(f"  Base Reward: {format_rate(card.get('baseRewardRate'))}")
        rules = card.get("rewardRules") or []
        if rules:
            parts: list[str] = []
            for rule in rules:
                cat = SpendingCategory.from_str(rule.get("category"))
                if cat and rule.get("rewardRate") is not None:
                    parts.append(f"{cat.display_name} {format_rate(rule.get('rewardRate'))}")
            if parts:
                lines.append(f"  Category Rewards: {', '.join(parts)}")
        lines.append("")
    return "\n".join(lines)


@tool
async def get_user_cards() -> dict[str, Any]:
    """Get the list of credit cards that the user has added to their wallet.
    Use this to see what cards the user owns before making recommendations."""
    try:
        ctx = get_tool_context()
    except LookupError:
        return _err("User ID is required (no tool context bound)")

    try:
        card_ids = await ctx.user_client.get_user_card_ids(ctx.user_id)
        if not card_ids:
            return _ok("The user has no cards added to their wallet yet.", [])
        cards = await ctx.card_client.get_cards_batch(card_ids)
        if not cards:
            return _ok("The user has no cards added to their wallet yet.", [])
        return _ok(_format_cards(cards), cards)
    except JavaServiceError as e:
        return _err(f"Failed to retrieve user cards: {e.message}")

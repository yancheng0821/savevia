"""LangChain tool: compare_cards — side-by-side rate table for 2-5 cards.

Mirrors com.savevia.optimizer.agent.tools.CompareCardsTool.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from langchain_core.tools import tool

from app.clients._base import JavaServiceError
from app.modules.agent.context import get_tool_context
from app.modules.locale.categories import SpendingCategory
from app.modules.optimizer.cashback_calculator import (
    format_rate_as_percentage,
    get_reward_rate,
)
from app.modules.tools._format import card_header

DEFAULT_CATEGORIES = [
    SpendingCategory.DINING,
    SpendingCategory.GROCERY,
    SpendingCategory.GAS,
    SpendingCategory.TRAVEL,
    SpendingCategory.ONLINE_SHOPPING,
    SpendingCategory.OTHER,
]


def _ok(content: str, data: Any) -> dict[str, Any]:
    return {"success": True, "content": content, "data": data}


def _err(content: str) -> dict[str, Any]:
    return {"success": False, "content": content, "data": None}


@tool
async def compare_cards(
    card_ids: list[int],
    categories: list[str] | None = None,
) -> dict[str, Any]:
    """Compare multiple credit cards side by side, showing their reward rates
    across different spending categories. Useful for helping users decide which
    card to use.

    Args:
        card_ids: List of card IDs to compare (2-5 cards).
        categories: Optional list of SpendingCategory enum names to compare.
            Defaults to DINING, GROCERY, GAS, TRAVEL, ONLINE_SHOPPING, OTHER.
    """
    try:
        ctx = get_tool_context()
    except LookupError:
        return _err("Tool context unavailable")

    if not card_ids or len(card_ids) < 2:
        return _err("Need at least 2 cards to compare")
    if len(card_ids) > 5:
        return _err("Cannot compare more than 5 cards at once")

    cats: list[SpendingCategory] = []
    if categories:
        for name in categories:
            c = SpendingCategory.from_str(name)
            if c is not None:
                cats.append(c)
    if not cats:
        cats = list(DEFAULT_CATEGORIES)

    try:
        cards = await ctx.card_client.get_cards_batch(card_ids)
    except JavaServiceError as e:
        return _err(f"Failed to compare cards: {e.message}")
    if not cards:
        return _err("Could not find cards with the provided IDs")

    lines: list[str] = ["## Card Comparison\n", "### Cards"]
    for c in cards:
        lines.append(
            f"- **{card_header(c)}** (ID: {c.get('id')}) - Annual Fee: ${c.get('annualFee')}"
        )
    lines.append("\n### Reward Rates by Category\n")

    header_cells = ["Category"] + [c.get("name", "") for c in cards]
    lines.append("| " + " | ".join(header_cells) + " |")
    lines.append("|" + "----------|" * (len(cards) + 1))

    comparison: list[dict[str, Any]] = []
    for cat in cats:
        rates = {c.get("id"): get_reward_rate(c, cat) for c in cards}
        max_rate = max(rates.values())
        row_cells = [cat.display_name]
        for c in cards:
            rate = rates[c.get("id")]
            cell = format_rate_as_percentage(rate)
            if rate == max_rate and len(cards) > 1:
                row_cells.append(f"**{cell}** ✓")
            else:
                row_cells.append(cell)
        lines.append("| " + " | ".join(row_cells) + " |")
        comparison.append({
            "category": cat.name,
            "rates": {str(k): str(v) for k, v in rates.items()},
            "bestRate": str(max_rate),
        })

    lines.append("\n### Summary")
    for c in cards:
        best_cats: list[str] = []
        for cat in cats:
            rate = get_reward_rate(c, cat)
            others_max = max(
                (get_reward_rate(o, cat) for o in cards if o.get("id") != c.get("id")),
                default=Decimal("0"),
            )
            if rate >= others_max and rate > 0:
                best_cats.append(cat.display_name)
        if best_cats:
            lines.append(f"- **{card_header(c)}**: Best for {', '.join(best_cats)}")
        else:
            lines.append(f"- **{card_header(c)}**: Not the best for any compared category")

    data = {
        "cards": [
            {"id": c.get("id"), "name": card_header(c), "annualFee": c.get("annualFee")}
            for c in cards
        ],
        "comparison": comparison,
    }
    return _ok("\n".join(lines), data)

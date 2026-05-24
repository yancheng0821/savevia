"""LangChain tool: search_cards — discover new cards (filtered + sorted).

Mirrors com.savevia.optimizer.agent.tools.SearchCardsTool. There is no
/search endpoint on Java's card service, so we fetch the catalog and
filter in Python.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Literal

from langchain_core.tools import tool

from app.clients._base import JavaServiceError
from app.modules.agent.context import get_tool_context
from app.modules.locale.categories import SpendingCategory
from app.modules.tools._format import card_header, format_rate

MAX_RESULTS = 5
MIN_CATEGORY_RATE = Decimal("0.01")


def _ok(content: str, data: Any) -> dict[str, Any]:
    return {"success": True, "content": content, "data": data}


def _err(content: str) -> dict[str, Any]:
    return {"success": False, "content": content, "data": None}


def _has_good_rate_for_category(card: dict, category: SpendingCategory) -> bool:
    for rule in card.get("rewardRules") or []:
        if rule.get("category") == category.name:
            rate = rule.get("rewardRate")
            if rate is not None and Decimal(str(rate)) >= MIN_CATEGORY_RATE:
                return True
    return False


def _category_rate(card: dict, category: SpendingCategory) -> Decimal:
    for rule in card.get("rewardRules") or []:
        if rule.get("category") == category.name and rule.get("rewardRate") is not None:
            return Decimal(str(rule["rewardRate"]))
    base = card.get("baseRewardRate")
    return Decimal(str(base)) if base else Decimal("0")


def _base_rate(card: dict) -> Decimal:
    base = card.get("baseRewardRate")
    return Decimal(str(base)) if base else Decimal("0")


def _format_results(
    filtered: list[dict],
    shown: list[dict],
    bank: str | None,
    category: SpendingCategory | None,
    no_annual_fee: bool | None,
    no_fx_fee: bool | None,
    network: str | None,
) -> str:
    lines = ["## Search Results\n"]

    filters: list[str] = []
    if bank: filters.append(f"Bank: {bank}")
    if category: filters.append(f"Category: {category.display_name}")
    if no_annual_fee: filters.append("No Annual Fee")
    if no_fx_fee: filters.append("No FX Fee")
    if network: filters.append(f"Network: {network}")
    if filters:
        lines.append(f"**Filters**: {', '.join(filters)}\n")

    suffix = f" (showing top {MAX_RESULTS})" if len(filtered) > MAX_RESULTS else ""
    lines.append(f"Found **{len(filtered)}** cards{suffix}:\n")

    if not shown:
        lines.append("No cards found matching the criteria.")
    else:
        for c in shown:
            lines.append(f"### {card_header(c)} (ID: {c.get('id')})")
            lines.append(f"- **Annual Fee**: ${c.get('annualFee')}")
            lines.append(f"- **Type**: {c.get('cardType')}")
            if c.get("noFxFee"):
                lines.append("- **No Foreign Transaction Fee**: Yes")
            rules = c.get("rewardRules") or []
            if rules:
                lines.append("- **Rewards**:")
                for rule in rules:
                    cat = SpendingCategory.from_str(rule.get("category"))
                    if not cat: continue
                    rate = format_rate(rule.get("rewardRate"))
                    line = f"  - {cat.display_name}: {rate}"
                    cap = rule.get("monthlyCapAmount")
                    if cap and Decimal(str(cap)) > 0:
                        line += f" (cap: ${cap}/mo)"
                    lines.append(line)
            elif c.get("baseRewardRate"):
                lines.append(f"- **Base Rate**: {format_rate(c.get('baseRewardRate'))} on all purchases")
            lines.append("")
    return "\n".join(lines)


@tool
async def search_cards(
    bank: str | None = None,
    category: str | None = None,
    no_annual_fee: bool | None = None,
    no_fx_fee: bool | None = None,
    network: Literal["VISA", "MASTERCARD", "AMEX"] | None = None,
) -> dict[str, Any]:
    """Search for credit cards the user doesn't have, filtered by various criteria.
    Use when the user asks about new cards to apply for, or wants recommendations
    for cards with specific features (e.g., no annual fee, travel rewards, etc.).

    Args:
        bank: Filter by bank name substring (e.g., 'TD', 'CIBC', 'AMEX').
        category: Find cards with good rewards in this spending category
            (one of SpendingCategory enum names). Use for 'travel cards' etc.
        no_annual_fee: If True, only show cards with $0 annual fee.
        no_fx_fee: If True, only show cards with no foreign transaction fee.
        network: Filter by card network (VISA / MASTERCARD / AMEX).
            NOT for reward type — use `category` for that.
    """
    try:
        ctx = get_tool_context()
    except LookupError:
        return _err("Tool context unavailable")

    cat = SpendingCategory.from_str(category)

    try:
        all_cards = await ctx.card_client.list_all_cards()
        owned_ids = set(await ctx.user_client.get_user_card_ids(ctx.user_id) or [])
    except JavaServiceError as e:
        return _err(f"Failed to search cards: {e.message}")

    def keep(c: dict) -> bool:
        if c.get("id") in owned_ids: return False
        if bank and bank.upper() not in (c.get("bank") or "").upper(): return False
        if no_annual_fee:
            fee = c.get("annualFee")
            if fee is None or Decimal(str(fee)) != 0: return False
        if no_fx_fee and not c.get("noFxFee"): return False
        if network:
            ct = (c.get("cardType") or "").upper()
            if network.upper() not in ct: return False
        if cat is not None and not _has_good_rate_for_category(c, cat): return False
        return True

    filtered = [c for c in all_cards if keep(c)]
    filtered.sort(
        key=(lambda c: _category_rate(c, cat)) if cat else (lambda c: _base_rate(c)),
        reverse=True,
    )
    shown = filtered[:MAX_RESULTS]

    data = {
        "totalFound": len(filtered),
        "showing": len(shown),
        "cards": [
            {
                "id": c.get("id"),
                "name": card_header(c),
                "annualFee": c.get("annualFee"),
                "cardType": c.get("cardType"),
                "noFxFee": c.get("noFxFee"),
            }
            for c in shown
        ],
    }
    content = _format_results(filtered, shown, bank, cat, no_annual_fee, no_fx_fee, network)
    return _ok(content, data)

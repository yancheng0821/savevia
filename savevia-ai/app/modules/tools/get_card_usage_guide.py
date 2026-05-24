"""LangChain tool: get_card_usage_guide — usage tips, partners, points value.

Mirrors com.savevia.optimizer.agent.tools.GetCardUsageGuideTool.
"""

from __future__ import annotations

from typing import Any

from langchain_core.tools import tool

from app.clients._base import JavaServiceError
from app.modules.agent.context import get_tool_context
from app.modules.locale.mapping import locale_to_lang


def _ok(content: str, data: Any) -> dict[str, Any]:
    return {"success": True, "content": content, "data": data}


def _err(content: str) -> dict[str, Any]:
    return {"success": False, "content": content, "data": None}


@tool
async def get_card_usage_guide(card_id: int) -> dict[str, Any]:
    """Get usage tips and guide for a specific credit card.
    Includes reward redemption tips, transfer partners, point value, and best
    practices. Use when users ask how to best use or maximize a specific card.

    Args:
        card_id: The ID of the credit card to get usage guide for.
    """
    try:
        ctx = get_tool_context()
    except LookupError:
        return _err("Tool context unavailable")

    if card_id is None:
        return _err("card_id is required")

    lang = locale_to_lang(ctx.locale)
    try:
        guide = await ctx.card_client.get_card_usage_guide(card_id, lang=lang)
    except JavaServiceError as e:
        return _err(f"Failed to get card usage guide: {e.message}")
    if not guide:
        return _ok(f"No usage guide available for this card (ID: {card_id}).", None)

    lines = ["## Card Usage Guide\n"]
    if guide.get("rewardType"):
        lines.append(f"**Reward Type**: {guide['rewardType']}")
    if guide.get("pointProgram"):
        lines.append(f"**Point Program**: {guide['pointProgram']}")
    if guide.get("pointValue"):
        lines.append(f"**Point Value**: {guide['pointValue']} cents per point")
    lines.append("")

    partners = guide.get("transferPartners") or []
    if partners:
        lines.append("### Transfer Partners")
        for p in partners:
            line = f"- **{p.get('name')}**"
            if p.get("ratio"):
                line += f" ({p['ratio']})"
            if p.get("value"):
                line += f" - Value: {p['value']}"
            lines.append(line)
        lines.append("")

    tips = guide.get("tips") or []
    if tips:
        lines.append("### Usage Tips")
        for t in tips:
            lines.append(f"**{t.get('title')}**")
            lines.append(t.get("content", ""))
            lines.append("")

    content = "\n".join(lines).rstrip() + "\n"
    if len(content.strip()) < 30:
        content = "No detailed usage guide available for this card.\n"

    data = {
        "cardId": card_id,
        "rewardType": guide.get("rewardType"),
        "pointProgram": guide.get("pointProgram"),
        "pointValue": guide.get("pointValue"),
        "transferPartners": partners,
        "tips": tips,
    }
    return _ok(content, data)

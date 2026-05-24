"""Memory injection — fetches user memory from Java, formats it for the
system prompt. Mirrors com.savevia.optimizer.service.MemoryInjectionStrategy.

Phase 2: memory READ is on Java (MemoryController). Phase 3 will port
extraction; this module's HTTP call swaps to the new endpoint there.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.clients._base import JavaServiceError
from app.core.logging import get_logger

if TYPE_CHECKING:
    from app.clients.user_client import UserServiceClient

_log = get_logger("savevia-ai.memory_injection")

_SPENDING_KEYWORDS = {
    "买", "消费", "花", "支出", "月", "每月", "多少钱", "预算",
    "超市", "加油", "吃饭", "餐厅", "网购", "旅行", "出差",
    "spend", "buy", "purchase", "cost", "budget", "monthly",
    "grocery", "groceries", "gas", "fuel", "dining", "restaurant",
    "online", "shopping", "travel", "trip",
}

_LIFESTYLE_KEYWORDS = {
    "旅行", "出差", "出国", "机票", "酒店", "孩子", "小孩", "宠物",
    "通勤", "开车", "地铁", "公交",
    "travel", "trip", "flight", "hotel", "abroad", "vacation",
    "kids", "children", "family", "pet", "dog", "cat",
    "commute", "drive", "car", "transit", "subway", "bus",
}


def determine_extended_categories(user_message: str | None) -> set[str]:
    """Return the set of extended-memory categories triggered by keywords in the
    user message. Empty set if no keywords match."""
    cats: set[str] = set()
    if not user_message:
        return cats
    lower = user_message.lower()
    if any(kw.lower() in lower for kw in _SPENDING_KEYWORDS):
        cats.add("spending")
    if any(kw.lower() in lower for kw in _LIFESTYLE_KEYWORDS):
        cats.add("lifestyle")
    return cats


def format_memory_for_prompt(ctx: dict[str, Any] | None) -> str:
    """Render a MemoryContextDTO dict as the multi-line prompt block, or empty
    string if no memory is available."""
    if not ctx or not ctx.get("hasMemory"):
        return ""

    lines = ["\nUSER MEMORY (Long-term context about this user):"]
    core = ctx.get("coreMemory")
    if core:
        lines.append(core)
    ext = ctx.get("extendedMemory")
    if ext:
        lines.append(ext)
    summaries = ctx.get("recentSummaries") or []
    if summaries:
        lines.append("[Previous Interactions]")
        for s in summaries:
            lines.append(f"- {s}")
    lines.append("")
    lines.append(
        "Use this context to provide personalized recommendations. "
        "Respect user's preferences and exclusions."
    )
    lines.append("")
    return "\n".join(lines)


async def build_memory_block(
    *,
    user_client: "UserServiceClient",
    user_id: int,
    user_message: str,
) -> str:
    """Fetch + format memory block in one call. Returns '' on any failure."""
    cats = sorted(determine_extended_categories(user_message))
    try:
        ctx = await user_client.get_user_memory_context(
            user_id=user_id, categories=cats,
        )
    except JavaServiceError as e:
        _log.warning(
            "memory_context_fetch_failed",
            user_id=user_id, error=e.message,
        )
        return ""
    return format_memory_for_prompt(ctx)

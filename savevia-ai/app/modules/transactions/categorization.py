"""Merchant-name → SpendingCategory mapping.

Mirrors com.savevia.optimizer.service.TransactionCategorizationService.
The Java service caches an in-memory pattern list (CopyOnWriteArrayList)
loaded from the `merchant_categories` table; we mirror that with a list
loaded by `refresh_patterns()` and re-loadable on demand.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.repositories.merchant_category_repository import MerchantCategoryRepository

_DEFAULT_CATEGORY = "OTHER"


@dataclass(frozen=True)
class CategorizationResult:
    category: str
    confidence: float


class CategorizationService:
    """Pattern-matching categorizer. NOT thread-safe across processes; each
    Python worker keeps its own cache. Java's CopyOnWriteArrayList provides
    intra-process thread safety; in asyncio there's only one writer at a time,
    so a plain list suffices.
    """

    def __init__(self, *, merchant_repository: "MerchantCategoryRepository"):
        self._repo = merchant_repository
        # Each entry is (pattern_upper, category, priority).
        self._patterns: list[tuple[str, str, int]] = []

    async def refresh_patterns(self) -> None:
        """Reload patterns from the DB. Java does this in @PostConstruct;
        we call it once at app startup from main.py's lifespan."""
        rows = await self._repo.find_all_active()
        self._patterns = [
            (
                (row.merchant_pattern or "").upper(),
                row.category,
                row.priority or 0,
            )
            for row in rows
            if row.merchant_pattern
        ]

    def categorize(self, merchant_name: str | None) -> str:
        """Return the category for `merchant_name`, or 'OTHER' if no pattern matches."""
        if not merchant_name:
            return _DEFAULT_CATEGORY
        upper = merchant_name.upper()
        # Patterns are already ordered by priority DESC (see repository).
        for pattern_upper, category, _priority in self._patterns:
            if pattern_upper in upper:
                return category
        return _DEFAULT_CATEGORY

    def categorize_with_confidence(
        self, merchant_name: str | None
    ) -> CategorizationResult:
        """Categorize + emit a 0.0-1.0 confidence (mirrors Java's heuristic:
        priority/200 + 0.5, capped at 1.0). Unmatched names get 0.3."""
        if not merchant_name:
            return CategorizationResult(_DEFAULT_CATEGORY, 0.0)
        upper = merchant_name.upper()
        best: tuple[str, int] | None = None
        for pattern_upper, category, priority in self._patterns:
            if pattern_upper in upper:
                if best is None or priority > best[1]:
                    best = (category, priority)
        if best is None:
            return CategorizationResult(_DEFAULT_CATEGORY, 0.3)
        category, priority = best
        confidence = min(1.0, 0.5 + (priority / 200.0))
        return CategorizationResult(category, confidence)

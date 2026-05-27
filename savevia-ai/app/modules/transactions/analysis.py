"""TransactionAnalysisService — Python port of
com.savevia.optimizer.service.TransactionAnalysisService.

Three public flows mirror the Java controller:
- `analyze_transactions` — process unanalyzed transactions in bulk
- `get_missed_cashback_summary` — 90-day summary with per-category breakdown
- `get_recent_transactions` — paginated recent list with card-name hydration
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING, Iterable

from app.clients._base import JavaServiceError
from app.core.logging import get_logger
from app.models.transaction import Transaction
from app.modules.transactions.schema import (
    CardRecommendation,
    CategoryMissedCashback,
    MissedCashbackSummary,
    TransactionDTO,
)

if TYPE_CHECKING:
    from app.clients.card_client import CardServiceClient
    from app.modules.transactions.categorization import CategorizationService
    from app.repositories.transaction_repository import TransactionRepository

_log = get_logger("savevia-ai.transactions")

_FOUR_DP = Decimal("0.0001")
_ZERO = Decimal("0")
_SUMMARY_WINDOW_DAYS = 90
_TOP_RECOMMENDATIONS_LIMIT = 3


def _as_decimal(value: object) -> Decimal:
    if value is None or value == "":
        return _ZERO
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _reward_rate(card: dict, category: str | None) -> Decimal:
    """Per-card reward rate for a category. Matches Java's getRewardRate:
    rules win first by exact category-name match; fall back to baseRewardRate;
    final fallback is 0 (not 1% — this is for analysis only, not user-facing)."""
    if category and card.get("rewardRules"):
        for rule in card["rewardRules"]:
            rule_cat = rule.get("category")
            if rule_cat == category and rule.get("rewardRate") is not None:
                return _as_decimal(rule["rewardRate"])
    return _as_decimal(card.get("baseRewardRate"))


class TransactionAnalysisService:
    def __init__(
        self,
        *,
        transaction_repository: "TransactionRepository",
        card_client: "CardServiceClient",
        categorization: "CategorizationService",
    ):
        self._repo = transaction_repository
        self._cards = card_client
        self._categorize = categorization

    # ---- public flows -------------------------------------------------

    async def analyze_transactions(
        self,
        *,
        user_id: int,
        user_card_ids: list[int],
        force: bool = False,
    ) -> None:
        if not user_card_ids:
            _log.warning(
                "analysis_skipped_no_card_ids", user_id=user_id,
            )
            return

        user_cards = await self._fetch_cards(user_card_ids)
        if not user_cards:
            _log.warning("analysis_skipped_no_cards", user_id=user_id)
            return

        if force:
            reset = await self._repo.reset_analysis_by_user_id(user_id)
            _log.info("analysis_reset_rows", user_id=user_id, count=reset)

        unanalyzed = await self._repo.find_unanalyzed_by_user_id(user_id)
        if not unanalyzed:
            return
        _log.info(
            "analysing_transactions",
            user_id=user_id, count=len(unanalyzed), cards=len(user_cards),
        )
        for txn in unanalyzed:
            await self._analyze_one(txn, user_cards)

    async def get_recent_transactions(
        self,
        *,
        user_id: int,
        limit: int,
        user_card_ids: list[int],
    ) -> list[TransactionDTO]:
        transactions = await self._repo.find_recent_by_user_id(user_id, limit=limit)
        user_cards = await self._fetch_cards(user_card_ids) if user_card_ids else []
        card_map = {c.get("id"): c for c in user_cards}
        return [self._txn_to_dto(t, card_map) for t in transactions]

    async def get_missed_cashback_summary(
        self,
        *,
        user_id: int,
        user_card_ids: list[int],
    ) -> MissedCashbackSummary:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        start = now - timedelta(days=_SUMMARY_WINDOW_DAYS)
        transactions = await self._repo.find_by_user_and_date_range(
            user_id=user_id, start=start, end=now,
        )

        user_cards = await self._fetch_cards(user_card_ids) if user_card_ids else []

        # Analyse any pending rows in-flight so the summary reflects them.
        pending = [t for t in transactions if not t.is_analyzed]
        if pending and user_cards:
            for txn in pending:
                await self._analyze_one(txn, user_cards)
            # Re-fetch so we see the updated values.
            transactions = await self._repo.find_by_user_and_date_range(
                user_id=user_id, start=start, end=now,
            )

        summary = MissedCashbackSummary(total_transactions=len(transactions))

        debit_count = 0
        debit_spending = _ZERO
        debit_missed = _ZERO
        total_actual = _ZERO
        total_optimal = _ZERO
        total_missed = _ZERO

        # Group transactions by category
        by_category: dict[str, list[Transaction]] = {}
        for t in transactions:
            cat = t.category or "OTHER"
            by_category.setdefault(cat, []).append(t)
            if t.card_used_id is None:
                debit_count += 1
                debit_spending += abs(t.amount)
                if t.missed_cashback is not None:
                    debit_missed += t.missed_cashback
            if t.actual_cashback is not None:
                total_actual += t.actual_cashback
            if t.optimal_cashback is not None:
                total_optimal += t.optimal_cashback

        breakdown: list[CategoryMissedCashback] = []
        total_spending = _ZERO
        for category, txns in by_category.items():
            cat_spending = sum((abs(t.amount) for t in txns), _ZERO)
            cat_missed = sum(
                ((t.missed_cashback or _ZERO) for t in txns),
                _ZERO,
            )
            total_spending += cat_spending
            total_missed += cat_missed

            best_card = None
            best_rate = _ZERO
            for card in user_cards:
                rate = _reward_rate(card, category)
                if rate > best_rate:
                    best_rate = rate
                    best_card = card

            entry = CategoryMissedCashback(
                category=category,
                spending=cat_spending,
                missed_cashback=cat_missed,
            )
            if best_card is not None:
                entry.best_card_name = best_card.get("name")
                entry.best_card_bank = best_card.get("bank")
                entry.best_card_rate = best_rate
            breakdown.append(entry)

        breakdown.sort(key=lambda e: e.spending, reverse=True)

        summary.debit_transactions = debit_count
        summary.debit_spending = debit_spending
        summary.debit_missed_cashback = debit_missed
        summary.total_spending = total_spending
        summary.total_actual_cashback = total_actual
        summary.total_optimal_cashback = total_optimal
        summary.total_missed_cashback = total_missed
        summary.category_breakdown = breakdown
        summary.top_recommendations = self._build_recommendations(breakdown, user_cards)
        return summary

    # ---- helpers ------------------------------------------------------

    async def _fetch_cards(self, user_card_ids: list[int]) -> list[dict]:
        if not user_card_ids:
            return []
        try:
            return await self._cards.get_cards_batch(user_card_ids) or []
        except JavaServiceError as e:
            _log.warning("fetch_user_cards_failed", error=e.message)
            return []

    async def _analyze_one(self, txn: Transaction, user_cards: list[dict]) -> None:
        # Set / refresh category if missing or marked OTHER
        if not txn.category or txn.category == "OTHER":
            txn.category = self._categorize.categorize(txn.merchant)

        best_card: dict | None = None
        best_rate = _ZERO
        for card in user_cards:
            rate = _reward_rate(card, txn.category)
            if rate > best_rate:
                best_rate = rate
                best_card = card

        if best_card is None:
            txn.is_analyzed = True
            await self._repo.update_analysis(
                transaction_id=txn.id,
                best_card_id=None,
                actual_cashback=_ZERO,
                optimal_cashback=_ZERO,
                missed_cashback=_ZERO,
                category=txn.category,
                is_analyzed=True,
            )
            return

        amount = abs(txn.amount)
        optimal = (amount * best_rate).quantize(_FOUR_DP, rounding=ROUND_HALF_UP)

        actual: Decimal
        if txn.card_used_id is not None:
            used = next(
                (c for c in user_cards if c.get("id") == txn.card_used_id),
                None,
            )
            if used is not None:
                actual_rate = _reward_rate(used, txn.category)
                actual = (amount * actual_rate).quantize(
                    _FOUR_DP, rounding=ROUND_HALF_UP,
                )
            else:
                # Used a card we don't have details for — treat as 0.
                actual = _ZERO
        else:
            # Debit card / bank transfer — no cashback earned.
            actual = _ZERO

        missed = optimal - actual
        if missed < _ZERO:
            missed = _ZERO

        await self._repo.update_analysis(
            transaction_id=txn.id,
            best_card_id=best_card.get("id"),
            actual_cashback=actual,
            optimal_cashback=optimal,
            missed_cashback=missed,
            category=txn.category,
            is_analyzed=True,
        )

    def _txn_to_dto(
        self,
        txn: Transaction,
        card_map: dict[int, dict],
    ) -> TransactionDTO:
        used = (
            card_map.get(txn.card_used_id) if txn.card_used_id is not None else None
        )
        best = (
            card_map.get(txn.best_card_id) if txn.best_card_id is not None else None
        )
        return TransactionDTO(
            id=txn.id,
            user_id=txn.user_id,
            amount=txn.amount,
            merchant=txn.merchant,
            description=txn.description,
            category=txn.category,
            transaction_date=txn.transaction_date,
            card_used_id=txn.card_used_id,
            best_card_id=txn.best_card_id,
            actual_cashback=txn.actual_cashback,
            optimal_cashback=txn.optimal_cashback,
            missed_cashback=txn.missed_cashback,
            is_analyzed=txn.is_analyzed,
            is_debit_transaction=txn.card_used_id is None,
            card_used_name=(
                f"{used.get('bank', '')} {used.get('name', '')}".strip()
                if used else None
            ),
            best_card_name=best.get("name") if best else None,
            best_card_bank=best.get("bank") if best else None,
            best_card_rate=_reward_rate(best, txn.category) if best else None,
        )

    def _build_recommendations(
        self,
        breakdown: Iterable[CategoryMissedCashback],
        user_cards: list[dict],
    ) -> list[CardRecommendation]:
        card_savings: dict[int, Decimal] = {}
        card_categories: dict[int, list[str]] = {}

        for card in user_cards:
            card_id = card.get("id")
            if card_id is None:
                continue
            savings = _ZERO
            best_cats: list[str] = []
            for entry in breakdown:
                rate = _reward_rate(card, entry.category)
                if (
                    rate > _ZERO
                    and entry.missed_cashback > _ZERO
                    and entry.best_card_bank == card.get("bank")
                    and entry.best_card_name == card.get("name")
                ):
                    savings += entry.missed_cashback
                    best_cats.append(entry.category)
            card_savings[card_id] = savings
            card_categories[card_id] = best_cats

        # Sort cards by potential savings DESC, keep top-N with savings > 0.
        sorted_cards = sorted(
            (c for c in user_cards
             if card_savings.get(c.get("id"), _ZERO) > _ZERO),
            key=lambda c: card_savings.get(c.get("id"), _ZERO),
            reverse=True,
        )[:_TOP_RECOMMENDATIONS_LIMIT]

        return [
            CardRecommendation(
                card_id=card["id"],
                card_name=card.get("name", ""),
                bank=card.get("bank", ""),
                potential_savings=card_savings.get(card["id"], _ZERO),
                best_categories=card_categories.get(card["id"], []),
            )
            for card in sorted_cards
        ]

"""CashbackOptimizerService — Python port of
com.savevia.optimizer.service.CashbackOptimizerService.

Picks the best card per spending category, sums up the monthly/annual
rewards, subtracts annual fees, and emits a Java-equivalent summary.

NOTE: AI-generated per-recommendation explanations (Java's
OpenAiService.generateExplanations) are intentionally deferred to a
follow-up sub-task. The endpoint's contract still includes `aiExplanation`
in CategoryRecommendation — it just stays empty in the base path.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

from app.clients._base import JavaServiceError
from app.core.logging import get_logger
from app.modules.locale.categories import SpendingCategory
from app.modules.optimizer.cashback_calculator import (
    calculate_reward,
    format_rate_as_percentage,
    get_reward_rate,
)
from app.modules.optimizer_api.schema import (
    CategoryRecommendation,
    OptimizationRequest,
    OptimizationResult,
)

if TYPE_CHECKING:
    from app.clients.card_client import CardServiceClient
    from app.clients.user_client import UserServiceClient

_log = get_logger("savevia-ai.optimizer")

_TWO_DP = Decimal("0.01")


def _format_currency(amount: Decimal) -> str:
    return f"${amount.quantize(_TWO_DP, rounding=ROUND_HALF_UP)}"


class OptimizerInputError(ValueError):
    """Raised for client-side validation failures (no cards, empty spending)."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class CashbackOptimizerService:
    def __init__(
        self,
        *,
        card_client: "CardServiceClient",
        user_client: "UserServiceClient",
    ):
        self._card = card_client
        self._user = user_client

    async def optimize(self, request: OptimizationRequest) -> OptimizationResult:
        if not request.card_ids:
            raise OptimizerInputError("NO_CARDS_SELECTED", "At least one card must be selected")
        if not request.monthly_spending:
            raise OptimizerInputError("INVALID_SPENDING_DATA", "Spending data is required")

        try:
            user_cards = await self._card.get_cards_batch(request.card_ids)
        except JavaServiceError as e:
            raise OptimizerInputError(
                "CARD_NOT_FOUND", f"Failed to fetch card details: {e.message}",
            ) from e
        if not user_cards:
            raise OptimizerInputError("CARD_NOT_FOUND", "Failed to fetch card details")

        recommendations: list[CategoryRecommendation] = []
        total_monthly_reward = Decimal("0")

        for raw_category, amount in request.monthly_spending.items():
            cat = SpendingCategory.from_str(raw_category)
            if cat is None or amount is None or amount <= 0:
                continue

            best_card: dict | None = None
            best_reward = Decimal("0")
            best_rate = Decimal("0")

            for card in user_cards:
                reward = calculate_reward(card, cat, amount)
                if reward > best_reward:
                    best_reward = reward
                    best_card = card
                    best_rate = get_reward_rate(card, cat)

            if best_card is None:
                continue

            explanation = (
                f"Use {best_card.get('bank', '')} {best_card.get('name', '')} for {cat.display_name}"
                f" - earn {_format_currency(best_reward)} cashback"
                f" ({format_rate_as_percentage(best_rate)})"
            )
            recommendations.append(
                CategoryRecommendation(
                    category=cat.name,
                    monthly_spend=amount,
                    recommended_card=best_card,
                    reward_rate=best_rate,
                    monthly_reward=best_reward,
                    explanation=explanation,
                )
            )
            total_monthly_reward += best_reward

        annual_reward = total_monthly_reward * 12
        total_annual_fees = sum(
            (Decimal(str(c.get("annualFee"))) if c.get("annualFee") is not None else Decimal("0")
             for c in user_cards),
            Decimal("0"),
        )
        net_annual_savings = annual_reward - total_annual_fees

        summary = (
            f"With your current cards, you can earn {_format_currency(annual_reward)} "
            "per year in cashback. After deducting "
            f"{_format_currency(total_annual_fees)} in annual fees, your net savings "
            f"would be {_format_currency(net_annual_savings)}."
        )

        # AI explanations — port of Java's OpenAiService.generateExplanations
        # is deferred. For now we still check + record AI usage so quota
        # accounting stays consistent (matches Java behaviour for the
        # logged-in + flag-on path even when we don't actually call OpenAI).
        if request.enable_ai_explanation and request.user_id is not None:
            try:
                allowed = await self._user.check_can_use_ai(user_id=request.user_id)
                if allowed:
                    # TODO(plan-04 follow-up): port OpenAiService.generateExplanations.
                    # When implemented, fill recommendation.ai_explanation here
                    # before recording usage.
                    try:
                        await self._user.record_ai_usage(user_id=request.user_id)
                    except JavaServiceError as e:
                        _log.warning("record_ai_usage_failed", error=e.message)
                else:
                    _log.info(
                        "ai_explanation_quota_exhausted",
                        user_id=request.user_id,
                    )
            except JavaServiceError as e:
                _log.warning("ai_quota_check_failed", error=e.message)

        return OptimizationResult(
            recommendations=recommendations,
            monthly_reward=total_monthly_reward.quantize(_TWO_DP, rounding=ROUND_HALF_UP),
            annual_reward=annual_reward.quantize(_TWO_DP, rounding=ROUND_HALF_UP),
            total_annual_fees=total_annual_fees.quantize(_TWO_DP, rounding=ROUND_HALF_UP),
            net_annual_savings=net_annual_savings.quantize(_TWO_DP, rounding=ROUND_HALF_UP),
            summary=summary,
        )

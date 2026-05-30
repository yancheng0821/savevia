"""Optimizer endpoint DTOs.

Wire format matches Java's:
- inbound: OptimizationRequest (cardIds, monthlySpending, locale, enableAiExplanation, userId)
- outbound: OptimizationResult containing CategoryRecommendation list

Monthly spending is a JSON object keyed by SpendingCategory enum name
(e.g. `{"DINING": "200.00", "GROCERY": "500.00"}`).
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.core.types import Money


def _camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


class _OptimizerModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=_camel,
        populate_by_name=True,
        extra="ignore",
    )


class OptimizationRequest(_OptimizerModel):
    user_id: int | None = None
    card_ids: list[int] = Field(default_factory=list)
    monthly_spending: dict[str, Decimal] = Field(default_factory=dict)
    locale: str | None = None
    enable_ai_explanation: bool | None = None


class CategoryRecommendation(_OptimizerModel):
    category: str
    monthly_spend: Money
    recommended_card: dict | None = None
    reward_rate: Money
    monthly_reward: Money
    explanation: str | None = None
    ai_explanation: str | None = None


class OptimizationResult(_OptimizerModel):
    recommendations: list[CategoryRecommendation] = Field(default_factory=list)
    monthly_reward: Money = Decimal("0.00")
    annual_reward: Money = Decimal("0.00")
    total_annual_fees: Money = Decimal("0.00")
    net_annual_savings: Money = Decimal("0.00")
    summary: str = ""

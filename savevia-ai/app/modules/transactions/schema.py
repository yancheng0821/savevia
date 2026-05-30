"""Transactions module DTOs (wire format)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.core.types import Money


def _camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


class _TxModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=_camel,
        populate_by_name=True,
        extra="ignore",
    )


class TransactionDTO(_TxModel):
    id: int
    user_id: int
    amount: Money
    merchant: str | None = None
    description: str | None = None
    category: str | None = None
    transaction_date: datetime
    card_used_id: int | None = None
    best_card_id: int | None = None
    actual_cashback: Money | None = None
    optimal_cashback: Money | None = None
    missed_cashback: Money | None = None
    is_analyzed: bool | None = None
    is_debit_transaction: bool | None = None
    card_used_name: str | None = None
    best_card_name: str | None = None
    best_card_bank: str | None = None
    best_card_rate: Money | None = None


class CategoryMissedCashback(_TxModel):
    category: str
    spending: Money = Decimal("0")
    missed_cashback: Money = Decimal("0")
    best_card_name: str | None = None
    best_card_bank: str | None = None
    best_card_rate: Money | None = None


class CardRecommendation(_TxModel):
    card_id: int
    card_name: str
    bank: str
    potential_savings: Money
    best_categories: list[str] = Field(default_factory=list)


class MissedCashbackSummary(_TxModel):
    total_transactions: int = 0
    debit_transactions: int = 0
    total_spending: Money = Decimal("0")
    debit_spending: Money = Decimal("0")
    total_actual_cashback: Money = Decimal("0")
    total_optimal_cashback: Money = Decimal("0")
    total_missed_cashback: Money = Decimal("0")
    debit_missed_cashback: Money = Decimal("0")
    category_breakdown: list[CategoryMissedCashback] = Field(default_factory=list)
    top_recommendations: list[CardRecommendation] = Field(default_factory=list)

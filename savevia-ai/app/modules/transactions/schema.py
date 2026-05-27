"""Transactions module DTOs (wire format)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


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
    amount: Decimal
    merchant: str | None = None
    description: str | None = None
    category: str | None = None
    transaction_date: datetime
    card_used_id: int | None = None
    best_card_id: int | None = None
    actual_cashback: Decimal | None = None
    optimal_cashback: Decimal | None = None
    missed_cashback: Decimal | None = None
    is_analyzed: bool | None = None
    is_debit_transaction: bool | None = None
    card_used_name: str | None = None
    best_card_name: str | None = None
    best_card_bank: str | None = None
    best_card_rate: Decimal | None = None


class CategoryMissedCashback(_TxModel):
    category: str
    spending: Decimal = Decimal("0")
    missed_cashback: Decimal = Decimal("0")
    best_card_name: str | None = None
    best_card_bank: str | None = None
    best_card_rate: Decimal | None = None


class CardRecommendation(_TxModel):
    card_id: int
    card_name: str
    bank: str
    potential_savings: Decimal
    best_categories: list[str] = Field(default_factory=list)


class MissedCashbackSummary(_TxModel):
    total_transactions: int = 0
    debit_transactions: int = 0
    total_spending: Decimal = Decimal("0")
    debit_spending: Decimal = Decimal("0")
    total_actual_cashback: Decimal = Decimal("0")
    total_optimal_cashback: Decimal = Decimal("0")
    total_missed_cashback: Decimal = Decimal("0")
    debit_missed_cashback: Decimal = Decimal("0")
    category_breakdown: list[CategoryMissedCashback] = Field(default_factory=list)
    top_recommendations: list[CardRecommendation] = Field(default_factory=list)

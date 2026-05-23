from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.repositories.base import BaseRepository


@dataclass(frozen=True)
class CategorySummary:
    """Aggregate row returned by `get_category_summary`.

    Mirrors TransactionMapper$CategorySummary in the Java service.
    """

    category: str | None
    total_amount: Decimal
    total_missed: Decimal


class TransactionRepository(BaseRepository[Transaction]):
    """Async translation of TransactionMapper.xml."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Transaction)

    async def find_by_user_and_date_range(
        self,
        user_id: int,
        start: datetime,
        end: datetime,
    ) -> list[Transaction]:
        stmt = (
            select(Transaction)
            .where(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start,
                Transaction.transaction_date < end,
            )
            .order_by(Transaction.transaction_date.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_unanalyzed_by_user_id(self, user_id: int) -> list[Transaction]:
        stmt = select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.is_analyzed.is_(False),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_recent_by_user_id(
        self, user_id: int, limit: int = 50
    ) -> list[Transaction]:
        stmt = (
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.transaction_date.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_account_and_flinks_id(
        self, account_id: int, flinks_id: str
    ) -> list[Transaction]:
        """Translates `findByAccountAndFlinksId` — duplicate-detection lookup."""
        stmt = select(Transaction).where(
            Transaction.account_id == account_id,
            Transaction.flinks_transaction_id == flinks_id,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_category_summary(
        self, user_id: int, start: datetime
    ) -> list[CategorySummary]:
        """Translates `getCategorySummary` — per-category totals since `start`."""
        stmt = (
            select(
                Transaction.category,
                func.sum(Transaction.amount).label("total_amount"),
                func.sum(Transaction.missed_cashback).label("total_missed"),
            )
            .where(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start,
            )
            .group_by(Transaction.category)
        )
        result = await self.session.execute(stmt)
        return [
            CategorySummary(
                category=row.category,
                total_amount=row.total_amount or Decimal("0"),
                total_missed=row.total_missed or Decimal("0"),
            )
            for row in result.all()
        ]

    async def update_analysis(
        self,
        transaction_id: int,
        *,
        best_card_id: int | None,
        actual_cashback: Decimal,
        optimal_cashback: Decimal,
        missed_cashback: Decimal,
        category: str | None,
        is_analyzed: bool = True,
    ) -> int:
        stmt = (
            update(Transaction)
            .where(Transaction.id == transaction_id)
            .values(
                best_card_id=best_card_id,
                actual_cashback=actual_cashback,
                optimal_cashback=optimal_cashback,
                missed_cashback=missed_cashback,
                category=category,
                is_analyzed=is_analyzed,
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount or 0

    async def reset_analysis_by_user_id(self, user_id: int) -> int:
        stmt = (
            update(Transaction)
            .where(Transaction.user_id == user_id)
            .values(
                is_analyzed=False,
                best_card_id=None,
                actual_cashback=None,
                optimal_cashback=None,
                missed_cashback=None,
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount or 0

    async def batch_insert(self, transactions: list[Transaction]) -> list[Transaction]:
        return await self.add_all(transactions)

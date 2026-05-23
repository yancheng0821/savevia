from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import delete as sa_delete
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.saved_result import SavedResult
from app.repositories.base import BaseRepository


class SavedResultRepository(BaseRepository[SavedResult]):
    """Async translation of SavedResultMapper.xml."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, SavedResult)

    async def find_by_user_id(
        self, user_id: int, limit: int = 100
    ) -> list[SavedResult]:
        stmt = (
            select(SavedResult)
            .where(SavedResult.user_id == user_id)
            .order_by(SavedResult.id.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def select_by_user_id_latest(self, user_id: int) -> SavedResult | None:
        """Translates `selectByUserIdLatest` — newest row for the user."""
        stmt = (
            select(SavedResult)
            .where(SavedResult.user_id == user_id)
            .order_by(SavedResult.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def select_by_share_id(self, share_id: str) -> SavedResult | None:
        """Translates `selectByShareId` — honours expires_at.

        Returns None for share_ids whose expires_at has passed.
        """
        now = datetime.utcnow()
        stmt = select(SavedResult).where(
            SavedResult.share_id == share_id,
            (SavedResult.expires_at.is_(None)) | (SavedResult.expires_at > now),
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_user_result(
        self,
        user_id: int,
        *,
        result_json: str,
        net_annual_savings: Decimal | None,
        annual_reward: Decimal | None,
        total_annual_fees: Decimal | None,
    ) -> int:
        """Translates `updateUserResult` — rewrites the user's stored result."""
        stmt = (
            update(SavedResult)
            .where(SavedResult.user_id == user_id)
            .values(
                result_json=result_json,
                net_annual_savings=net_annual_savings,
                annual_reward=annual_reward,
                total_annual_fees=total_annual_fees,
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount or 0

    async def update_share_id(
        self, saved_id: int, share_id: str, *, ttl_days: int = 30
    ) -> int:
        """Translates `updateShareId` — assigns a share_id with 30-day TTL."""
        expires_at = datetime.utcnow() + timedelta(days=ttl_days)
        stmt = (
            update(SavedResult)
            .where(SavedResult.id == saved_id)
            .values(share_id=share_id, expires_at=expires_at)
        )
        result = await self.session.execute(stmt)
        return result.rowcount or 0

    async def delete_by_user_and_id(self, user_id: int, saved_id: int) -> int:
        """Tenant-scoped delete: only removes the row if it belongs to user."""
        stmt = sa_delete(SavedResult).where(
            SavedResult.id == saved_id,
            SavedResult.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.rowcount or 0

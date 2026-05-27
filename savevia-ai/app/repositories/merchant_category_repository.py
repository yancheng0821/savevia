"""Repository for the `merchant_categories` table.

Translates the read-only side of MerchantCategoryMapper.xml. The
categorization service caches the active pattern list in memory and
calls `find_all_active()` only on cache refresh.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.merchant_category import MerchantCategory
from app.repositories.base import BaseRepository


class MerchantCategoryRepository(BaseRepository[MerchantCategory]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MerchantCategory)

    async def find_all_active(self) -> list[MerchantCategory]:
        """Order by priority DESC so higher-priority patterns win first."""
        stmt = (
            select(MerchantCategory)
            .where(MerchantCategory.is_active.is_(True))
            .order_by(MerchantCategory.priority.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

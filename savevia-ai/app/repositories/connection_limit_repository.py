from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.connection_history import ConnectionHistory
from app.models.user_connection_limit import UserConnectionLimit
from app.repositories.base import BaseRepository


class ConnectionLimitRepository(BaseRepository[UserConnectionLimit]):
    """Async translation of ConnectionLimitMapper."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, UserConnectionLimit)

    async def find_by_user_and_month(
        self, user_id: int, year_month: str
    ) -> UserConnectionLimit | None:
        stmt = select(UserConnectionLimit).where(
            UserConnectionLimit.user_id == user_id,
            UserConnectionLimit.year_month == year_month,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def insert(self, limit: UserConnectionLimit) -> UserConnectionLimit:
        return await self.add(limit)

    async def update_connection_count(self, limit: UserConnectionLimit) -> int:
        stmt = (
            update(UserConnectionLimit)
            .where(UserConnectionLimit.id == limit.id)
            .values(connection_count=limit.connection_count)
        )
        result = await self.session.execute(stmt)
        return result.rowcount or 0

    async def insert_history(self, history: ConnectionHistory) -> ConnectionHistory:
        self.session.add(history)
        await self.session.flush()
        return history

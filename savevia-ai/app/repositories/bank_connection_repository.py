from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bank_connection import BankConnection
from app.repositories.base import BaseRepository


class BankConnectionRepository(BaseRepository[BankConnection]):
    """Async translation of BankConnectionMapper."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, BankConnection)

    async def find_by_user_id(self, user_id: int) -> list[BankConnection]:
        stmt = (
            select(BankConnection)
            .where(BankConnection.user_id == user_id)
            .order_by(BankConnection.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, connection_id: int) -> BankConnection | None:
        return await self.get_by_id(connection_id)

    async def find_by_user_and_login_id(
        self, user_id: int, login_id: str
    ) -> BankConnection | None:
        stmt = select(BankConnection).where(
            BankConnection.user_id == user_id,
            BankConnection.flinks_login_id == login_id,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def find_by_user_and_institution(
        self, user_id: int, institution_name: str
    ) -> BankConnection | None:
        stmt = select(BankConnection).where(
            BankConnection.user_id == user_id,
            BankConnection.institution_name == institution_name,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def insert(self, connection: BankConnection) -> BankConnection:
        return await self.add(connection)

    async def update_status(self, connection: BankConnection) -> int:
        stmt = (
            update(BankConnection)
            .where(BankConnection.id == connection.id)
            .values(
                status=connection.status,
                flinks_login_id=connection.flinks_login_id,
                last_sync_at=connection.last_sync_at,
                error_message=connection.error_message,
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount or 0

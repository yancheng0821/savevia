from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bank_account import BankAccount
from app.repositories.base import BaseRepository


class BankAccountRepository(BaseRepository[BankAccount]):
    """Async translation of BankAccountMapper."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, BankAccount)

    async def find_by_connection_id(self, connection_id: int) -> list[BankAccount]:
        stmt = select(BankAccount).where(BankAccount.connection_id == connection_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def insert(self, account: BankAccount) -> BankAccount:
        return await self.add(account)

    async def update(self, account: BankAccount) -> int:
        stmt = (
            update(BankAccount)
            .where(BankAccount.id == account.id)
            .values(balance=account.balance, linked_card_id=account.linked_card_id)
        )
        result = await self.session.execute(stmt)
        return result.rowcount or 0

"""BankConnectionService — port of BankConnectionController logic
(DTO assembly, owner checks, config, delegating to Flinks + ConnectionLimit).
"""

from __future__ import annotations

from typing import Literal

from app.modules.bank.schema import BankAccountDTO, BankConnectionDTO, FlinksConnectRequest

ResyncResult = Literal["OK", "NOT_FOUND", "LIMIT_EXCEEDED"]


class BankConnectionService:
    def __init__(self, *, session, card_client, categorization, settings):
        from app.modules.connection_limits.service import ConnectionLimitService
        from app.modules.flinks.client import FlinksClient
        from app.modules.flinks.demo_data import DemoDataGenerator
        from app.modules.flinks.service import FlinksService
        from app.repositories.bank_account_repository import BankAccountRepository
        from app.repositories.bank_connection_repository import BankConnectionRepository
        from app.repositories.connection_limit_repository import ConnectionLimitRepository
        from app.repositories.transaction_repository import TransactionRepository

        self._session = session
        self._conn_repo = BankConnectionRepository(session)
        self._acct_repo = BankAccountRepository(session)
        self._customer_id = settings.flinks_customer_id
        self._iframe_url = settings.flinks_iframe_url
        self._sandbox = settings.flinks_sandbox
        self._limits = ConnectionLimitService(
            repository=ConnectionLimitRepository(session),
            default_max_connections=settings.connection_max_per_month,
        )
        self._flinks = FlinksService(
            bank_connection_repo=self._conn_repo,
            bank_account_repo=self._acct_repo,
            transaction_repo=TransactionRepository(session),
            categorization=categorization,
            card_client=card_client,
            connection_limits=self._limits,
            demo_factory=lambda: DemoDataGenerator(),
            flinks_client_factory=lambda: FlinksClient(
                base_url=settings.flinks_api_url,
                customer_id=settings.flinks_customer_id,
            ),
            sandbox=settings.flinks_sandbox,
        )

    # ---- config / limit --------------------------------------------------

    async def get_flinks_config(self, user_id: int) -> dict:
        limit = await self._limits.get_connection_limit(user_id)
        full_iframe = self._iframe_url
        if self._customer_id:
            full_iframe = f"{self._iframe_url}?customerId={self._customer_id}"
        cfg = {
            "customerId": self._customer_id,
            "iframeUrl": self._iframe_url,
            "sandbox": self._sandbox,
            "connectUrl": full_iframe,
            "connectionLimit": self._limit_summary(limit),
        }
        await self._session.commit()
        return cfg

    async def get_connection_limit(self, user_id: int) -> dict:
        limit = await self._limits.get_connection_limit(user_id)
        out = {**self._limit_summary(limit), "yearMonth": limit.year_month}
        await self._session.commit()
        return out

    @staticmethod
    def _limit_summary(limit) -> dict:
        used = limit.connection_count or 0
        mx = limit.max_connections or 0
        return {"used": used, "max": mx, "remaining": max(mx - used, 0),
                "canConnect": used < mx}

    # ---- connection CRUD -------------------------------------------------

    async def connect(self, user_id: int, request: FlinksConnectRequest) -> BankConnectionDTO:
        connection = await self._flinks.connect_bank(user_id, request)
        dto = await self._to_dto(connection)
        await self._session.commit()
        return dto

    async def get_connections(self, user_id: int) -> list[BankConnectionDTO]:
        rows = await self._conn_repo.find_by_user_id(user_id)
        return [await self._to_dto(r) for r in rows]

    async def get_connection(
        self, user_id: int, connection_id: int
    ) -> BankConnectionDTO | None:
        conn = await self._conn_repo.find_by_id(connection_id)
        if conn is None or conn.user_id != user_id:
            return None
        return await self._to_dto(conn)

    async def refresh(
        self, user_id: int, connection_id: int
    ) -> BankConnectionDTO | None:
        conn = await self._conn_repo.find_by_id(connection_id)
        if conn is None or conn.user_id != user_id:
            return None
        await self._flinks.refresh_bank_data(conn)
        dto = await self._to_dto(conn)
        await self._session.commit()
        return dto

    async def resync(
        self, user_id: int, connection_id: int, *, user_card_ids: list[int] | None
    ) -> "ResyncResult | BankConnectionDTO":
        conn = await self._conn_repo.find_by_id(connection_id)
        if conn is None or conn.user_id != user_id:
            return "NOT_FOUND"
        if not await self._limits.can_connect(user_id):
            return "LIMIT_EXCEEDED"
        await self._flinks.force_refresh_bank_data(conn, user_card_ids)
        await self._limits.record_connection(
            user_id, conn.institution_name, conn.flinks_login_id
        )
        dto = await self._to_dto(conn)
        await self._session.commit()
        return dto

    async def disconnect(self, user_id: int, connection_id: int) -> bool:
        conn = await self._conn_repo.find_by_id(connection_id)
        if conn is None or conn.user_id != user_id:
            return False
        conn.status = "DISCONNECTED"
        await self._conn_repo.update_status(conn)
        await self._limits.record_disconnect(
            user_id, conn.institution_name, conn.flinks_login_id
        )
        await self._session.commit()
        return True

    # ---- DTO assembly ----------------------------------------------------

    async def _to_dto(self, connection) -> BankConnectionDTO:
        accounts = await self._acct_repo.find_by_connection_id(connection.id)
        status = connection.status
        if status is not None and not isinstance(status, str):
            status = getattr(status, "value", None)
        return BankConnectionDTO(
            id=connection.id,
            institution_name=connection.institution_name,
            status=status,
            last_sync_at=connection.last_sync_at,
            error_message=connection.error_message,
            created_at=connection.created_at,
            accounts=[
                BankAccountDTO(
                    id=a.id, account_type=a.account_type, account_name=a.account_name,
                    account_number_masked=a.account_number_masked, balance=a.balance,
                    is_active=a.is_active,
                )
                for a in accounts
            ],
        )

"""ConnectionLimitService — Python port of
com.savevia.optimizer.service.ConnectionLimitService.

Calendar-month quota keyed `yyyy-MM`. `today` is injectable for tests.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date

from app.core.logging import get_logger
from app.models.connection_history import ConnectionHistory, ConnectionHistoryAction
from app.models.user_connection_limit import UserConnectionLimit
from app.repositories.connection_limit_repository import ConnectionLimitRepository

_log = get_logger("savevia-ai.connection-limit")


class ConnectionLimitService:
    def __init__(
        self,
        *,
        repository: ConnectionLimitRepository,
        default_max_connections: int = 5,
        today: Callable[[], date] = date.today,
    ):
        self._repo = repository
        self._default_max = default_max_connections
        self._today = today

    def _current_year_month(self) -> str:
        return self._today().strftime("%Y-%m")

    async def get_connection_limit(self, user_id: int) -> UserConnectionLimit:
        ym = self._current_year_month()
        limit = await self._repo.find_by_user_and_month(user_id, ym)
        if limit is None:
            limit = UserConnectionLimit(
                user_id=user_id,
                year_month=ym,
                connection_count=0,
                max_connections=self._default_max,
            )
            await self._repo.insert(limit)
            _log.info("connection_limit_created", user_id=user_id, year_month=ym)
        return limit

    @staticmethod
    def _can(limit: UserConnectionLimit) -> bool:
        return (limit.connection_count or 0) < (limit.max_connections or 0)

    @staticmethod
    def _remaining(limit: UserConnectionLimit) -> int:
        return max((limit.max_connections or 0) - (limit.connection_count or 0), 0)

    async def can_connect(self, user_id: int) -> bool:
        return self._can(await self.get_connection_limit(user_id))

    async def get_remaining_connections(self, user_id: int) -> int:
        return self._remaining(await self.get_connection_limit(user_id))

    async def record_connection(
        self, user_id: int, institution_name: str, flinks_login_id: str | None
    ) -> bool:
        limit = await self.get_connection_limit(user_id)
        if not self._can(limit):
            _log.warning(
                "connection_limit_reached",
                user_id=user_id,
                used=limit.connection_count,
                max=limit.max_connections,
            )
            return False
        limit.connection_count = (limit.connection_count or 0) + 1
        await self._repo.update_connection_count(limit)
        await self._write_history(
            user_id, institution_name, flinks_login_id, ConnectionHistoryAction.CONNECT
        )
        return True

    async def record_disconnect(
        self, user_id: int, institution_name: str, flinks_login_id: str | None
    ) -> None:
        await self._write_history(
            user_id, institution_name, flinks_login_id, ConnectionHistoryAction.DISCONNECT
        )

    async def record_refresh(
        self, user_id: int, institution_name: str, flinks_login_id: str | None
    ) -> None:
        await self._write_history(
            user_id, institution_name, flinks_login_id, ConnectionHistoryAction.REFRESH
        )

    async def _write_history(
        self,
        user_id: int,
        institution_name: str,
        flinks_login_id: str | None,
        action: ConnectionHistoryAction,
    ) -> None:
        await self._repo.insert_history(
            ConnectionHistory(
                user_id=user_id,
                institution_name=institution_name,
                action=action,
                flinks_login_id=flinks_login_id,
            )
        )

"""Bank-connection router — /api/v1/optimize/bank/** (Java parity).

Error envelopes mirror Java's `Result.error(String)` → code 500
(BankConnectionController returns Result.error(...) for not-found / limit).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_db
from app.modules.bank.schema import FlinksConnectRequest
from app.modules.bank.service import BankConnectionService

_LIMIT_MSG = (
    "LIMIT_EXCEEDED:Monthly connection limit reached (5/month). "
    "Please try again next month."
)


def _ok(data: object | None) -> dict:
    return {"code": 200, "message": "success", "data": data, "timestamp": 0}


def _error(code: int, message: str) -> dict:
    return {"code": code, "message": message, "data": None, "timestamp": 0}


def _parse_user_id(raw: str | None) -> int | None:
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def build_bank_router(
    get_card_client: Callable[[], Any],
    get_categorization: Callable[[], Any],
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/optimize/bank", tags=["bank"])

    def _svc(session: AsyncSession) -> BankConnectionService:
        return BankConnectionService(
            session=session,
            card_client=get_card_client(),
            categorization=get_categorization(),
            settings=get_settings(),
        )

    @router.get("/flinks-config")
    async def flinks_config(
        x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
        session: AsyncSession = Depends(get_db),
    ):
        uid = _parse_user_id(x_user_id)
        if uid is None:
            return _error(401, "User not authenticated")
        return _ok(await _svc(session).get_flinks_config(uid))

    @router.get("/connection-limit")
    async def connection_limit(
        x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
        session: AsyncSession = Depends(get_db),
    ):
        uid = _parse_user_id(x_user_id)
        if uid is None:
            return _error(401, "User not authenticated")
        return _ok(await _svc(session).get_connection_limit(uid))

    @router.post("/connect")
    async def connect(
        body: FlinksConnectRequest = Body(...),
        x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
        session: AsyncSession = Depends(get_db),
    ):
        uid = _parse_user_id(x_user_id)
        if uid is None:
            return _error(401, "User not authenticated")
        try:
            dto = await _svc(session).connect(uid, body)
        except RuntimeError as e:
            return _error(500, str(e))
        return _ok(dto.model_dump(by_alias=True, mode="json"))

    @router.get("/connections")
    async def connections(
        x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
        session: AsyncSession = Depends(get_db),
    ):
        uid = _parse_user_id(x_user_id)
        if uid is None:
            return _error(401, "User not authenticated")
        dtos = await _svc(session).get_connections(uid)
        return _ok([d.model_dump(by_alias=True, mode="json") for d in dtos])

    @router.get("/connections/{connection_id}")
    async def connection(
        connection_id: int,
        x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
        session: AsyncSession = Depends(get_db),
    ):
        uid = _parse_user_id(x_user_id)
        if uid is None:
            return _error(401, "User not authenticated")
        dto = await _svc(session).get_connection(uid, connection_id)
        if dto is None:
            return _error(500, "Connection not found")
        return _ok(dto.model_dump(by_alias=True, mode="json"))

    @router.post("/connections/{connection_id}/refresh")
    async def refresh(
        connection_id: int,
        x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
        session: AsyncSession = Depends(get_db),
    ):
        uid = _parse_user_id(x_user_id)
        if uid is None:
            return _error(401, "User not authenticated")
        dto = await _svc(session).refresh(uid, connection_id)
        if dto is None:
            return _error(500, "Connection not found")
        return _ok(dto.model_dump(by_alias=True, mode="json"))

    @router.post("/connections/{connection_id}/resync")
    async def resync(
        connection_id: int,
        body: dict | None = Body(default=None),
        x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
        session: AsyncSession = Depends(get_db),
    ):
        uid = _parse_user_id(x_user_id)
        if uid is None:
            return _error(401, "User not authenticated")
        user_card_ids = None
        if body and body.get("userCardIds") is not None:
            user_card_ids = [int(x) for x in body["userCardIds"]]
        result = await _svc(session).resync(uid, connection_id, user_card_ids=user_card_ids)
        if result == "NOT_FOUND":
            return _error(500, "Connection not found")
        if result == "LIMIT_EXCEEDED":
            return _error(500, _LIMIT_MSG)
        return _ok(result.model_dump(by_alias=True, mode="json"))

    @router.delete("/connections/{connection_id}")
    async def disconnect(
        connection_id: int,
        x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
        session: AsyncSession = Depends(get_db),
    ):
        uid = _parse_user_id(x_user_id)
        if uid is None:
            return _error(401, "User not authenticated")
        ok = await _svc(session).disconnect(uid, connection_id)
        if not ok:
            return _error(500, "Connection not found")
        return _ok(None)

    return router

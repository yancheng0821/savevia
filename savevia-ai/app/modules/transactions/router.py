"""Transactions HTTP router — three endpoints under /api/v1/optimize/transactions.

Mirrors com.savevia.optimizer.controller.TransactionController. The
controller takes user_card_ids as a comma-separated header
(`X-User-Card-Ids`) instead of fetching from the user service — the
frontend sends them straight from local state.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.modules.transactions.categorization import CategorizationService

if TYPE_CHECKING:
    from app.modules.transactions.analysis import TransactionAnalysisService


def _ok(data: object | None) -> dict:
    return {"code": 200, "message": "success", "data": data, "timestamp": 0}


def _error(code: int, message: str) -> dict:
    return {"code": code, "message": message, "data": None, "timestamp": 0}


def _parse_card_ids(raw: str | None) -> list[int]:
    if not raw or not raw.strip():
        return []
    out: list[int] = []
    for piece in raw.split(","):
        s = piece.strip()
        if not s:
            continue
        try:
            out.append(int(s))
        except ValueError:
            continue
    return out


def _parse_user_id(raw: str | None) -> int | None:
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def build_transactions_router(
    get_service: "Callable[[AsyncSession], TransactionAnalysisService]",
) -> APIRouter:
    """Build the router. `get_service` is a factory that takes a SQLAlchemy
    session and returns a fully-wired analysis service. Tests can override
    this to inject mocks; in production main.py wires it through the
    session + cached categorization service."""

    router = APIRouter(prefix="/api/v1/optimize/transactions", tags=["transactions"])

    @router.get("")
    async def get_recent_transactions(
        x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
        x_user_card_ids: Annotated[
            str | None, Header(alias="X-User-Card-Ids")
        ] = None,
        limit: int = Query(default=50, ge=1, le=500),
        session: AsyncSession = Depends(get_db),
    ) -> dict:
        user_id = _parse_user_id(x_user_id)
        if user_id is None:
            return _error(401, "User not authenticated")
        service = get_service(session)
        items = await service.get_recent_transactions(
            user_id=user_id, limit=limit, user_card_ids=_parse_card_ids(x_user_card_ids),
        )
        return _ok([t.model_dump(by_alias=True, mode="json") for t in items])

    @router.get("/summary")
    async def get_summary(
        x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
        x_user_card_ids: Annotated[
            str | None, Header(alias="X-User-Card-Ids")
        ] = None,
        session: AsyncSession = Depends(get_db),
    ) -> dict:
        user_id = _parse_user_id(x_user_id)
        if user_id is None:
            return _error(401, "User not authenticated")
        service = get_service(session)
        summary = await service.get_missed_cashback_summary(
            user_id=user_id, user_card_ids=_parse_card_ids(x_user_card_ids),
        )
        return _ok(summary.model_dump(by_alias=True, mode="json"))

    @router.post("/analyze")
    async def analyze(
        x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
        x_user_card_ids: Annotated[
            str | None, Header(alias="X-User-Card-Ids")
        ] = None,
        force: bool = Query(default=False),
        session: AsyncSession = Depends(get_db),
    ) -> dict:
        user_id = _parse_user_id(x_user_id)
        if user_id is None:
            return _error(401, "User not authenticated")
        service = get_service(session)
        await service.analyze_transactions(
            user_id=user_id,
            user_card_ids=_parse_card_ids(x_user_card_ids),
            force=force,
        )
        return _ok(None)

    return router


def build_analysis_service(
    *,
    session: AsyncSession,
    card_client,
    categorization: CategorizationService,
):
    """Factory used by main.py's lifespan. Built per-request because the
    transaction repository binds to a session; the categorization service
    is process-wide and passed in."""
    from app.modules.transactions.analysis import TransactionAnalysisService
    from app.repositories.transaction_repository import TransactionRepository

    return TransactionAnalysisService(
        transaction_repository=TransactionRepository(session),
        card_client=card_client,
        categorization=categorization,
    )


__all__ = ["build_transactions_router", "build_analysis_service"]

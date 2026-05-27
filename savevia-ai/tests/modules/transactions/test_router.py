"""Tests for the transactions router."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def app_and_service():
    from fastapi import FastAPI

    from app.core.db import get_db
    from app.modules.transactions.router import build_transactions_router
    from app.modules.transactions.schema import (
        MissedCashbackSummary,
        TransactionDTO,
    )

    service = AsyncMock()

    async def _fake_db():
        yield object()

    app = FastAPI()
    app.dependency_overrides[get_db] = _fake_db
    app.include_router(build_transactions_router(lambda _session: service))
    return app, service, TransactionDTO, MissedCashbackSummary


@pytest.fixture
async def client(app_and_service):
    app, *_ = app_and_service
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test",
    ) as c:
        yield c


# ---- /transactions GET -------------------------------------------------

async def test_get_recent_requires_user_id(client):
    resp = await client.get("/api/v1/optimize/transactions")
    body = resp.json()
    assert body["code"] == 401


async def test_get_recent_parses_card_ids_header_and_passes_limit(client, app_and_service):
    _, service, TransactionDTO, _ = app_and_service
    service.get_recent_transactions.return_value = [
        TransactionDTO(
            id=1, user_id=42, amount=Decimal("100"),
            transaction_date=datetime(2026, 5, 1),
        ),
    ]
    resp = await client.get(
        "/api/v1/optimize/transactions?limit=10",
        headers={"X-User-Id": "42", "X-User-Card-Ids": "1, 2, 3"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 200
    call = service.get_recent_transactions.await_args
    assert call.kwargs["user_id"] == 42
    assert call.kwargs["limit"] == 10
    assert call.kwargs["user_card_ids"] == [1, 2, 3]


async def test_get_recent_ignores_garbage_in_card_ids_header(client, app_and_service):
    _, service, *_ = app_and_service
    service.get_recent_transactions.return_value = []
    await client.get(
        "/api/v1/optimize/transactions",
        headers={"X-User-Id": "42", "X-User-Card-Ids": "1,abc,2,,"},
    )
    assert service.get_recent_transactions.await_args.kwargs["user_card_ids"] == [1, 2]


# ---- /transactions/summary GET ----------------------------------------

async def test_get_summary_returns_envelope(client, app_and_service):
    _, service, _, MissedCashbackSummary = app_and_service
    service.get_missed_cashback_summary.return_value = MissedCashbackSummary(
        total_transactions=3, total_spending=Decimal("300"),
    )
    resp = await client.get(
        "/api/v1/optimize/transactions/summary",
        headers={"X-User-Id": "42", "X-User-Card-Ids": "1"},
    )
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["totalTransactions"] == 3
    assert body["data"]["totalSpending"] == "300"


async def test_get_summary_requires_user_id(client):
    resp = await client.get("/api/v1/optimize/transactions/summary")
    assert resp.json()["code"] == 401


# ---- /transactions/analyze POST ---------------------------------------

async def test_analyze_requires_user_id(client):
    resp = await client.post("/api/v1/optimize/transactions/analyze")
    assert resp.json()["code"] == 401


async def test_analyze_forwards_force_flag(client, app_and_service):
    _, service, *_ = app_and_service
    resp = await client.post(
        "/api/v1/optimize/transactions/analyze?force=true",
        headers={"X-User-Id": "42", "X-User-Card-Ids": "1,2"},
    )
    body = resp.json()
    assert body["code"] == 200
    call = service.analyze_transactions.await_args
    assert call.kwargs["user_id"] == 42
    assert call.kwargs["user_card_ids"] == [1, 2]
    assert call.kwargs["force"] is True

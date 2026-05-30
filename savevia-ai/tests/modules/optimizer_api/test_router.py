"""Tests for the optimizer router."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def app_and_service():
    from fastapi import FastAPI

    from app.modules.optimizer_api.router import build_optimizer_router
    from app.modules.optimizer_api.schema import (
        CategoryRecommendation,
        OptimizationResult,
    )

    service = AsyncMock()
    app = FastAPI()
    app.include_router(build_optimizer_router(lambda: service))
    return app, service, OptimizationResult, CategoryRecommendation


@pytest.fixture
async def client(app_and_service):
    app, *_ = app_and_service
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test",
    ) as c:
        yield c


async def test_calculate_returns_envelope_with_result(client, app_and_service):
    _, service, OptimizationResult, CategoryRecommendation = app_and_service
    service.optimize.return_value = OptimizationResult(
        recommendations=[
            CategoryRecommendation(
                category="DINING",
                monthly_spend=Decimal("100"),
                recommended_card={"id": 1, "bank": "TD", "name": "Cash Visa"},
                reward_rate=Decimal("0.04"),
                monthly_reward=Decimal("4.00"),
                explanation="x",
            ),
        ],
        monthly_reward=Decimal("4.00"),
        annual_reward=Decimal("48.00"),
        total_annual_fees=Decimal("0.00"),
        net_annual_savings=Decimal("48.00"),
        summary="ok",
    )

    resp = await client.post(
        "/api/v1/optimize/calculate",
        json={
            "cardIds": [1],
            "monthlySpending": {"DINING": "100.00"},
            "enableAiExplanation": False,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 200
    data = body["data"]
    assert data["monthlyReward"] == 4.0
    assert data["recommendations"][0]["category"] == "DINING"
    # camelCase aliases for nested fields; Money serializes as a JSON number
    assert data["recommendations"][0]["monthlySpend"] == 100.0


async def test_calculate_400_on_no_cards_selected(client, app_and_service):
    _, service, *_ = app_and_service
    from app.modules.optimizer_api.service import OptimizerInputError

    service.optimize.side_effect = OptimizerInputError(
        "NO_CARDS_SELECTED", "At least one card must be selected",
    )
    resp = await client.post(
        "/api/v1/optimize/calculate",
        json={"cardIds": [], "monthlySpending": {"DINING": "100"}},
    )
    body = resp.json()
    assert body["code"] == 400
    assert "card must be selected" in body["message"]


async def test_calculate_passes_decimal_spending_to_service(client, app_and_service):
    _, service, OptimizationResult, _ = app_and_service
    service.optimize.return_value = OptimizationResult()
    resp = await client.post(
        "/api/v1/optimize/calculate",
        json={
            "cardIds": [1, 2],
            "monthlySpending": {"DINING": "200.50", "GROCERY": "500"},
        },
    )
    assert resp.status_code == 200
    sent = service.optimize.await_args.args[0]
    assert sent.card_ids == [1, 2]
    assert sent.monthly_spending["DINING"] == Decimal("200.50")
    assert sent.monthly_spending["GROCERY"] == Decimal("500")

"""Tests for the saved-results router. Mocks the SavedResultService via DI
override so we don't need a live DB."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def app_and_service():
    """Build a FastAPI app with the saved_results router and an override that
    injects a mocked SavedResultService."""
    from fastapi import FastAPI

    from app.core.db import get_db
    from app.modules.saved_results.router import router
    from app.modules.saved_results.schema import OptimizationResult, SaveResultResponse

    service = AsyncMock()

    # The router calls `_service(session)` to build a SavedResultService.
    # We monkeypatch the `_service` factory used by the router so it returns
    # our mock instead. (Simpler than overriding get_db + intercepting.)
    import app.modules.saved_results.router as router_mod

    def _override_service(_session):
        return service

    # Override the get_db dependency to yield a sentinel — the service mock
    # ignores it, but FastAPI still requires the dependency to resolve.
    async def _fake_db():
        yield object()

    app = FastAPI()
    app.dependency_overrides[get_db] = _fake_db
    app.include_router(router)

    # Patch the factory used by the route handlers
    router_mod._service = _override_service

    yield app, service, OptimizationResult, SaveResultResponse

    # Restore (router_mod._service is module-level; reset back to the
    # real implementation by re-importing). Avoid leak into other tests.
    from importlib import reload
    reload(router_mod)


@pytest.fixture
async def client(app_and_service):
    app, *_ = app_and_service
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test",
    ) as c:
        yield c


# ---- /share POST ------------------------------------------------------

async def test_share_returns_envelope_with_share_id_and_url(client, app_and_service):
    _, service, _, SaveResultResponse = app_and_service
    service.save_result.return_value = SaveResultResponse(
        share_id="ABCD1234", share_url="http://x/share/ABCD1234",
    )
    resp = await client.post(
        "/api/v1/optimize/share",
        headers={"X-User-Id": "42"},
        json={"result": {"annualReward": "100.00", "summary": "x"}},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 200
    assert body["data"] == {"shareId": "ABCD1234", "shareUrl": "http://x/share/ABCD1234"}
    # Service got the parsed result + user_id from header
    call = service.save_result.await_args
    assert call.kwargs["user_id"] == 42


async def test_share_works_for_anonymous_user(client, app_and_service):
    _, service, _, SaveResultResponse = app_and_service
    service.save_result.return_value = SaveResultResponse(
        share_id="ABCD1234", share_url="http://x/share/ABCD1234",
    )
    resp = await client.post(
        "/api/v1/optimize/share",
        json={"result": {"summary": "anon"}},
    )
    assert resp.status_code == 200
    assert service.save_result.await_args.kwargs["user_id"] is None


# ---- /share GET -------------------------------------------------------

async def test_get_shared_result_returns_payload(client, app_and_service):
    _, service, OptimizationResult, _ = app_and_service
    service.get_by_share_id.return_value = OptimizationResult.model_validate({
        "annualReward": "150.00", "summary": "hi",
    })
    resp = await client.get("/api/v1/optimize/share/ABCD1234")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["annualReward"] == 150.0


async def test_get_shared_result_returns_404_envelope_when_missing(client, app_and_service):
    _, service, *_ = app_and_service
    service.get_by_share_id.return_value = None
    resp = await client.get("/api/v1/optimize/share/MISSING")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 404
    assert "not found" in body["message"].lower()


# ---- /share/{id}/og HTML ----------------------------------------------

async def test_og_page_default_when_no_savings(client, app_and_service):
    _, service, *_ = app_and_service
    service.get_by_share_id.return_value = None
    resp = await client.get("/api/v1/optimize/share/X/og")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
    body = resp.text
    assert "<title>SaveVia - Credit Card Cashback Optimizer</title>" in body
    assert "og:title" in body


async def test_og_page_substitutes_savings_into_title(client, app_and_service):
    _, service, OptimizationResult, _ = app_and_service
    service.get_by_share_id.return_value = OptimizationResult.model_validate({
        "netAnnualSavings": "450.50",
    })
    resp = await client.get("/api/v1/optimize/share/ABCD1234/og")
    body = resp.text
    # rounded HALF_UP to whole dollars: 450.50 -> 451
    assert "$451/year" in body
    assert "ABCD1234" in body  # share URL embeds it


# ---- /user-result POST ------------------------------------------------

async def test_save_user_result_requires_user(client, app_and_service):
    resp = await client.post(
        "/api/v1/optimize/user-result",
        json={"result": {"summary": "x"}},
    )
    body = resp.json()
    assert body["code"] == 401


async def test_save_user_result_with_user_succeeds(client, app_and_service):
    _, service, *_ = app_and_service
    resp = await client.post(
        "/api/v1/optimize/user-result",
        headers={"X-User-Id": "7"},
        json={"result": {"summary": "x"}},
    )
    body = resp.json()
    assert body["code"] == 200
    service.save_user_result.assert_awaited_once()
    assert service.save_user_result.await_args.kwargs["user_id"] == 7


# ---- /user-result GET -------------------------------------------------

async def test_get_user_result_requires_user(client, app_and_service):
    resp = await client.get("/api/v1/optimize/user-result")
    assert resp.json()["code"] == 401


async def test_get_user_result_returns_null_when_no_row(client, app_and_service):
    _, service, *_ = app_and_service
    service.get_user_result.return_value = None
    resp = await client.get(
        "/api/v1/optimize/user-result",
        headers={"X-User-Id": "7"},
    )
    body = resp.json()
    assert body["code"] == 200
    assert body["data"] is None


async def test_get_user_result_returns_payload(client, app_and_service):
    _, service, OptimizationResult, _ = app_and_service
    service.get_user_result.return_value = OptimizationResult.model_validate({
        "annualReward": "200.00",
    })
    resp = await client.get(
        "/api/v1/optimize/user-result",
        headers={"X-User-Id": "7"},
    )
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["annualReward"] == 200.0

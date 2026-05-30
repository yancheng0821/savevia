from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def app_and_service(monkeypatch):
    from fastapi import FastAPI

    from app.core.db import get_db
    from app.modules.bank import router as bank_router_mod

    service = AsyncMock()

    # Patch the service constructor used inside the router to return our mock.
    monkeypatch.setattr(bank_router_mod, "BankConnectionService", lambda **kw: service)

    async def _fake_db():
        yield object()

    app = FastAPI()
    app.dependency_overrides[get_db] = _fake_db
    app.include_router(bank_router_mod.build_bank_router(
        get_card_client=lambda: AsyncMock(),
        get_categorization=lambda: object(),
    ))
    return app, service


@pytest.fixture
async def client(app_and_service):
    app, _ = app_and_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


async def test_connections_requires_user_id(client):
    resp = await client.get("/api/v1/optimize/bank/connections")
    assert resp.json()["code"] == 401


async def test_get_connection_not_found_is_500(client, app_and_service):
    _, service = app_and_service
    service.get_connection.return_value = None
    resp = await client.get(
        "/api/v1/optimize/bank/connections/9", headers={"X-User-Id": "42"}
    )
    body = resp.json()
    assert body["code"] == 500
    assert body["message"] == "Connection not found"


async def test_connect_limit_exceeded_maps_to_500(client, app_and_service):
    _, service = app_and_service
    service.connect.side_effect = RuntimeError("LIMIT_EXCEEDED:You have reached ...")
    resp = await client.post(
        "/api/v1/optimize/bank/connect",
        headers={"X-User-Id": "42"},
        json={"loginId": "demo-x", "institutionName": "TD"},
    )
    body = resp.json()
    assert body["code"] == 500
    assert body["message"].startswith("LIMIT_EXCEEDED")


async def test_resync_over_limit_returns_limit_message(client, app_and_service):
    _, service = app_and_service
    service.resync.return_value = "LIMIT_EXCEEDED"
    resp = await client.post(
        "/api/v1/optimize/bank/connections/9/resync",
        headers={"X-User-Id": "42"}, json={},
    )
    body = resp.json()
    assert body["code"] == 500
    assert "Monthly connection limit reached" in body["message"]


async def test_flinks_config_ok(client, app_and_service):
    _, service = app_and_service
    service.get_flinks_config.return_value = {"customerId": "c", "sandbox": True}
    resp = await client.get(
        "/api/v1/optimize/bank/flinks-config", headers={"X-User-Id": "42"}
    )
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["customerId"] == "c"

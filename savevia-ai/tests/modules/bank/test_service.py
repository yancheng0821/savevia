from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock


def _acct(**kw):
    base = dict(id=11, account_type="CREDIT_CARD", account_name="TD Visa",
                account_number_masked="****1234", balance=Decimal("50.00"), is_active=True)
    base.update(kw)
    return SimpleNamespace(**base)


def _conn(**kw):
    base = dict(id=1, user_id=42, institution_name="TD", status="CONNECTED",
                last_sync_at=datetime(2026, 5, 30), error_message=None,
                created_at=datetime(2026, 5, 1), flinks_login_id="demo-x")
    base.update(kw)
    return SimpleNamespace(**base)


def _service(*, conn_repo=None, acct_repo=None, limits=None, flinks=None, session=None):
    from app.modules.bank.service import BankConnectionService
    svc = BankConnectionService.__new__(BankConnectionService)
    svc._session = session or AsyncMock()
    svc._conn_repo = conn_repo or AsyncMock()
    svc._acct_repo = acct_repo or AsyncMock()
    svc._limits = limits or AsyncMock()
    svc._flinks = flinks or AsyncMock()
    svc._customer_id = "cust-1"
    svc._iframe_url = "https://iframe/"
    svc._sandbox = True
    return svc


async def test_get_connection_returns_none_for_wrong_owner():
    conn_repo = AsyncMock()
    conn_repo.find_by_id.return_value = _conn(user_id=99)
    svc = _service(conn_repo=conn_repo)
    assert await svc.get_connection(42, 1) is None


async def test_to_dto_includes_accounts():
    acct_repo = AsyncMock()
    acct_repo.find_by_connection_id.return_value = [_acct()]
    svc = _service(acct_repo=acct_repo)
    dto = await svc._to_dto(_conn())
    assert dto.institution_name == "TD"
    assert dto.accounts[0].account_number_masked == "****1234"


async def test_disconnect_sets_status_and_records_history():
    conn_repo = AsyncMock()
    conn = _conn()
    conn_repo.find_by_id.return_value = conn
    acct_repo = AsyncMock()
    acct_repo.find_by_connection_id.return_value = []
    limits = AsyncMock()
    svc = _service(conn_repo=conn_repo, acct_repo=acct_repo, limits=limits)
    ok = await svc.disconnect(42, 1)
    assert ok is True
    assert conn.status == "DISCONNECTED"
    conn_repo.update_status.assert_awaited()
    limits.record_disconnect.assert_awaited_once()


async def test_resync_blocked_over_limit_returns_limit_error():
    conn_repo = AsyncMock()
    conn_repo.find_by_id.return_value = _conn()
    limits = AsyncMock()
    limits.can_connect.return_value = False
    svc = _service(conn_repo=conn_repo, limits=limits)
    result = await svc.resync(42, 1, user_card_ids=None)
    assert result == "LIMIT_EXCEEDED"


async def test_connection_limit_summary_shape():
    limits = AsyncMock()
    limits.get_connection_limit.return_value = SimpleNamespace(
        connection_count=2, max_connections=5, year_month="2026-05",
    )
    svc = _service(limits=limits)
    out = await svc.get_connection_limit(42)
    assert out == {"used": 2, "max": 5, "remaining": 3, "canConnect": True,
                   "yearMonth": "2026-05"}

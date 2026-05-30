from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock


def _limit(*, id=1, user_id=42, ym="2026-05", count=0, mx=5):
    return SimpleNamespace(
        id=id, user_id=user_id, year_month=ym,
        connection_count=count, max_connections=mx,
    )


def _service(repo, *, today=date(2026, 5, 30), default_max=5):
    from app.modules.connection_limits.service import ConnectionLimitService
    return ConnectionLimitService(
        repository=repo, default_max_connections=default_max, today=lambda: today,
    )


async def test_get_creates_row_when_absent():
    repo = AsyncMock()
    repo.find_by_user_and_month.return_value = None
    repo.insert.side_effect = lambda row: row
    svc = _service(repo)
    row = await svc.get_connection_limit(42)
    repo.find_by_user_and_month.assert_awaited_once_with(42, "2026-05")
    repo.insert.assert_awaited_once()
    assert row.year_month == "2026-05"
    assert row.max_connections == 5
    assert row.connection_count == 0


async def test_can_connect_true_until_cap():
    repo = AsyncMock()
    repo.find_by_user_and_month.return_value = _limit(count=4, mx=5)
    assert await _service(repo).can_connect(42) is True
    repo.find_by_user_and_month.return_value = _limit(count=5, mx=5)
    assert await _service(repo).can_connect(42) is False


async def test_record_connection_increments_and_logs_history():
    repo = AsyncMock()
    repo.find_by_user_and_month.return_value = _limit(count=2, mx=5)
    svc = _service(repo)
    ok = await svc.record_connection(42, "TD", "demo-x")
    assert ok is True
    repo.update_connection_count.assert_awaited_once()
    hist = repo.insert_history.await_args.args[0]
    assert hist.action.value == "CONNECT"
    assert hist.user_id == 42


async def test_record_connection_refuses_when_at_cap():
    repo = AsyncMock()
    repo.find_by_user_and_month.return_value = _limit(count=5, mx=5)
    ok = await _service(repo).record_connection(42, "TD", "demo-x")
    assert ok is False
    repo.update_connection_count.assert_not_called()


async def test_record_disconnect_writes_history_only():
    repo = AsyncMock()
    await _service(repo).record_disconnect(42, "TD", "demo-x")
    hist = repo.insert_history.await_args.args[0]
    assert hist.action.value == "DISCONNECT"
    repo.update_connection_count.assert_not_called()

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest


class _Cat:
    def categorize(self, name):  # deterministic stub
        return "DINING" if name and "UBER" in name.upper() else "OTHER"


def _demo_factory():
    import random

    from app.modules.flinks.demo_data import DemoDataGenerator
    c = {"n": 0}

    def u():
        c["n"] += 1
        return f"uuid{c['n']:04d}"

    return lambda: DemoDataGenerator(
        rng=random.Random(1), uuid_factory=u, now=lambda: datetime(2026, 5, 30),
    )


def _service(*, sandbox=True, conn_repo=None, acct_repo=None, txn_repo=None,
             card=None, limits=None):
    from app.modules.flinks.service import FlinksService
    return FlinksService(
        bank_connection_repo=conn_repo or AsyncMock(),
        bank_account_repo=acct_repo or AsyncMock(),
        transaction_repo=txn_repo or AsyncMock(),
        categorization=_Cat(),
        card_client=card or AsyncMock(),
        connection_limits=limits or AsyncMock(),
        demo_factory=_demo_factory(),
        flinks_client_factory=lambda: AsyncMock(),
        sandbox=sandbox,
    )


def _conn(**kw):
    base = dict(id=1, user_id=42, flinks_login_id="demo-x", institution_name="TD",
                status="PENDING", last_sync_at=None, error_message=None)
    base.update(kw)
    return SimpleNamespace(**base)


async def test_match_credit_card_scoring_threshold():
    svc = _service()
    cards = [{"id": 9, "bank": "TD", "name": "TD Cash Back Visa Infinite"}]
    matched = svc._match_credit_card_to_user_card(
        "TD Cash Back Visa Infinite", "TD Canada Trust", cards,
    )
    assert matched == 9
    assert svc._match_credit_card_to_user_card(
        "TD Cash Back Visa", "RBC Royal Bank", cards,
    ) is None


async def test_map_account_type_and_mask():
    svc = _service()
    assert svc._map_account_type("Chequing") == "CHECKING"
    assert svc._map_account_type("Credit") == "CREDIT_CARD"
    assert svc._map_account_type(None) == "OTHER"
    assert svc._mask_account_number("123456789") == "****6789"
    assert svc._mask_account_number("12") == "****"


async def test_connect_existing_login_triggers_refresh_not_new_quota():
    conn_repo = AsyncMock()
    existing = _conn(status="CONNECTED")
    conn_repo.find_by_user_and_login_id.return_value = existing
    limits = AsyncMock()
    svc = _service(conn_repo=conn_repo, limits=limits)
    from app.modules.bank.schema import FlinksConnectRequest
    out = await svc.connect_bank(
        42, FlinksConnectRequest(login_id="demo-x", institution_name="TD")
    )
    assert out is existing
    limits.record_refresh.assert_awaited()
    limits.record_connection.assert_not_called()


async def test_connect_new_demo_saves_accounts_and_counts_quota():
    conn_repo = AsyncMock()
    conn_repo.find_by_user_and_login_id.return_value = None
    conn_repo.find_by_user_and_institution.return_value = None
    acct_repo = AsyncMock()
    acct_repo.find_by_connection_id.return_value = []
    txn_repo = AsyncMock()
    txn_repo.find_by_account_and_flinks_id.return_value = []
    limits = AsyncMock()
    limits.can_connect.return_value = True
    card = AsyncMock()
    card.get_cards_batch.return_value = [
        {"id": 9, "bank": "TD", "name": "TD Cash Back Visa Infinite"}
    ]
    svc = _service(conn_repo=conn_repo, acct_repo=acct_repo, txn_repo=txn_repo,
                   limits=limits, card=card)

    from app.modules.bank.schema import FlinksConnectRequest
    conn_repo.insert.side_effect = lambda c: setattr(c, "id", 1) or c
    out = await svc.connect_bank(42, FlinksConnectRequest(
        login_id="demo-new", institution_name="TD", user_card_ids=[9],
    ))
    assert out.status == "CONNECTED"
    assert out.last_sync_at is not None
    limits.record_connection.assert_awaited_once()
    assert acct_repo.insert.await_count >= 1
    assert txn_repo.insert.await_count >= 1


async def test_connect_blocked_when_over_limit():
    conn_repo = AsyncMock()
    conn_repo.find_by_user_and_login_id.return_value = None
    conn_repo.find_by_user_and_institution.return_value = None
    limits = AsyncMock()
    limits.can_connect.return_value = False
    limits.get_remaining_connections.return_value = 0
    svc = _service(conn_repo=conn_repo, limits=limits)
    from app.modules.bank.schema import FlinksConnectRequest
    with pytest.raises(RuntimeError, match="LIMIT_EXCEEDED"):
        await svc.connect_bank(
            42, FlinksConnectRequest(login_id="demo-z", institution_name="TD")
        )


async def test_refresh_is_local_only_no_timestamp():
    conn_repo = AsyncMock()
    svc = _service(conn_repo=conn_repo)
    conn = _conn(status="REFRESHING", last_sync_at=None)
    await svc.refresh_bank_data(conn)
    assert conn.status == "CONNECTED"
    assert conn.last_sync_at is None
    conn_repo.update_status.assert_awaited()

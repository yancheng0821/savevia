import os
from decimal import Decimal

import pytest


@pytest.fixture
async def db_session():
    from app.core.db import dispose_engine, get_session_factory

    await dispose_engine()
    factory = get_session_factory()
    async with factory() as session:
        yield session


def test_repository_signature():
    from app.repositories.saved_result_repository import SavedResultRepository

    for name in ("find_by_user_id", "delete_by_user_and_id"):
        assert hasattr(SavedResultRepository, name), f"missing method: {name}"


@pytest.mark.skipif(
    not os.environ.get("INTEGRATION_TESTS"),
    reason="requires running MySQL",
)
async def test_saved_result_crud(db_session):
    import uuid

    from app.models import SavedResult
    from app.repositories.saved_result_repository import SavedResultRepository

    repo = SavedResultRepository(db_session)
    user_id = 77_777_777

    item = SavedResult(
        user_id=user_id,
        result_json='{"test": "delete-me"}',
        share_id=str(uuid.uuid4())[:32],
    )
    await repo.add(item)
    await db_session.commit()

    items = await repo.find_by_user_id(user_id)
    assert any(i.id == item.id for i in items)

    deleted = await repo.delete_by_user_and_id(user_id=user_id, saved_id=item.id)
    await db_session.commit()
    assert deleted == 1

    after = await repo.find_by_user_id(user_id)
    assert all(i.id != item.id for i in after)


@pytest.mark.skipif(
    not os.environ.get("INTEGRATION_TESTS"),
    reason="requires running MySQL",
)
async def test_select_by_share_id_honours_expiry(db_session):
    """`select_by_share_id` must return None for expired shares."""
    import uuid
    from datetime import datetime, timedelta

    from app.models import SavedResult
    from app.repositories.saved_result_repository import SavedResultRepository

    repo = SavedResultRepository(db_session)
    user_id = 77_777_778

    fresh_share = str(uuid.uuid4())[:32]
    expired_share = str(uuid.uuid4())[:32]

    fresh = SavedResult(
        user_id=user_id,
        result_json='{"fresh": true}',
        share_id=fresh_share,
        expires_at=datetime.utcnow() + timedelta(days=1),
    )
    expired = SavedResult(
        user_id=user_id,
        result_json='{"expired": true}',
        share_id=expired_share,
        expires_at=datetime.utcnow() - timedelta(days=1),
    )
    await repo.add_all([fresh, expired])
    await db_session.commit()

    assert await repo.select_by_share_id(fresh_share) is not None
    assert await repo.select_by_share_id(expired_share) is None

    await repo.delete(fresh)
    await repo.delete(expired)
    await db_session.commit()


@pytest.mark.skipif(
    not os.environ.get("INTEGRATION_TESTS"),
    reason="requires running MySQL",
)
async def test_update_user_result_and_share_id(db_session):
    """`update_user_result` and `update_share_id` rewrite the right columns."""
    import uuid

    from app.models import SavedResult
    from app.repositories.saved_result_repository import SavedResultRepository

    repo = SavedResultRepository(db_session)
    user_id = 77_777_779

    item = SavedResult(
        user_id=user_id,
        result_json='{"v": 1}',
        share_id=str(uuid.uuid4())[:32],
    )
    await repo.add(item)
    await db_session.commit()

    updated = await repo.update_user_result(
        user_id,
        result_json='{"v": 2}',
        net_annual_savings=Decimal("123.45"),
        annual_reward=Decimal("234.56"),
        total_annual_fees=Decimal("99.99"),
    )
    await db_session.commit()
    assert updated == 1

    latest = await repo.select_by_user_id_latest(user_id)
    assert latest is not None
    assert latest.result_json == '{"v": 2}'
    assert latest.net_annual_savings == Decimal("123.45")

    new_share = str(uuid.uuid4())[:32]
    affected = await repo.update_share_id(item.id, new_share, ttl_days=7)
    await db_session.commit()
    assert affected == 1

    reloaded = await repo.get_by_id(item.id)
    assert reloaded is not None
    assert reloaded.share_id == new_share
    assert reloaded.expires_at is not None

    await repo.delete(reloaded)
    await db_session.commit()

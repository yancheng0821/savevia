import os
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import text


@pytest.fixture
async def db_session():
    from app.core.db import dispose_engine, get_session_factory

    await dispose_engine()
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def _seed_user(session, user_id: int) -> None:
    """Insert a synthetic user row so FK constraints on user_id succeed.

    `transactions.user_id` has an ON DELETE CASCADE FK to `users.id`, so we
    seed the row up-front and let the cascade clean it up at test teardown.
    """
    await session.execute(
        text(
            "INSERT IGNORE INTO users (id, email, name) VALUES "
            "(:id, :email, :name)"
        ),
        {"id": user_id, "email": f"tx-{user_id}@test.local", "name": f"tx{user_id}"},
    )


async def _cleanup_user(session, user_id: int) -> None:
    await session.execute(text("DELETE FROM users WHERE id = :id"), {"id": user_id})


def test_repository_signature():
    from app.repositories.transaction_repository import TransactionRepository

    for name in (
        "find_by_user_and_date_range",
        "find_unanalyzed_by_user_id",
        "find_recent_by_user_id",
        "update_analysis",
        "reset_analysis_by_user_id",
        "batch_insert",
    ):
        assert hasattr(TransactionRepository, name), f"missing method: {name}"


@pytest.mark.skipif(
    not os.environ.get("INTEGRATION_TESTS"),
    reason="requires running MySQL",
)
async def test_insert_and_find_recent(db_session):
    from app.models import Transaction
    from app.repositories.transaction_repository import TransactionRepository

    repo = TransactionRepository(db_session)
    user_id = 88_888_888
    await _seed_user(db_session, user_id)
    await db_session.commit()

    t = Transaction(
        user_id=user_id,
        amount=Decimal("42.50"),
        merchant="Test Coffee",
        category="DINING",
        transaction_date=datetime.utcnow(),
    )
    await repo.add(t)
    await db_session.commit()

    recent = await repo.find_recent_by_user_id(user_id=user_id, limit=10)
    assert any(x.id == t.id for x in recent)

    # FK ON DELETE CASCADE drops the transaction as the user is removed.
    await _cleanup_user(db_session, user_id)
    await db_session.commit()


@pytest.mark.skipif(
    not os.environ.get("INTEGRATION_TESTS"),
    reason="requires running MySQL",
)
async def test_find_by_date_range(db_session):
    from app.models import Transaction
    from app.repositories.transaction_repository import TransactionRepository

    repo = TransactionRepository(db_session)
    user_id = 88_888_889
    await _seed_user(db_session, user_id)
    await db_session.commit()

    now = datetime.utcnow()

    inside = Transaction(
        user_id=user_id, amount=Decimal("10"), merchant="A",
        transaction_date=now,
    )
    outside = Transaction(
        user_id=user_id, amount=Decimal("20"), merchant="B",
        transaction_date=now - timedelta(days=60),
    )
    await repo.add_all([inside, outside])
    await db_session.commit()

    found = await repo.find_by_user_and_date_range(
        user_id=user_id,
        start=now - timedelta(days=7),
        end=now + timedelta(days=1),
    )
    ids = {t.id for t in found}
    assert inside.id in ids
    assert outside.id not in ids

    await _cleanup_user(db_session, user_id)
    await db_session.commit()

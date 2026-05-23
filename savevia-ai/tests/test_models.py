import os

import pytest


@pytest.mark.skipif(
    not os.environ.get("INTEGRATION_TESTS"),
    reason="requires running MySQL — set INTEGRATION_TESTS=1 to enable",
)
async def test_all_models_match_live_schema():
    """Verify each declared model maps to a real table with matching columns."""
    from sqlalchemy import inspect

    from app.core.db import dispose_engine, get_engine
    from app.models import (
        BankAccount,
        BankConnection,
        ConnectionHistory,
        MerchantCategory,
        MissedCashbackReport,
        SavedResult,
        Transaction,
        UserConnectionLimit,
    )

    # Each async test runs in its own event loop, so dispose any cached
    # engine bound to a previous loop before creating a fresh connection.
    await dispose_engine()

    engine = get_engine()
    async with engine.connect() as conn:
        def _check(sync_conn):
            insp = inspect(sync_conn)
            errors = []
            for model in (
                Transaction,
                SavedResult,
                BankConnection,
                BankAccount,
                ConnectionHistory,
                MerchantCategory,
                MissedCashbackReport,
                UserConnectionLimit,
            ):
                table = model.__tablename__
                if not insp.has_table(table):
                    errors.append(f"missing table: {table}")
                    continue
                live_cols = {c["name"] for c in insp.get_columns(table)}
                model_cols = {c.name for c in model.__table__.columns}
                missing_in_db = model_cols - live_cols
                missing_in_model = live_cols - model_cols
                if missing_in_db:
                    errors.append(f"{table}: model has columns not in DB: {missing_in_db}")
                if missing_in_model:
                    errors.append(f"{table}: DB has columns not in model: {missing_in_model}")
            assert not errors, "\n".join(errors)

        await conn.run_sync(_check)


def test_models_register_with_base():
    import app.models  # noqa: F401 — force-register all models
    from app.models import Base

    tablenames = set(Base.metadata.tables.keys())
    assert "transactions" in tablenames
    assert "saved_results" in tablenames
    assert "bank_connections" in tablenames
    assert "bank_accounts" in tablenames
    assert "connection_history" in tablenames
    assert "merchant_categories" in tablenames
    assert "missed_cashback_reports" in tablenames
    assert "user_connection_limits" in tablenames
    assert len(tablenames) >= 8

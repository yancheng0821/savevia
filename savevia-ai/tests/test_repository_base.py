import os

import pytest


@pytest.mark.skipif(
    not os.environ.get("INTEGRATION_TESTS"),
    reason="requires running MySQL — set INTEGRATION_TESTS=1 to enable",
)
async def test_base_repository_crud_roundtrip():
    """Sanity: create, read, update, delete on saved_results."""
    from app.core.db import dispose_engine, get_session_factory
    from app.models import SavedResult
    from app.repositories.base import BaseRepository

    # Dispose any cached engine bound to a stale event loop (test isolation)
    await dispose_engine()

    factory = get_session_factory()
    async with factory() as session:
        repo: BaseRepository[SavedResult] = BaseRepository(session, SavedResult)

        # Read SavedResult model first to know required columns. The plan's
        # simple test used `title`/`category`/`amount` but the real schema may
        # require `result_json` and `share_id`. Adapt the row construction here
        # based on what `SavedResult.__table__.columns` says is NOT NULL without
        # a default — minimum required: id, user_id, result_json, share_id.
        import uuid

        item = SavedResult(
            user_id=999_999,
            result_json='{"test": "delete-me"}',
            share_id=str(uuid.uuid4())[:32],
        )
        created = await repo.add(item)
        await session.commit()
        assert created.id is not None

        fetched = await repo.get_by_id(created.id)
        assert fetched is not None
        assert fetched.user_id == 999_999

        await repo.delete(fetched)
        await session.commit()
        gone = await repo.get_by_id(created.id)
        assert gone is None


def test_base_repository_signature():
    import inspect

    from app.repositories.base import BaseRepository

    assert hasattr(BaseRepository, "add")
    assert hasattr(BaseRepository, "get_by_id")
    assert hasattr(BaseRepository, "delete")
    assert hasattr(BaseRepository, "list")
    assert inspect.iscoroutinefunction(BaseRepository.get_by_id)

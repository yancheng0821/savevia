"""Tests for SavedResultService — uses a mocked repository so we exercise
the service logic without a real DB."""

from __future__ import annotations

import json
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest


def _result(**kw):
    from app.modules.saved_results.schema import OptimizationResult
    return OptimizationResult.model_validate({
        "monthlyReward": kw.get("monthly", "10.00"),
        "annualReward": kw.get("annual", "120.00"),
        "totalAnnualFees": kw.get("fees", "30.00"),
        "netAnnualSavings": kw.get("net", "90.00"),
        "summary": kw.get("summary", "ok"),
        "recommendations": kw.get("recs", []),
    })


@pytest.fixture
def session():
    s = AsyncMock()
    s.commit = AsyncMock()
    s.add = lambda obj: setattr(obj, "id", 999)  # fake auto-increment
    return s


@pytest.fixture
def repo():
    r = AsyncMock()
    return r


def _build(session, repo):
    from app.modules.saved_results.service import SavedResultService
    return SavedResultService(
        session=session,
        share_base_url="http://example.test",
        repository=repo,
    )


# ---- save_result -------------------------------------------------------

async def test_save_result_for_anonymous_inserts_new_row(session, repo):
    svc = _build(session, repo)
    resp = await svc.save_result(_result(), user_id=None)
    assert len(resp.share_id) == 8
    assert resp.share_url == f"http://example.test/share/{resp.share_id}"
    # No existing-row lookup for anonymous
    repo.select_by_user_id_latest.assert_not_called()
    session.commit.assert_awaited()


async def test_save_result_for_user_with_existing_row_updates_share_id(session, repo):
    from app.models.saved_result import SavedResult

    existing = SavedResult(id=42)
    repo.select_by_user_id_latest.return_value = existing
    repo.update_share_id.return_value = 1

    svc = _build(session, repo)
    resp = await svc.save_result(_result(), user_id=7)

    repo.update_share_id.assert_awaited_once()
    assert repo.update_share_id.await_args.args == (42, resp.share_id)
    assert repo.update_share_id.await_args.kwargs.get("ttl_days") == 30
    # Path that updates should NOT call session.add
    session.commit.assert_awaited()


async def test_save_result_for_user_without_existing_row_inserts_new(session, repo):
    repo.select_by_user_id_latest.return_value = None
    svc = _build(session, repo)
    resp = await svc.save_result(_result(), user_id=7)
    repo.update_share_id.assert_not_called()
    assert resp.share_id  # generated
    session.commit.assert_awaited()


async def test_save_result_share_id_uses_safe_alphabet(session, repo):
    """No 0/O/1/I/l per Java's CHARS."""
    svc = _build(session, repo)
    seen: set[str] = set()
    for _ in range(50):
        resp = await svc.save_result(_result(), user_id=None)
        seen.add(resp.share_id)
    # 50 ids should be unique (collision odds tiny)
    assert len(seen) == 50
    forbidden = set("0O1Il")
    for share_id in seen:
        assert len(share_id) == 8
        assert not (set(share_id) & forbidden), f"forbidden char in {share_id}"


# ---- get_by_share_id ---------------------------------------------------

async def test_get_by_share_id_returns_parsed_result(session, repo):
    from app.models.saved_result import SavedResult

    repo.select_by_share_id.return_value = SavedResult(
        id=1,
        result_json=json.dumps({
            "netAnnualSavings": "150.00", "summary": "round trip",
        }),
    )
    svc = _build(session, repo)
    out = await svc.get_by_share_id("ABCD1234")
    assert out.net_annual_savings == Decimal("150.00")
    assert out.summary == "round trip"


async def test_get_by_share_id_returns_none_when_missing(session, repo):
    repo.select_by_share_id.return_value = None
    svc = _build(session, repo)
    assert await svc.get_by_share_id("missing") is None


# ---- user-result endpoints --------------------------------------------

async def test_save_user_result_updates_when_existing_row(session, repo):
    from app.models.saved_result import SavedResult

    repo.select_by_user_id_latest.return_value = SavedResult(id=1, user_id=7)
    svc = _build(session, repo)
    await svc.save_user_result(_result(), user_id=7)
    repo.update_user_result.assert_awaited_once()
    session.commit.assert_awaited()


async def test_save_user_result_inserts_when_no_existing_row(session, repo):
    repo.select_by_user_id_latest.return_value = None
    svc = _build(session, repo)
    await svc.save_user_result(_result(), user_id=7)
    repo.update_user_result.assert_not_called()
    session.commit.assert_awaited()


async def test_get_user_result_returns_none_when_no_row(session, repo):
    repo.select_by_user_id_latest.return_value = None
    svc = _build(session, repo)
    assert await svc.get_user_result(user_id=7) is None


async def test_get_user_result_returns_parsed_result(session, repo):
    from app.models.saved_result import SavedResult

    repo.select_by_user_id_latest.return_value = SavedResult(
        id=1, user_id=7,
        result_json=json.dumps({"annualReward": "200.00"}),
    )
    svc = _build(session, repo)
    out = await svc.get_user_result(user_id=7)
    assert out.annual_reward == Decimal("200.00")

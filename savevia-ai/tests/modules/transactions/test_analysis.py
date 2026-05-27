"""Tests for TransactionAnalysisService."""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.models.transaction import Transaction


def _txn(*, id: int, amount: str, card_used_id: int | None = None,
         category: str | None = None, merchant: str = "X",
         is_analyzed: bool = False, missed: str | None = None) -> Transaction:
    t = Transaction(
        id=id,
        user_id=42,
        amount=Decimal(amount),
        merchant=merchant,
        category=category,
        transaction_date=datetime(2026, 5, 1),
        card_used_id=card_used_id,
        is_analyzed=is_analyzed,
    )
    if missed is not None:
        t.missed_cashback = Decimal(missed)
    return t


def _card(*, id: int, name: str, bank: str = "TD",
          base: str = "0.01", rules: list | None = None) -> dict:
    return {
        "id": id, "name": name, "bank": bank, "annualFee": "0",
        "baseRewardRate": base, "rewardRules": rules or [],
    }


def _rule(cat: str, rate: str) -> dict:
    return {"category": cat, "rewardRate": rate, "monthlyCapAmount": None}


@pytest.fixture
def deps():
    repo = AsyncMock()
    card_client = AsyncMock()
    categorize = AsyncMock()
    # categorize.categorize is sync (not async)
    categorize.categorize = lambda merchant: "OTHER" if not merchant else "DINING"
    return repo, card_client, categorize


def _service(deps):
    repo, card_client, categorize = deps
    from app.modules.transactions.analysis import TransactionAnalysisService
    return TransactionAnalysisService(
        transaction_repository=repo,
        card_client=card_client,
        categorization=categorize,
    )


# ---- analyze_transactions ---------------------------------------------

async def test_analyze_skips_when_no_card_ids(deps):
    repo, card_client, _ = deps
    svc = _service(deps)
    await svc.analyze_transactions(user_id=42, user_card_ids=[], force=False)
    repo.find_unanalyzed_by_user_id.assert_not_called()
    card_client.get_cards_batch.assert_not_called()


async def test_analyze_skips_when_card_fetch_empty(deps):
    repo, card_client, _ = deps
    card_client.get_cards_batch.return_value = []
    svc = _service(deps)
    await svc.analyze_transactions(user_id=42, user_card_ids=[1])
    repo.find_unanalyzed_by_user_id.assert_not_called()


async def test_analyze_force_resets_then_analyses(deps):
    repo, card_client, _ = deps
    card_client.get_cards_batch.return_value = [
        _card(id=1, name="A", rules=[_rule("DINING", "0.04")]),
    ]
    repo.find_unanalyzed_by_user_id.return_value = [
        _txn(id=10, amount="100", merchant="restaurant"),
    ]
    svc = _service(deps)
    await svc.analyze_transactions(user_id=42, user_card_ids=[1], force=True)
    repo.reset_analysis_by_user_id.assert_awaited_once_with(42)


async def test_analyze_marks_debit_transaction_as_full_miss(deps):
    """card_used_id is None -> actual = 0, missed = optimal."""
    repo, card_client, _ = deps
    card_client.get_cards_batch.return_value = [
        _card(id=1, name="A", rules=[_rule("DINING", "0.04")]),
    ]
    repo.find_unanalyzed_by_user_id.return_value = [
        _txn(id=10, amount="100", merchant="restaurant", card_used_id=None),
    ]
    svc = _service(deps)
    await svc.analyze_transactions(user_id=42, user_card_ids=[1])
    call = repo.update_analysis.await_args
    assert call.kwargs["transaction_id"] == 10
    # 100 * 0.04 = 4.0000
    assert call.kwargs["optimal_cashback"] == Decimal("4.0000")
    assert call.kwargs["actual_cashback"] == Decimal("0")
    assert call.kwargs["missed_cashback"] == Decimal("4.0000")
    assert call.kwargs["best_card_id"] == 1
    assert call.kwargs["category"] == "DINING"


async def test_analyze_credit_card_uses_actual_rate(deps):
    """card_used_id == best card -> missed = 0."""
    repo, card_client, _ = deps
    card_client.get_cards_batch.return_value = [
        _card(id=1, name="A", rules=[_rule("DINING", "0.04")]),
    ]
    repo.find_unanalyzed_by_user_id.return_value = [
        _txn(id=10, amount="100", merchant="diner", card_used_id=1),
    ]
    svc = _service(deps)
    await svc.analyze_transactions(user_id=42, user_card_ids=[1])
    call = repo.update_analysis.await_args
    assert call.kwargs["optimal_cashback"] == Decimal("4.0000")
    assert call.kwargs["actual_cashback"] == Decimal("4.0000")
    assert call.kwargs["missed_cashback"] == Decimal("0")


async def test_analyze_credit_card_lower_rate_marks_partial_miss(deps):
    """Using card-B (2%) when card-A (4%) was best — missed = 2."""
    repo, card_client, _ = deps
    card_client.get_cards_batch.return_value = [
        _card(id=1, name="A", rules=[_rule("DINING", "0.04")]),
        _card(id=2, name="B", rules=[_rule("DINING", "0.02")]),
    ]
    repo.find_unanalyzed_by_user_id.return_value = [
        _txn(id=10, amount="100", merchant="diner", card_used_id=2),
    ]
    svc = _service(deps)
    await svc.analyze_transactions(user_id=42, user_card_ids=[1, 2])
    call = repo.update_analysis.await_args
    assert call.kwargs["best_card_id"] == 1
    assert call.kwargs["optimal_cashback"] == Decimal("4.0000")
    assert call.kwargs["actual_cashback"] == Decimal("2.0000")
    assert call.kwargs["missed_cashback"] == Decimal("2.0000")


# ---- get_recent_transactions ------------------------------------------

async def test_get_recent_transactions_returns_dto_with_hydrated_card_names(deps):
    repo, card_client, _ = deps
    card_client.get_cards_batch.return_value = [
        _card(id=1, name="Cash Visa", bank="TD",
              rules=[_rule("DINING", "0.04")]),
    ]
    repo.find_recent_by_user_id.return_value = [
        _txn(id=10, amount="100", merchant="diner", card_used_id=1,
             category="DINING", is_analyzed=True),
    ]
    svc = _service(deps)
    results = await svc.get_recent_transactions(
        user_id=42, limit=10, user_card_ids=[1],
    )
    assert len(results) == 1
    dto = results[0]
    assert dto.card_used_id == 1
    assert dto.card_used_name == "TD Cash Visa"
    assert dto.is_debit_transaction is False


async def test_get_recent_transactions_flags_debit_transaction(deps):
    repo, card_client, _ = deps
    repo.find_recent_by_user_id.return_value = [
        _txn(id=11, amount="50", merchant="any", card_used_id=None,
             category="OTHER", is_analyzed=True),
    ]
    svc = _service(deps)
    results = await svc.get_recent_transactions(
        user_id=42, limit=10, user_card_ids=[],
    )
    assert results[0].is_debit_transaction is True


# ---- get_missed_cashback_summary --------------------------------------

async def test_summary_aggregates_per_category_and_top_recommendations(deps):
    repo, card_client, _ = deps
    card_client.get_cards_batch.return_value = [
        _card(id=1, name="A", bank="TD", rules=[_rule("DINING", "0.04")]),
        _card(id=2, name="B", bank="CIBC", rules=[_rule("GROCERY", "0.06")]),
    ]
    repo.find_by_user_and_date_range.return_value = [
        _txn(id=10, amount="100", merchant="diner", card_used_id=None,
             category="DINING", is_analyzed=True, missed="4.00"),
        _txn(id=11, amount="200", merchant="store", card_used_id=None,
             category="GROCERY", is_analyzed=True, missed="12.00"),
    ]
    svc = _service(deps)
    summary = await svc.get_missed_cashback_summary(
        user_id=42, user_card_ids=[1, 2],
    )
    assert summary.total_transactions == 2
    assert summary.debit_transactions == 2
    assert summary.total_spending == Decimal("300")
    assert summary.total_missed_cashback == Decimal("16.00")

    # 2 categories present; sorted by spending DESC -> GROCERY first
    cats = [b.category for b in summary.category_breakdown]
    assert cats == ["GROCERY", "DINING"]

    # Both cards should appear as top recommendations
    recs = {r.card_id for r in summary.top_recommendations}
    assert recs == {1, 2}


async def test_summary_runs_pending_analysis_inflight(deps):
    repo, card_client, _ = deps
    card_client.get_cards_batch.return_value = [
        _card(id=1, name="A", rules=[_rule("DINING", "0.04")]),
    ]
    pending = _txn(id=10, amount="100", merchant="diner",
                   card_used_id=None, is_analyzed=False)
    final = _txn(id=10, amount="100", merchant="diner", card_used_id=None,
                 category="DINING", is_analyzed=True, missed="4.00")

    # First call returns the unanalyzed row; second call (after in-flight
    # analysis) returns the analyzed version.
    repo.find_by_user_and_date_range.side_effect = [[pending], [final]]
    svc = _service(deps)
    summary = await svc.get_missed_cashback_summary(
        user_id=42, user_card_ids=[1],
    )
    repo.update_analysis.assert_awaited()  # _analyze_one was called
    assert summary.total_missed_cashback == Decimal("4.00")

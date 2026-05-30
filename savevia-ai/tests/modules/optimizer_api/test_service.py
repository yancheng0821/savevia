"""Tests for CashbackOptimizerService."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock

import pytest


def _card(*, id: int, name: str, bank: str = "TD", annual_fee: str = "0",
          base: str = "0.01", rules: list | None = None) -> dict:
    return {
        "id": id, "name": name, "bank": bank, "annualFee": annual_fee,
        "baseRewardRate": base, "rewardRules": rules or [], "noFxFee": False,
        "cardType": "VISA",
    }


def _rule(cat: str, rate: str, cap: str | None = None) -> dict:
    return {"category": cat, "rewardRate": rate, "monthlyCapAmount": cap}


@pytest.fixture
def clients():
    return AsyncMock(), AsyncMock()  # (card, user)


def _build(clients):
    from app.modules.optimizer_api.service import CashbackOptimizerService
    card, user = clients
    return CashbackOptimizerService(card_client=card, user_client=user)


async def test_raises_when_no_cards_selected(clients):
    from app.modules.optimizer_api.schema import OptimizationRequest
    from app.modules.optimizer_api.service import OptimizerInputError

    svc = _build(clients)
    with pytest.raises(OptimizerInputError) as exc:
        await svc.optimize(OptimizationRequest(card_ids=[], monthly_spending={"DINING": Decimal("100")}))
    assert exc.value.code == "NO_CARDS_SELECTED"


async def test_raises_when_no_spending_data(clients):
    from app.modules.optimizer_api.schema import OptimizationRequest
    from app.modules.optimizer_api.service import OptimizerInputError

    svc = _build(clients)
    with pytest.raises(OptimizerInputError) as exc:
        await svc.optimize(OptimizationRequest(card_ids=[1], monthly_spending={}))
    assert exc.value.code == "INVALID_SPENDING_DATA"


async def test_raises_when_card_fetch_returns_empty(clients):
    from app.modules.optimizer_api.schema import OptimizationRequest
    from app.modules.optimizer_api.service import OptimizerInputError

    card, user = clients
    card.get_cards_batch.return_value = []
    svc = _build(clients)
    with pytest.raises(OptimizerInputError) as exc:
        await svc.optimize(OptimizationRequest(
            card_ids=[1], monthly_spending={"DINING": Decimal("100")},
        ))
    assert exc.value.code == "CARD_NOT_FOUND"


async def test_picks_best_card_per_category_and_aggregates(clients):
    from app.modules.optimizer_api.schema import OptimizationRequest

    card, user = clients
    card.get_cards_batch.return_value = [
        _card(id=1, name="A", annual_fee="0",
              rules=[_rule("DINING", "0.04"), _rule("GROCERY", "0.01")]),
        _card(id=2, name="B", annual_fee="120",
              rules=[_rule("DINING", "0.02"), _rule("GROCERY", "0.06")]),
    ]

    svc = _build(clients)
    result = await svc.optimize(OptimizationRequest(
        card_ids=[1, 2],
        monthly_spending={
            "DINING": Decimal("200"),    # A wins: 200 * 0.04 = 8.00
            "GROCERY": Decimal("500"),   # B wins: 500 * 0.06 = 30.00
        },
    ))

    # monthly_reward = 8 + 30 = 38
    assert result.monthly_reward == Decimal("38.00")
    # annual = 38 * 12 = 456
    assert result.annual_reward == Decimal("456.00")
    # fees: 0 + 120 = 120
    assert result.total_annual_fees == Decimal("120.00")
    # net = 456 - 120 = 336
    assert result.net_annual_savings == Decimal("336.00")
    # both recommendations present, in input order
    assert {r.category for r in result.recommendations} == {"DINING", "GROCERY"}
    dining = next(r for r in result.recommendations if r.category == "DINING")
    assert dining.recommended_card["id"] == 1
    grocery = next(r for r in result.recommendations if r.category == "GROCERY")
    assert grocery.recommended_card["id"] == 2


async def test_skips_unknown_category_and_zero_amount(clients):
    from app.modules.optimizer_api.schema import OptimizationRequest

    card, user = clients
    card.get_cards_batch.return_value = [_card(id=1, name="A", base="0.02")]

    svc = _build(clients)
    result = await svc.optimize(OptimizationRequest(
        card_ids=[1],
        monthly_spending={
            "DINING": Decimal("100"),
            "GARBAGE_CATEGORY": Decimal("999"),  # ignored
            "GAS": Decimal("0"),                  # ignored
        },
    ))
    cats = {r.category for r in result.recommendations}
    assert cats == {"DINING"}


async def test_summary_text_matches_java_format(clients):
    from app.modules.optimizer_api.schema import OptimizationRequest

    card, user = clients
    card.get_cards_batch.return_value = [_card(id=1, name="A", base="0.02")]

    svc = _build(clients)
    result = await svc.optimize(OptimizationRequest(
        card_ids=[1], monthly_spending={"DINING": Decimal("100")},
    ))
    assert "you can earn $24.00 per year in cashback" in result.summary
    assert "deducting $0.00 in annual fees" in result.summary
    assert "net savings would be $24.00" in result.summary


async def test_ai_path_checks_quota_when_enabled_and_user_present(clients):
    from app.modules.optimizer_api.schema import OptimizationRequest

    card, user = clients
    card.get_cards_batch.return_value = [_card(id=1, name="A", base="0.02")]
    user.check_can_use_ai.return_value = True

    svc = _build(clients)
    await svc.optimize(OptimizationRequest(
        user_id=42, card_ids=[1],
        monthly_spending={"DINING": Decimal("100")},
        enable_ai_explanation=True,
    ))

    user.check_can_use_ai.assert_awaited_once_with(user_id=42)
    user.record_ai_usage.assert_awaited_once_with(user_id=42)


async def test_ai_path_skips_record_when_over_quota(clients):
    from app.modules.optimizer_api.schema import OptimizationRequest

    card, user = clients
    card.get_cards_batch.return_value = [_card(id=1, name="A", base="0.02")]
    user.check_can_use_ai.return_value = False

    svc = _build(clients)
    await svc.optimize(OptimizationRequest(
        user_id=42, card_ids=[1],
        monthly_spending={"DINING": Decimal("100")},
        enable_ai_explanation=True,
    ))
    user.record_ai_usage.assert_not_called()


async def test_ai_path_skipped_for_guest_user(clients):
    from app.modules.optimizer_api.schema import OptimizationRequest

    card, user = clients
    card.get_cards_batch.return_value = [_card(id=1, name="A", base="0.02")]

    svc = _build(clients)
    await svc.optimize(OptimizationRequest(
        user_id=None, card_ids=[1],
        monthly_spending={"DINING": Decimal("100")},
        enable_ai_explanation=True,
    ))
    user.check_can_use_ai.assert_not_called()


async def test_ai_explanations_fill_recommendation_when_allowed(clients):
    from unittest.mock import AsyncMock

    from app.modules.optimizer_api.schema import OptimizationRequest

    card, user = clients
    card.get_cards_batch.return_value = [_card(id=1, name="A", base="0.02")]
    user.check_can_use_ai.return_value = True

    gen = AsyncMock()

    async def _fill(recs, **kw):
        for r in recs:
            r.ai_explanation = "explained"

    gen.generate_explanations.side_effect = _fill

    from app.modules.optimizer_api.service import CashbackOptimizerService
    svc = CashbackOptimizerService(
        card_client=card, user_client=user, explanation_generator=gen,
    )
    result = await svc.optimize(OptimizationRequest(
        user_id=42, card_ids=[1], monthly_spending={"DINING": Decimal("100")},
        enable_ai_explanation=True,
    ))
    assert result.recommendations[0].ai_explanation == "explained"
    user.record_ai_usage.assert_awaited_once_with(user_id=42)


async def test_record_ai_usage_429_does_not_propagate(clients):
    from app.clients._base import JavaServiceError
    from app.modules.optimizer_api.schema import OptimizationRequest

    card, user = clients
    card.get_cards_batch.return_value = [_card(id=1, name="A", base="0.02")]
    user.check_can_use_ai.return_value = True
    user.record_ai_usage.side_effect = JavaServiceError(
        "savevia-user", 429, "limit hit", path="/x", method="POST",
    )
    svc = _build(clients)
    # Must NOT raise
    result = await svc.optimize(OptimizationRequest(
        user_id=42, card_ids=[1],
        monthly_spending={"DINING": Decimal("100")},
        enable_ai_explanation=True,
    ))
    assert result.summary

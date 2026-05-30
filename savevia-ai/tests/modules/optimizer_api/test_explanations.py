from decimal import Decimal
from unittest.mock import AsyncMock


def _rec(category="DINING"):
    from app.modules.optimizer_api.schema import CategoryRecommendation
    return CategoryRecommendation(
        category=category, monthly_spend=Decimal("200"),
        recommended_card={"id": 1, "bank": "TD", "name": "TD Cash Back Visa",
                          "annualFee": "0", "baseRewardRate": "0.04", "rewardRules": []},
        reward_rate=Decimal("0.04"), monthly_reward=Decimal("8.00"),
    )


def _gen(model):
    from app.modules.optimizer_api.explanations import ExplanationGenerator
    return ExplanationGenerator(model_factory=lambda: model)


async def test_generate_explanations_fills_ai_explanation():
    fake_model = AsyncMock()
    fake_model.ainvoke.return_value = type("M", (), {"content": "Use TD for dining."})()
    gen = _gen(fake_model)

    recs = [_rec("DINING"), _rec("GROCERY")]
    await gen.generate_explanations(
        recs,
        user_cards=[{"id": 1, "bank": "TD", "name": "TD Cash Back Visa"}],
        locale="en",
    )
    assert recs[0].ai_explanation == "Use TD for dining."
    assert recs[1].ai_explanation == "Use TD for dining."
    assert fake_model.ainvoke.await_count == 2


async def test_generate_explanations_swallows_errors():
    fake_model = AsyncMock()
    fake_model.ainvoke.side_effect = RuntimeError("openai down")
    gen = _gen(fake_model)
    recs = [_rec("DINING")]
    await gen.generate_explanations(recs, user_cards=[], locale="en")  # must not raise
    assert recs[0].ai_explanation is None


async def test_single_prompt_contains_earnings_and_category():
    gen = _gen(AsyncMock())
    prompt = gen._build_single_prompt(
        _rec("DINING"),
        [{"id": 1, "bank": "TD", "name": "TD Cash Back Visa"}],
    )
    assert "Category: Dining." in prompt
    assert "$8.00/month" in prompt
    assert "$96.00/year" in prompt
    assert "4.0% rate" in prompt


async def test_fee_coverage_insight_appears_when_annual_fee_positive():
    from app.modules.optimizer_api.schema import CategoryRecommendation

    gen = _gen(AsyncMock())
    rec = CategoryRecommendation(
        category="DINING", monthly_spend=Decimal("200"),
        recommended_card={"id": 1, "bank": "TD", "name": "TD Visa", "annualFee": "120"},
        reward_rate=Decimal("0.04"), monthly_reward=Decimal("8.00"),
    )
    # annual reward 96, fee 120 -> 80% coverage
    prompt = gen._build_single_prompt(rec, [])
    assert "80% of the $120 annual fee" in prompt


async def test_language_instruction_switches_on_locale():
    from app.modules.optimizer_api.explanations import _language_instruction
    assert "Simplified Chinese" in _language_instruction("zh")
    assert "Japanese" in _language_instruction("ja")
    assert "English" in _language_instruction(None)
    assert "English" in _language_instruction("pt")  # unknown -> default

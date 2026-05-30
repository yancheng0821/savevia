"""ExplanationGenerator — port of OpenAiService.generateExplanations.

Per-recommendation, locale-aware LLM explanations. System message, language
instruction, and single-category prompt are copied verbatim from
com.savevia.optimizer.service.OpenAiService (buildSystemMessage:127-152,
getLanguageInstruction:171-182, buildSinglePrompt:187-242). Errors are
swallowed (explanation stays empty), matching Java.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING, Any

from app.core.config import get_settings
from app.core.logging import get_logger
from app.modules.locale.categories import SpendingCategory
from app.modules.optimizer.cashback_calculator import get_reward_rate

if TYPE_CHECKING:
    from app.modules.optimizer_api.schema import CategoryRecommendation

_log = get_logger("savevia-ai.explanations")
_MAX_CONCURRENCY = 10
_TWO_DP = Decimal("0.01")

# Verbatim from OpenAiService.getLanguageInstruction (:171-182)
_LANGUAGE_INSTRUCTIONS = {
    "zh": "LANGUAGE: Respond in Simplified Chinese. 用简洁专业的语气。",
    "zh-cn": "LANGUAGE: Respond in Simplified Chinese. 用简洁专业的语气。",
    "zh-tw": "LANGUAGE: Respond in Simplified Chinese. 用简洁专业的语气。",
    "ja": "LANGUAGE: Respond in Japanese. 簡潔でプロフェッショナルな表現で。",
    "ko": "LANGUAGE: Respond in Korean. 간결하고 전문적인 어조로.",
    "fr": "LANGUAGE: Respond in French. Style concis et professionnel.",
    "es": "LANGUAGE: Respond in Spanish. Estilo conciso y profesional.",
}
_DEFAULT_LANGUAGE_INSTRUCTION = "LANGUAGE: Respond in English."


def _language_instruction(locale: str | None) -> str:
    if locale is None:
        locale = "en"
    return _LANGUAGE_INSTRUCTIONS.get(locale.lower(), _DEFAULT_LANGUAGE_INSTRUCTION)


# Verbatim from OpenAiService.buildSystemMessage (:130-151)
_SYSTEM_TEMPLATE = """\
You are a professional Canadian financial advisor providing credit card optimization insights.

Rephrase the pre-calculated data below into a clear, professional summary. Vary sentence structure naturally.

TONE: Professional financial advisor - confident, informative, trustworthy. Not casual, not robotic.

DO:
- Use the exact numbers provided
- Vary how you present the information
- Sound like a professional giving advice

DON'T:
- Start with greetings ("Hey!", "Hi there!")
- Use casual slang
- Do any calculations yourself
- Use the same sentence pattern repeatedly

Keep to 2-3 sentences. Plain text only.

%s
"""


def _default_model_factory() -> Any:
    from langchain_openai import ChatOpenAI

    s = get_settings()
    return ChatOpenAI(
        model=s.openai_model,
        temperature=0.8,
        max_tokens=250,
        api_key=s.openai_api_key,
    )


class ExplanationGenerator:
    def __init__(self, *, model_factory: Callable[[], Any] = _default_model_factory):
        self._model_factory = model_factory

    async def generate_explanations(
        self,
        recommendations: list[CategoryRecommendation],
        user_cards: list[dict],
        locale: str | None,
    ) -> None:
        if not recommendations:
            return
        if not get_settings().openai_api_key:
            _log.info("openai_disabled_no_key")
            return

        model = self._model_factory()
        system = _SYSTEM_TEMPLATE % _language_instruction(locale)
        sem = asyncio.Semaphore(_MAX_CONCURRENCY)

        async def _one(rec: CategoryRecommendation) -> None:
            async with sem:
                try:
                    prompt = self._build_single_prompt(rec, user_cards)
                    msg = await model.ainvoke(
                        [("system", system), ("human", prompt)]
                    )
                    text = (getattr(msg, "content", "") or "").strip()
                    rec.ai_explanation = text or None
                except Exception as e:  # noqa: BLE001 — mirror Java swallow
                    _log.warning(
                        "explanation_failed", category=rec.category, error=str(e)
                    )

        await asyncio.gather(*(_one(r) for r in recommendations))

    # ---- prompt construction (verbatim port of buildSinglePrompt) --------

    def _build_single_prompt(
        self, rec: CategoryRecommendation, user_cards: list[dict]
    ) -> str:
        best_card = rec.recommended_card or {}
        cat = SpendingCategory.from_str(rec.category)
        display_name = cat.display_name if cat is not None else rec.category

        monthly_reward = Decimal(rec.monthly_reward)
        annual_reward = (monthly_reward * 12).quantize(_TWO_DP, rounding=ROUND_HALF_UP)
        annual_fee = (
            Decimal(str(best_card.get("annualFee")))
            if best_card.get("annualFee") is not None
            else Decimal("0")
        )

        insights: list[str] = []

        # Insight 1: Earnings
        insights.append(
            "Category: %s. Card: %s %s. You earn $%.2f/month, $%.2f/year at %.1f%% rate."
            % (
                display_name,
                best_card.get("bank", ""),
                best_card.get("name", ""),
                float(monthly_reward),
                float(annual_reward),
                float(rec.reward_rate) * 100,
            )
        )

        # Insight 2: Fee coverage (if applicable)
        if annual_fee > 0:
            coverage_percent = int(
                (annual_reward * 100 / annual_fee).quantize(
                    Decimal("1"), rounding=ROUND_HALF_UP
                )
            )
            if coverage_percent >= 100:
                insights.append(
                    "This category ALONE covers the $%.0f annual fee (and then some)."
                    % float(annual_fee)
                )
            else:
                insights.append(
                    "This category covers %d%% of the $%.0f annual fee."
                    % (coverage_percent, float(annual_fee))
                )

        # Insight 3: Comparison with the first alternative card
        if cat is not None and len(user_cards) > 1:
            for card in user_cards:
                if card.get("id") != best_card.get("id"):
                    card_rate = get_reward_rate(card, cat)
                    alt_annual = (
                        Decimal(rec.monthly_spend) * card_rate * 12
                    ).quantize(_TWO_DP, rounding=ROUND_HALF_UP)
                    diff_annual = (annual_reward - alt_annual).quantize(
                        _TWO_DP, rounding=ROUND_HALF_UP
                    )
                    if diff_annual > 0:
                        insights.append(
                            "You earn $%.2f/year MORE than using %s %s."
                            % (float(diff_annual), card.get("bank", ""), card.get("name", ""))
                        )
                    break

        # Insight 4: travel-points cards
        card_name = str(best_card.get("name", "")).lower()
        if any(
            kw in card_name
            for kw in ("cobalt", "gold", "platinum", "aeroplan", "avion")
        ):
            insights.append(
                "Bonus: These are travel points - redeemable for flights and hotels."
            )

        return "\n".join(insights)

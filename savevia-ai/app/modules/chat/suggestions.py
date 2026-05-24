"""Static suggested-question lists per locale. Verbatim port of
com.savevia.optimizer.service.ChatService.getSuggestions.
"""

from __future__ import annotations

_SUGGESTIONS: dict[str, list[str]] = {
    "en": [
        "Which card for my Europe trip next month?",
        "What's the best card for groceries?",
        "Which card is best for gas?",
        "What card gives the most cashback online?",
    ],
    "zh": [
        "下个月去欧洲旅游用哪张卡？",
        "买菜用哪张卡最划算？",
        "加油用哪张卡最好？",
        "网购用哪张卡返现最多？",
    ],
    "fr": [
        "Quelle carte pour voyager en Europe?",
        "Quelle carte pour l'epicerie?",
        "Quelle carte pour l'essence?",
        "Quelle carte pour les achats en ligne?",
    ],
    "es": [
        "Cual tarjeta usar para viajar a Europa?",
        "Cual tarjeta para compras de supermercado?",
        "Cual tarjeta para gasolina?",
        "Cual tarjeta para compras en linea?",
    ],
    "ja": [
        "ヨーロッパ旅行にはどのカード?",
        "スーパーでの買い物に最適なカードは?",
        "ガソリン代に最適なカードは?",
        "オンラインショッピングに最適なカードは?",
    ],
    "ko": [
        "유럽 여행에 어떤 카드를 사용해야 하나요?",
        "식료품 구매에 가장 좋은 카드는?",
        "주유에 가장 좋은 카드는?",
        "온라인 쇼핑에 가장 좋은 카드는?",
    ],
}


def get_suggestions(locale: str | None) -> list[str]:
    """Return the suggestion list for the given locale (falls back to 'en')."""
    if not locale:
        return _SUGGESTIONS["en"]
    key = locale.lower().split("-", 1)[0]
    return _SUGGESTIONS.get(key, _SUGGESTIONS["en"])

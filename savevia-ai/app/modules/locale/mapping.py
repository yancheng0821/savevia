"""Locale-string helpers — mirrors com.savevia.optimizer.service.ChatService."""

from __future__ import annotations

_LANG_BY_LOCALE = {
    "zh": "zh", "zh-cn": "zh", "zh-tw": "zh",
    "fr": "fr",
    "es": "es",
    "ja": "ja",
    "ko": "ko",
}

_LANGUAGE_NAMES = {
    "zh": "Chinese (Simplified)",
    "fr": "French",
    "es": "Spanish",
    "ja": "Japanese",
    "ko": "Korean",
    "en": "English",
}


def locale_to_lang(locale: str | None) -> str:
    """Map full locale (e.g., 'zh-CN', 'fr-CA') to the 2-letter lang used by
    Java's CardServiceClient.getCardUsageGuide(?lang=...). Unknown → 'en'."""
    if not locale:
        return "en"
    key = locale.lower()
    if key in _LANG_BY_LOCALE:
        return _LANG_BY_LOCALE[key]
    prefix = key.split("-", 1)[0]
    return _LANG_BY_LOCALE.get(prefix, "en")


def language_name(locale: str | None) -> str:
    """Human-readable language name used in the system prompt's
    'LANGUAGE: Respond in <name>' directive."""
    return _LANGUAGE_NAMES.get(locale_to_lang(locale), "English")

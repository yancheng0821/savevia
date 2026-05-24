"""Tests for SpendingCategory enum + locale helpers."""

import pytest


def test_spending_category_has_21_values():
    from app.modules.locale.categories import SpendingCategory
    assert len(list(SpendingCategory)) == 21


def test_spending_category_names_match_java():
    """The .name of each enum must match Java's name() output so LLM-generated
    tool args (which use the Java names) deserialise without translation."""
    from app.modules.locale.categories import SpendingCategory
    expected = {
        "DINING", "GROCERY", "GAS", "TRAVEL", "STREAMING", "TRANSIT", "PHARMACY",
        "RENT", "RECURRING", "ONLINE_SHOPPING", "FOREIGN", "RETAIL", "ENTERTAINMENT",
        "PERSONAL_SERVICES", "HOME_IMPROVEMENT", "WHOLESALE", "INSURANCE", "TELECOM",
        "EV_CHARGING", "LIQUOR", "OTHER",
    }
    assert {c.name for c in SpendingCategory} == expected


def test_display_name_matches_java():
    from app.modules.locale.categories import SpendingCategory
    assert SpendingCategory.DINING.display_name == "Dining"
    assert SpendingCategory.ONLINE_SHOPPING.display_name == "Online Shopping"
    assert SpendingCategory.RECURRING.display_name == "Recurring Bills"
    assert SpendingCategory.PERSONAL_SERVICES.display_name == "Personal Services"


def test_display_name_zh_matches_java():
    from app.modules.locale.categories import SpendingCategory
    assert SpendingCategory.DINING.display_name_zh == "餐饮"
    assert SpendingCategory.ONLINE_SHOPPING.display_name_zh == "网购"


def test_from_str_case_insensitive():
    from app.modules.locale.categories import SpendingCategory
    assert SpendingCategory.from_str("dining") is SpendingCategory.DINING
    assert SpendingCategory.from_str("DINING") is SpendingCategory.DINING
    assert SpendingCategory.from_str("Online_Shopping") is SpendingCategory.ONLINE_SHOPPING


def test_from_str_invalid_returns_none():
    from app.modules.locale.categories import SpendingCategory
    assert SpendingCategory.from_str("garbage") is None
    assert SpendingCategory.from_str("") is None
    assert SpendingCategory.from_str(None) is None  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "locale,expected_lang",
    [
        ("zh", "zh"), ("zh-CN", "zh"), ("zh-cn", "zh"), ("zh-TW", "zh"),
        ("fr", "fr"), ("fr-CA", "fr"),
        ("es", "es"), ("es-MX", "es"),
        ("ja", "ja"), ("ko", "ko"),
        ("en", "en"), ("en-US", "en"),
        ("", "en"), (None, "en"),
        ("xx-XX", "en"),
    ],
)
def test_locale_to_lang(locale, expected_lang):
    from app.modules.locale.mapping import locale_to_lang
    assert locale_to_lang(locale) == expected_lang


@pytest.mark.parametrize(
    "locale,expected_name",
    [
        ("zh", "Chinese (Simplified)"),
        ("zh-CN", "Chinese (Simplified)"),
        ("fr", "French"),
        ("es", "Spanish"),
        ("ja", "Japanese"),
        ("ko", "Korean"),
        ("en", "English"),
        (None, "English"),
        ("xx", "English"),
    ],
)
def test_language_name(locale, expected_name):
    from app.modules.locale.mapping import language_name
    assert language_name(locale) == expected_name

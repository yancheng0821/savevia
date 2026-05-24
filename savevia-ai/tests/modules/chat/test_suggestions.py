"""Tests for the static suggestions endpoint payload."""

import pytest


@pytest.mark.parametrize(
    "locale,expected_count,must_contain",
    [
        ("en", 4, "Europe trip"),
        ("zh", 4, "买菜"),
        ("zh-CN", 4, "买菜"),
        ("fr", 4, "Europe"),
        ("es", 4, "Europa"),
        ("ja", 4, "ヨーロッパ"),
        ("ko", 4, "유럽"),
        (None, 4, "Europe trip"),
        ("xx", 4, "Europe trip"),
    ],
)
def test_get_suggestions_returns_localized_list(locale, expected_count, must_contain):
    from app.modules.chat.suggestions import get_suggestions
    out = get_suggestions(locale)
    assert len(out) == expected_count
    assert any(must_contain in s for s in out)

"""Tests for the TOOLS barrel."""


def test_tools_list_has_all_six_in_canonical_order():
    from app.modules.tools import TOOLS

    names = [t.name for t in TOOLS]
    assert names == [
        "get_user_cards",
        "calculate_reward",
        "get_best_card",
        "compare_cards",
        "get_card_usage_guide",
        "search_cards",
    ]

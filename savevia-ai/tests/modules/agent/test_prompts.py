"""Tests for the agent system prompt builder."""

import pytest


def _card(*, id: int, bank: str, name: str, fee: str) -> dict:
    return {
        "id": id, "bank": bank, "name": name, "annualFee": fee,
        "baseRewardRate": "0.01", "rewardRules": [], "noFxFee": False,
    }


def test_includes_header_tools_role_security_language():
    from app.modules.agent.prompts import build_agent_system_prompt

    p = build_agent_system_prompt(user_cards=[], memory_context="", locale="en")
    assert "SaveVia's AI Card Advisor" in p
    assert "AVAILABLE TOOLS:" in p
    assert "WHEN TO USE TOOLS:" in p
    assert "YOUR ROLE:" in p
    assert "CRITICAL CONSTRAINTS:" in p
    assert "SECURITY:" in p
    assert p.rstrip().endswith("LANGUAGE: Respond in English.")


def test_lists_all_six_tools():
    from app.modules.agent.prompts import build_agent_system_prompt

    p = build_agent_system_prompt(user_cards=[], memory_context="", locale="en")
    for name in [
        "get_user_cards", "calculate_reward", "get_best_card",
        "compare_cards", "get_card_usage_guide", "search_cards",
    ]:
        assert name in p


def test_no_cards_block_when_empty():
    from app.modules.agent.prompts import build_agent_system_prompt

    p = build_agent_system_prompt(user_cards=[], memory_context="", locale="en")
    assert "user has not selected any cards yet" in p.lower()


def test_lists_user_cards_with_id_bank_name_and_fee():
    from app.modules.agent.prompts import build_agent_system_prompt

    cards = [
        _card(id=101, bank="TD", name="Cash Visa", fee="0"),
        _card(id=202, bank="CIBC", name="Aventura", fee="139"),
    ]
    p = build_agent_system_prompt(user_cards=cards, memory_context="", locale="en")
    assert "ID:101 TD Cash Visa" in p
    assert "Annual Fee: $0" in p
    assert "ID:202 CIBC Aventura" in p
    assert "Annual Fee: $139" in p


def test_memory_context_is_injected_after_header():
    from app.modules.agent.prompts import build_agent_system_prompt

    memory = "USER MEMORY (Long-term context...):\n[Core] Prefers cashback."
    p = build_agent_system_prompt(user_cards=[], memory_context=memory, locale="en")
    assert memory in p
    assert p.index(memory) < p.index("AVAILABLE TOOLS:")


def test_empty_memory_context_does_not_inject_block():
    from app.modules.agent.prompts import build_agent_system_prompt

    p = build_agent_system_prompt(user_cards=[], memory_context="", locale="en")
    assert "USER MEMORY" not in p


@pytest.mark.parametrize(
    "locale,expected_name",
    [
        ("zh", "Chinese (Simplified)"),
        ("fr", "French"),
        ("es", "Spanish"),
        ("ja", "Japanese"),
        ("ko", "Korean"),
        ("en", "English"),
        (None, "English"),
    ],
)
def test_language_directive_changes_with_locale(locale, expected_name):
    from app.modules.agent.prompts import build_agent_system_prompt

    p = build_agent_system_prompt(user_cards=[], memory_context="", locale=locale)
    assert p.rstrip().endswith(f"LANGUAGE: Respond in {expected_name}.")

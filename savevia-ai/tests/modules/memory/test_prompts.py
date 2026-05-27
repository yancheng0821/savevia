"""Tests for the extraction system prompt."""


def test_prompt_starts_with_memory_extraction_assistant_intro():
    from app.modules.memory.prompts import EXTRACTION_SYSTEM_PROMPT
    assert EXTRACTION_SYSTEM_PROMPT.startswith(
        "You are a memory extraction assistant for SaveVia"
    )


def test_prompt_includes_all_five_top_level_json_keys():
    from app.modules.memory.prompts import EXTRACTION_SYSTEM_PROMPT
    for key in [
        '"identity"', '"spending"', '"preference"',
        '"exclusion"', '"lifestyle"', '"recommendations"', '"summary"',
    ]:
        assert key in EXTRACTION_SYSTEM_PROMPT, f"missing JSON key in prompt: {key}"


def test_prompt_enumerates_user_type_values():
    """Match Java's enum list verbatim — drift here breaks fact-extraction quality."""
    from app.modules.memory.prompts import EXTRACTION_SYSTEM_PROMPT
    assert (
        '"user_type": "student|new_immigrant|pr_holder|citizen|work_permit|visitor|null"'
        in EXTRACTION_SYSTEM_PROMPT
    )


def test_prompt_enumerates_income_ranges():
    from app.modules.memory.prompts import EXTRACTION_SYSTEM_PROMPT
    assert (
        '"income_range": "under_30k|30k_60k|60k_100k|100k_plus|null"'
        in EXTRACTION_SYSTEM_PROMPT
    )


def test_prompt_documents_rules_section():
    from app.modules.memory.prompts import EXTRACTION_SYSTEM_PROMPT
    assert "Rules:" in EXTRACTION_SYSTEM_PROMPT
    assert "Only extract information explicitly mentioned" in EXTRACTION_SYSTEM_PROMPT
    assert "monthly CAD estimates" in EXTRACTION_SYSTEM_PROMPT


def test_prompt_is_immutable_constant():
    import app.modules.memory.prompts as p
    assert isinstance(p.EXTRACTION_SYSTEM_PROMPT, str)
    assert len(p.EXTRACTION_SYSTEM_PROMPT) > 1000

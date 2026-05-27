"""Tests for the memory extraction Pydantic schema.

The same model must:
  - parse the LLM's snake_case JSON, AND
  - serialise to camelCase JSON for Java consumption.
"""

import json


def test_parses_full_llm_response():
    from app.modules.memory.schema import MemoryExtractionResult

    payload = {
        "identity": {
            "user_type": "new_immigrant",
            "residency_years": 2,
            "occupation": "engineer",
            "income_range": "60k_100k",
        },
        "spending": {
            "monthly_grocery": 500, "monthly_gas": 100, "monthly_dining": 200,
            "monthly_online": 300, "monthly_travel": 0, "monthly_total": 1200,
        },
        "preference": {
            "annual_fee_tolerance": "100",
            "reward_type": "cashback",
            "preferred_banks": ["TD", "CIBC"],
            "preferred_networks": ["VISA"],
        },
        "exclusion": {
            "excluded_banks": ["RBC"],
            "excluded_networks": None,
            "excluded_cards": None,
        },
        "lifestyle": {
            "travel_frequency": "yearly",
            "has_children": True,
            "has_pets": False,
            "commute_method": "transit",
        },
        "recommendations": [
            {"card_name": "TD Cash", "card_id": 101, "user_response": "accepted"},
        ],
        "summary": "New immigrant, prefers cashback.",
    }

    result = MemoryExtractionResult.model_validate(payload)
    assert result.identity.user_type == "new_immigrant"
    assert result.spending.monthly_grocery == 500
    assert result.preference.preferred_banks == ["TD", "CIBC"]
    assert result.exclusion.excluded_banks == ["RBC"]
    assert result.lifestyle.has_children is True
    assert result.recommendations[0].card_id == 101
    assert result.summary.startswith("New immigrant")


def test_parses_partial_response_with_null_subsections():
    from app.modules.memory.schema import MemoryExtractionResult

    result = MemoryExtractionResult.model_validate({
        "identity": None,
        "spending": {"monthly_grocery": 500},
        "summary": "Just spending.",
    })
    assert result.identity is None
    assert result.spending.monthly_grocery == 500
    assert result.spending.monthly_dining is None
    assert result.preference is None
    assert result.recommendations == []


def test_dump_uses_camel_case_aliases_for_java_wire_format():
    from app.modules.memory.schema import MemoryExtractionResult

    result = MemoryExtractionResult.model_validate({
        "identity": {"user_type": "student", "residency_years": 1},
        "spending": {"monthly_grocery": 400},
        "lifestyle": {"has_children": False},
        "summary": "x",
    })
    wire = result.model_dump(by_alias=True, exclude_none=True)
    assert wire["identity"]["userType"] == "student"
    assert wire["identity"]["residencyYears"] == 1
    assert wire["spending"]["monthlyGrocery"] == 400
    assert wire["lifestyle"]["hasChildren"] is False
    assert "user_type" not in json.dumps(wire)


def test_dump_omits_unset_or_none_optional_fields():
    from app.modules.memory.schema import MemoryExtractionResult

    result = MemoryExtractionResult.model_validate({"summary": "minimal"})
    wire = result.model_dump(by_alias=True, exclude_none=True)
    assert wire == {"summary": "minimal", "recommendations": []}


def test_recommendations_default_to_empty_list_not_none():
    from app.modules.memory.schema import MemoryExtractionResult

    result = MemoryExtractionResult.model_validate({"summary": "x"})
    assert result.recommendations == []

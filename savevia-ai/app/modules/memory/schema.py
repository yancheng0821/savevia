"""Pydantic mirrors of com.savevia.user.dto.MemoryExtractionResultDTO.

Why two name surfaces:
- Inbound LLM JSON uses snake_case (per the extraction prompt).
- Outbound Java request body uses camelCase (Jackson default).

We rely on Pydantic v2 `alias_generator` so a single class handles both.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


def _camel(name: str) -> str:
    """snake_case -> camelCase (Jackson convention)."""
    parts = name.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


class _MemoryModel(BaseModel):
    """Base model: accepts snake_case field names on input, serialises with
    camelCase aliases on output (`model_dump(by_alias=True)`)."""
    model_config = ConfigDict(
        alias_generator=_camel,
        populate_by_name=True,
        extra="ignore",
    )


class IdentityInfo(_MemoryModel):
    user_type: str | None = None
    residency_years: int | None = None
    occupation: str | None = None
    income_range: str | None = None


class SpendingInfo(_MemoryModel):
    monthly_grocery: int | None = None
    monthly_gas: int | None = None
    monthly_dining: int | None = None
    monthly_online: int | None = None
    monthly_travel: int | None = None
    monthly_total: int | None = None


class PreferenceInfo(_MemoryModel):
    annual_fee_tolerance: str | None = None
    reward_type: str | None = None
    preferred_banks: list[str] | None = None
    preferred_networks: list[str] | None = None


class ExclusionInfo(_MemoryModel):
    excluded_banks: list[str] | None = None
    excluded_networks: list[str] | None = None
    excluded_cards: list[str] | None = None


class LifestyleInfo(_MemoryModel):
    travel_frequency: str | None = None
    has_children: bool | None = None
    has_pets: bool | None = None
    commute_method: str | None = None


class RecommendationInfo(_MemoryModel):
    card_name: str | None = None
    card_id: int | None = None
    user_response: str | None = None


class MemoryExtractionResult(_MemoryModel):
    identity: IdentityInfo | None = None
    spending: SpendingInfo | None = None
    preference: PreferenceInfo | None = None
    exclusion: ExclusionInfo | None = None
    lifestyle: LifestyleInfo | None = None
    recommendations: list[RecommendationInfo] = Field(default_factory=list)
    summary: str | None = None

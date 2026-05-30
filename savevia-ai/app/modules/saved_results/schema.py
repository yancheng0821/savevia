"""Saved-results DTOs.

`OptimizationResult` is intentionally permissive — the upstream optimizer
DTO has many shape variations across the app's lifetime; we accept any
dict-shaped payload and only require the three numeric fields the
`saved_results` table indexes on.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.core.types import Money


def _camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


class OptimizationResult(BaseModel):
    """Mirror of Java com.savevia.optimizer.dto.OptimizationResult.

    Loose validation: unrecognised keys pass through into `model_extra`
    (kept by `extra=allow`) so we never reject a payload we receive.
    The frontend will keep evolving; the table just stores the JSON.
    """
    model_config = {
        "alias_generator": _camel,
        "populate_by_name": True,
        "extra": "allow",
    }

    recommendations: list[dict[str, Any]] | None = None
    monthly_reward: Money | None = None
    annual_reward: Money | None = None
    total_annual_fees: Money | None = None
    net_annual_savings: Money | None = None
    summary: str | None = None


class SaveResultRequest(BaseModel):
    """POST /api/v1/optimize/share + /user-result body."""
    result: OptimizationResult = Field(..., description="Optimization result to persist.")


class SaveResultResponse(BaseModel):
    share_id: str = Field(..., alias="shareId")
    share_url: str = Field(..., alias="shareUrl")

    model_config = {"populate_by_name": True}

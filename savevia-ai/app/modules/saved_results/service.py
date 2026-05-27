"""SavedResultService — Python port of
com.savevia.optimizer.service.SavedResultService.

Behaviour parity with Java:
- 8-character share_id from the same alphabet (excludes confusing 0/O/1/l/I).
- For logged-in users, calling share() rewrites the user's existing row with
  a new share_id (single shareable row per user); for anonymous callers,
  always insert a fresh row with a 30-day expiry.
- user-result endpoints store the same JSON payload without a share_id.
"""

from __future__ import annotations

import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.saved_result import SavedResult
from app.modules.saved_results.schema import OptimizationResult, SaveResultResponse
from app.repositories.saved_result_repository import SavedResultRepository

# Java's CHARS verbatim: removes 0/O/1/l/I to keep share IDs unambiguous.
_SHARE_ID_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
_SHARE_ID_LENGTH = 8
_SHARE_TTL_DAYS = 30


def _generate_share_id() -> str:
    return "".join(
        secrets.choice(_SHARE_ID_ALPHABET) for _ in range(_SHARE_ID_LENGTH)
    )


def _result_to_dict(result: OptimizationResult) -> dict[str, Any]:
    """Serialise the validated OptimizationResult back to a Java-shaped dict
    (camelCase, includes the pass-through fields)."""
    return result.model_dump(by_alias=True, exclude_none=False, mode="json")


class SavedResultService:
    def __init__(
        self,
        *,
        session: AsyncSession,
        share_base_url: str,
        repository: SavedResultRepository | None = None,
    ):
        self._session = session
        self._repo = repository if repository is not None else SavedResultRepository(session)
        self._share_base_url = share_base_url.rstrip("/")

    # ---- share endpoints ------------------------------------------------

    async def save_result(
        self, result: OptimizationResult, user_id: int | None
    ) -> SaveResultResponse:
        """POST /api/v1/optimize/share — assigns a share_id with 30-day TTL."""
        share_id = _generate_share_id()

        # Logged-in users reuse their existing row: rewrite its share_id +
        # extend the TTL. Anonymous or first-time users get a fresh row.
        if user_id is not None:
            existing = await self._repo.select_by_user_id_latest(user_id)
            if existing is not None:
                await self._repo.update_share_id(
                    existing.id, share_id, ttl_days=_SHARE_TTL_DAYS,
                )
                await self._session.commit()
                return SaveResultResponse(
                    share_id=share_id,
                    share_url=f"{self._share_base_url}/share/{share_id}",
                )

        # Fresh row (anonymous or first-time logged-in)
        row = SavedResult(
            share_id=share_id,
            user_id=user_id,
            result_json=json.dumps(_result_to_dict(result)),
            net_annual_savings=result.net_annual_savings,
            annual_reward=result.annual_reward,
            total_annual_fees=result.total_annual_fees,
            expires_at=datetime.now(timezone.utc).replace(tzinfo=None)
            + timedelta(days=_SHARE_TTL_DAYS),
        )
        self._session.add(row)
        await self._session.commit()

        return SaveResultResponse(
            share_id=share_id,
            share_url=f"{self._share_base_url}/share/{share_id}",
        )

    async def get_by_share_id(self, share_id: str) -> OptimizationResult | None:
        """GET /api/v1/optimize/share/{shareId} — None if missing/expired."""
        row = await self._repo.select_by_share_id(share_id)
        if row is None:
            return None
        return OptimizationResult.model_validate_json(row.result_json)

    # ---- user-result endpoints -----------------------------------------

    async def save_user_result(
        self, result: OptimizationResult, user_id: int
    ) -> None:
        """POST /api/v1/optimize/user-result — upsert by user_id (no share_id)."""
        result_json = json.dumps(_result_to_dict(result))
        existing = await self._repo.select_by_user_id_latest(user_id)
        if existing is not None:
            await self._repo.update_user_result(
                user_id=user_id,
                result_json=result_json,
                net_annual_savings=result.net_annual_savings,
                annual_reward=result.annual_reward,
                total_annual_fees=result.total_annual_fees,
            )
        else:
            row = SavedResult(
                share_id=None,
                user_id=user_id,
                result_json=result_json,
                net_annual_savings=result.net_annual_savings,
                annual_reward=result.annual_reward,
                total_annual_fees=result.total_annual_fees,
            )
            self._session.add(row)
        await self._session.commit()

    async def get_user_result(
        self, user_id: int
    ) -> OptimizationResult | None:
        """GET /api/v1/optimize/user-result — newest row for the user."""
        row = await self._repo.select_by_user_id_latest(user_id)
        if row is None:
            return None
        return OptimizationResult.model_validate_json(row.result_json)

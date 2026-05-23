"""HTTP client for savevia-card service.

Endpoint map (verified against `CreditCardController`):

    GET  /api/v1/cards                       -> List<CreditCardDTO>      (all cards)
    GET  /api/v1/cards/{id}                  -> CreditCardDTO
    GET  /api/v1/cards/bank/{bank}           -> List<CreditCardDTO>
    POST /api/v1/cards/batch                 body: List<Long> (raw array, NOT wrapped)
                                             -> List<CreditCardDTO>
    GET  /api/v1/cards/{id}/usage-guide?lang -> CardUsageGuideDTO        (singular)

Card endpoints are public (no X-User-Id required).

NOTE: There is no `/search` endpoint in the Java card service. Search must
be composed in Python by combining `list_all_cards()` with local filtering
(planned for Plan 02 tools).
"""
from typing import Any

from app.clients._base import BaseJavaClient


class CardServiceClient(BaseJavaClient):
    service_name = "savevia-card"

    async def list_all_cards(self) -> list[dict[str, Any]]:
        """GET /api/v1/cards — full card catalog."""
        return await self._get("/api/v1/cards")

    async def get_card(self, card_id: int) -> dict[str, Any]:
        """GET /api/v1/cards/{id} — single card by ID."""
        return await self._get(f"/api/v1/cards/{card_id}")

    async def get_cards_by_bank(self, bank: str) -> list[dict[str, Any]]:
        """GET /api/v1/cards/bank/{bank} — all cards from a given bank."""
        return await self._get(f"/api/v1/cards/bank/{bank}")

    async def get_cards_batch(self, card_ids: list[int]) -> list[dict[str, Any]]:
        """POST /api/v1/cards/batch — body is a raw List<Long>, not wrapped."""
        return await self._post("/api/v1/cards/batch", json=card_ids)

    async def get_card_usage_guide(
        self, card_id: int, lang: str = "en"
    ) -> dict[str, Any]:
        """GET /api/v1/cards/{id}/usage-guide — returns a single CardUsageGuideDTO."""
        return await self._get(
            f"/api/v1/cards/{card_id}/usage-guide", params={"lang": lang}
        )

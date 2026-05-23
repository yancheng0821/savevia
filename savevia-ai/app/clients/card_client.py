from typing import Any

from app.clients._base import BaseJavaClient


class CardServiceClient(BaseJavaClient):
    service_name = "savevia-card"

    async def search_cards(
        self,
        query: str | None = None,
        category: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"limit": limit}
        if query:
            params["query"] = query
        if category:
            params["category"] = category
        return await self._get("/api/v1/cards/search", params=params)

    async def get_card(self, card_id: int) -> dict[str, Any]:
        return await self._get(f"/api/v1/cards/{card_id}")

    async def get_cards_batch(self, card_ids: list[int]) -> list[dict[str, Any]]:
        return await self._post("/api/v1/cards/batch", json={"ids": card_ids})

    async def get_card_usage_tips(self, card_id: int) -> list[dict[str, Any]]:
        return await self._get(f"/api/v1/cards/{card_id}/usage-tips")

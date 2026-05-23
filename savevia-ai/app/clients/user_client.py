from typing import Any

from app.clients._base import BaseJavaClient


class UserServiceClient(BaseJavaClient):
    service_name = "savevia-user"

    async def get_user_cards(self, user_id: int) -> list[dict[str, Any]]:
        return await self._get(f"/api/v1/users/{user_id}/cards")

    async def get_user_profile(self, user_id: int) -> dict[str, Any]:
        return await self._get(f"/api/v1/users/{user_id}")

    async def get_user_memory(self, user_id: int) -> list[dict[str, Any]]:
        return await self._get(f"/api/v1/memory/users/{user_id}")

    async def get_chat_history(self, conversation_id: str) -> list[dict[str, Any]]:
        return await self._get(f"/api/v1/chat/conversations/{conversation_id}/messages")

    async def get_ai_usage_limit(self, user_id: int) -> dict[str, Any]:
        return await self._get(f"/api/v1/ai-usage/users/{user_id}")

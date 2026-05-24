"""HTTP client for savevia-user service.

Endpoint map (verified against Java controllers):

    GET  /api/v1/users/me                          UserProfileController       -> UserDTO
    GET  /api/v1/users/me/cards                    UserCardController          -> List<Long>
    GET  /api/v1/users/ai-usage                    AiUsageController           -> AiUsageInfo
    GET  /api/v1/chat/conversations/{id}/messages  ChatController              -> List<ChatMessage>

All four endpoints require the `X-User-Id` header (set by the gateway
from the validated inbound JWT; we send the same header here).

NOTE: There is no MemoryController in Java today. The user-memory feature
is owned by this Python service (`user_memory_facts` table) and exposed
via internal Python endpoints — not by calling Java.
"""

from typing import Any

from app.clients._base import BaseJavaClient


class UserServiceClient(BaseJavaClient):
    service_name = "savevia-user"

    async def get_user_profile(self, user_id: int) -> dict[str, Any]:
        """GET /api/v1/users/me — returns UserDTO."""
        return await self._get("/api/v1/users/me", user_id=user_id)

    async def get_user_card_ids(self, user_id: int) -> list[int]:
        """GET /api/v1/users/me/cards — returns List<Long> (raw card IDs)."""
        return await self._get("/api/v1/users/me/cards", user_id=user_id)

    async def get_ai_usage_limit(self, user_id: int) -> dict[str, Any]:
        """GET /api/v1/users/ai-usage — returns AiUsageInfo {limit, used, remaining, ...}."""
        return await self._get("/api/v1/users/ai-usage", user_id=user_id)

    async def get_chat_history(self, conversation_id: int, user_id: int) -> list[dict[str, Any]]:
        """GET /api/v1/chat/conversations/{id}/messages — returns List<ChatMessage>.

        `conversation_id` is `Long` on the Java side, not a string.
        """
        return await self._get(
            f"/api/v1/chat/conversations/{conversation_id}/messages",
            user_id=user_id,
        )

    async def check_can_use_chat(self, user_id: int) -> bool:
        """GET /api/v1/users/ai-usage/chat/check/{userId} — returns Boolean.

        userId is a path param; X-User-Id is NOT used (matches Java AiUsageController).
        """
        data = await self._get(f"/api/v1/users/ai-usage/chat/check/{user_id}")
        return bool(data)

    async def record_chat_usage(self, user_id: int) -> bool:
        """POST /api/v1/users/ai-usage/chat/record/{userId} — increments chat counter.

        Returns true on success. If the increment tips the user past their monthly
        limit, Java responds HTTP 200 with code=429 — BaseJavaClient raises
        JavaServiceError. Callers MUST catch and log; the chat response already
        streamed to the user.
        """
        data = await self._post(f"/api/v1/users/ai-usage/chat/record/{user_id}")
        return bool(data)

    # ----- chat conversations / messages -----

    async def create_conversation(
        self, user_id: int, title: str = "New Conversation"
    ) -> dict[str, Any]:
        """POST /api/v1/chat/conversations — returns the created ChatConversation.

        Body: {"title": "..."}. Requires X-User-Id.
        """
        return await self._post(
            "/api/v1/chat/conversations",
            user_id=user_id,
            json={"title": title},
        )

    async def get_conversation(self, user_id: int, conversation_id: int) -> dict[str, Any]:
        """GET /api/v1/chat/conversations/{id} — validates ownership.

        Raises JavaServiceError (code=500, "Conversation not found") if the
        conversation doesn't exist or is owned by another user. Callers
        should catch and then fall back to creating a new conversation.
        """
        return await self._get(
            f"/api/v1/chat/conversations/{conversation_id}",
            user_id=user_id,
        )

    async def add_message(
        self, user_id: int, conversation_id: int, role: str, content: str
    ) -> dict[str, Any]:
        """POST /api/v1/chat/conversations/{id}/messages — appends a message.

        Body: {"role": "user"|"assistant", "content": "..."}. Returns the saved
        ChatMessage (with id and createdAt populated by Java).
        """
        return await self._post(
            f"/api/v1/chat/conversations/{conversation_id}/messages",
            user_id=user_id,
            json={"role": role, "content": content},
        )

    async def get_recent_messages(
        self, user_id: int, conversation_id: int, limit: int = 10
    ) -> list[dict[str, Any]]:
        """GET /api/v1/chat/conversations/{id}/messages/recent?limit={limit}.

        Returns the most recent `limit` messages (newest-last). This is the
        AI-context endpoint — distinct from the un-suffixed /messages which
        returns the full history and is used by the conversation list UI.
        """
        return await self._get(
            f"/api/v1/chat/conversations/{conversation_id}/messages/recent",
            user_id=user_id,
            params={"limit": limit},
        )

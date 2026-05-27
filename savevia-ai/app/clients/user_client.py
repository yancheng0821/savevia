"""HTTP client for savevia-user service.

Endpoint map (verified against Java controllers):

    GET  /api/v1/users/me                          UserProfileController       -> UserDTO
    GET  /api/v1/users/me/cards                    UserCardController          -> List<Long>
    GET  /api/v1/users/ai-usage                    AiUsageController           -> AiUsageInfo
    GET  /api/v1/users/ai-usage/chat/check/{id}    AiUsageController           -> Boolean
    POST /api/v1/users/ai-usage/chat/record/{id}   AiUsageController           -> Boolean
    POST /api/v1/chat/conversations                ChatController              -> ChatConversation
    GET  /api/v1/chat/conversations/{id}           ChatController              -> ChatConversation
    POST /api/v1/chat/conversations/{id}/messages  ChatController              -> ChatMessage
    GET  /api/v1/chat/conversations/{id}/messages/recent?limit=N  -> List<ChatMessage>
    GET  /api/v1/chat/conversations/{id}/messages  ChatController              -> List<ChatMessage>
    GET  /api/v1/internal/memory/{id}/context?categories=csv      -> MemoryContextDTO
    POST /api/v1/admin/track                       (admin tracking, on user svc) -> void

Auth pattern: X-User-Id is set for endpoints that key off the calling user
(/users/me, /chat/conversations, /admin/track). Endpoints that take userId
as a PATH parameter (/ai-usage/chat/check/{id}, /internal/memory/{id}/context)
do NOT use X-User-Id. We never forward the raw inbound JWT to internal Java.

Phase-2 note: user-memory READ is on Java (MemoryController). Phase 3 will
port memory extraction to Python and add writeback methods here.
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

    # ----- user memory (read-only in Phase 2; extraction is Phase 3) -----

    async def get_user_memory_context(
        self, user_id: int, categories: list[str] | None = None
    ) -> dict[str, Any]:
        """GET /api/v1/internal/memory/{userId}/context — returns MemoryContextDTO.

        `categories` is an optional list of extended-memory categories to
        include (e.g., ["spending", "lifestyle"]). Joined with commas for the
        query param when present; omitted entirely when None/empty.
        """
        params: dict[str, Any] = {}
        if categories:
            params["categories"] = ",".join(categories)
        return await self._get(
            f"/api/v1/internal/memory/{user_id}/context",
            params=params or None,
        )

    # ----- admin event tracking (fire-and-forget at call sites) -----

    async def track_event(
        self, event_type: str, user_id: int | None = None
    ) -> None:
        """POST /api/v1/admin/track — emits an analytics event.

        Callers should wrap with try/except and never let a tracking failure
        affect user-facing flow. X-User-Id is forwarded when present.
        """
        await self._post(
            "/api/v1/admin/track",
            user_id=user_id,
            json={"eventType": event_type},
        )

    async def post_extracted_memory(
        self,
        *,
        user_id: int,
        conversation_id: int | None,
        extraction: dict[str, Any],
    ) -> None:
        """POST /api/v1/internal/memory/{userId}/extracted — writes back the
        LLM-extracted MemoryExtractionResultDTO. Java handles dedup (upsert
        per fact) + summary row.

        `conversation_id` is forwarded as a query param so Java can stamp the
        extraction log; omit (=None) for one-off / batch extractions.
        """
        params: dict[str, Any] = {}
        if conversation_id is not None:
            params["conversationId"] = conversation_id
        await self._post(
            f"/api/v1/internal/memory/{user_id}/extracted",
            params=params or None,
            json=extraction,
        )

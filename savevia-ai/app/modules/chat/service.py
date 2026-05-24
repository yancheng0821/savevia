"""ChatService — orchestrates the chat turn end-to-end.

Mirrors com.savevia.optimizer.service.ChatService.streamResponse. Returns an
async iterator of pre-serialised SSE frames (strings). The router wraps it in
a StreamingResponse.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

from app.clients._base import JavaServiceError
from app.clients.card_client import CardServiceClient
from app.clients.user_client import UserServiceClient
from app.core.logging import get_logger
from app.modules.agent.context import use_tool_context
from app.modules.agent.graph import (
    DEFAULT_RECURSION_LIMIT,
    FALLBACK_MESSAGE,
)
from app.modules.agent.memory_injection import build_memory_block
from app.modules.agent.prompts import build_agent_system_prompt
from app.modules.chat.sse import (
    format_conversation_event,
    format_done_event,
    format_error_event,
    format_message_event,
    format_tool_call_event,
    format_tool_result_event,
)

_log = get_logger("savevia-ai.chat")

MAX_MESSAGE_LENGTH = 1000
MAX_CONTEXT_MESSAGES = 10


_QUOTA_EXCEEDED_MESSAGE = {
    "en": "Monthly chat limit reached. Your quota will reset next month.",
    "zh": "本月对话次数已用完，下个月将自动重置额度",
    "fr": "Limite de conversation atteinte ce mois-ci. Le quota sera réinitialisé le mois prochain.",
    "es": "Límite de conversación alcanzado este mes. La cuota se restablecerá el próximo mes.",
    "ja": "今月の会話回数が上限に達しました。来月に自動的にリセットされます。",
    "ko": "이번 달 대화 한도에 도달했습니다. 다음 달에 자동으로 초기화됩니다.",
}


def _quota_message(locale: str | None) -> str:
    if not locale:
        return _QUOTA_EXCEEDED_MESSAGE["en"]
    key = locale.lower().split("-", 1)[0]
    return _QUOTA_EXCEEDED_MESSAGE.get(key, _QUOTA_EXCEEDED_MESSAGE["en"])


def _stream_text_from_chunk(chunk: AIMessageChunk) -> str:
    """Extract text from an AIMessageChunk. Content may be a string OR a list
    of content parts (Anthropic-style tool-call mixed content)."""
    if isinstance(chunk.content, str):
        return chunk.content
    if isinstance(chunk.content, list):
        out: list[str] = []
        for part in chunk.content:
            if isinstance(part, dict) and part.get("type") == "text":
                out.append(str(part.get("text", "")))
        return "".join(out)
    return ""


class ChatService:
    def __init__(
        self,
        *,
        user_client: UserServiceClient,
        card_client: CardServiceClient,
        agent: Any,
    ):
        self._user = user_client
        self._card = card_client
        self._agent = agent

    async def stream(
        self,
        *,
        user_id: int,
        message: str,
        locale: str,
        conversation_id: int | None,
    ) -> AsyncIterator[str]:
        try:
            async for frame in self._stream_inner(
                user_id=user_id, message=message, locale=locale,
                conversation_id=conversation_id,
            ):
                yield frame
        except Exception as e:  # noqa: BLE001
            _log.exception("chat_stream_uncaught", error=str(e))
            yield format_error_event(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred",
            )

    async def _stream_inner(
        self,
        *,
        user_id: int,
        message: str,
        locale: str,
        conversation_id: int | None,
    ) -> AsyncIterator[str]:
        # 1. Validate input
        if not message or not message.strip():
            yield format_error_event(code="INVALID_INPUT", message="Message cannot be empty")
            return
        if len(message) > MAX_MESSAGE_LENGTH:
            yield format_error_event(
                code="MESSAGE_TOO_LONG",
                message=f"Message exceeds maximum length of {MAX_MESSAGE_LENGTH} characters",
            )
            return

        # 2. Quota check (chat-specific)
        try:
            allowed = await self._user.check_can_use_chat(user_id=user_id)
        except JavaServiceError as e:
            _log.warning("quota_check_failed", user_id=user_id, error=e.message)
            allowed = True  # match Java: failure to check ≠ failure to serve
        if not allowed:
            yield format_error_event(
                code="CHAT_QUOTA_EXCEEDED",
                message=_quota_message(locale),
            )
            return

        # 3. Conversation lifecycle
        conv_id = conversation_id
        if conv_id is not None:
            try:
                await self._user.get_conversation(user_id=user_id, conversation_id=conv_id)
            except JavaServiceError as e:
                _log.warning(
                    "conversation_validation_failed", conversation_id=conv_id, error=e.message,
                )
                conv_id = None
        if conv_id is None:
            try:
                created = await self._user.create_conversation(
                    user_id=user_id, title="New Conversation",
                )
            except JavaServiceError as e:
                _log.error("conversation_create_failed", user_id=user_id, error=e.message)
                yield format_error_event(
                    code="CONVERSATION_ERROR",
                    message="Failed to create conversation",
                )
                return
            conv_id = created["id"]
            yield format_conversation_event(conv_id)

        # 4. Save user message
        try:
            await self._user.add_message(
                user_id=user_id, conversation_id=conv_id, role="user", content=message,
            )
        except JavaServiceError as e:
            _log.warning("save_user_message_failed", error=e.message)

        # 5. Build context (cards + history + memory + system prompt)
        user_cards = await self._fetch_user_cards(user_id)
        recent = await self._fetch_recent_messages(user_id, conv_id)
        memory_block = await build_memory_block(
            user_client=self._user, user_id=user_id, user_message=message,
        )
        system_prompt = build_agent_system_prompt(
            user_cards=user_cards, memory_context=memory_block, locale=locale,
        )

        # 6. Stream the agent
        messages: list[BaseMessage] = [SystemMessage(content=system_prompt)]
        for m in recent:
            content = m.get("content") or ""
            if m.get("role") == "user" and content == message:
                continue
            role = m.get("role")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
        messages.append(HumanMessage(content=message))

        full_response: list[str] = []
        with use_tool_context(
            user_id=user_id, locale=locale,
            user_client=self._user, card_client=self._card,
        ):
            try:
                async for event in self._agent.astream_events(
                    {"messages": messages},
                    version="v2",
                    config={"recursion_limit": DEFAULT_RECURSION_LIMIT},
                ):
                    name = event.get("event")
                    if name == "on_chat_model_stream":
                        chunk = event.get("data", {}).get("chunk")
                        if chunk is None:
                            continue
                        text = _stream_text_from_chunk(chunk)
                        if text:
                            full_response.append(text)
                            yield format_message_event(text)
                    elif name == "on_tool_start":
                        tool_name = event.get("name", "")
                        args = event.get("data", {}).get("input") or {}
                        yield format_tool_call_event(name=tool_name, args=args)
                    elif name == "on_tool_end":
                        tool_name = event.get("name", "")
                        output = event.get("data", {}).get("output")
                        if isinstance(output, dict):
                            success = bool(output.get("success", True))
                            content = str(output.get("content", ""))
                            data = output.get("data")
                        else:
                            success = True
                            content = str(output) if output is not None else ""
                            data = None
                        yield format_tool_result_event(
                            name=tool_name, success=success, content=content, data=data,
                        )
            except Exception as e:  # noqa: BLE001
                _log.exception("agent_invocation_failed", error=str(e))
                yield format_error_event(code="INTERNAL_ERROR", message="Agent failed")
                return

        full_text = "".join(full_response)

        # 7a. Fallback if the agent produced nothing
        if not full_text:
            yield format_message_event(FALLBACK_MESSAGE)
            full_text = FALLBACK_MESSAGE

        # 7b. Save assistant message
        try:
            await self._user.add_message(
                user_id=user_id, conversation_id=conv_id,
                role="assistant", content=full_text,
            )
        except JavaServiceError as e:
            _log.warning("save_assistant_message_failed", error=e.message)

        # 7c. Record chat usage (post-hoc 429 must not surface)
        try:
            await self._user.record_chat_usage(user_id=user_id)
        except JavaServiceError as e:
            _log.warning("record_chat_usage_failed", error=e.message)

        # 7d. Fire-and-forget analytics
        asyncio.create_task(self._fire_track_event(user_id))

        # 8. Done
        yield format_done_event()

    # ---- helpers --------------------------------------------------------

    async def _fetch_user_cards(self, user_id: int) -> list[dict[str, Any]]:
        try:
            ids = await self._user.get_user_card_ids(user_id=user_id)
            if not ids:
                return []
            return await self._card.get_cards_batch(ids)
        except JavaServiceError as e:
            _log.warning("fetch_user_cards_failed", error=e.message)
            return []

    async def _fetch_recent_messages(
        self, user_id: int, conversation_id: int
    ) -> list[dict[str, Any]]:
        try:
            return await self._user.get_recent_messages(
                user_id=user_id, conversation_id=conversation_id,
                limit=MAX_CONTEXT_MESSAGES,
            )
        except JavaServiceError as e:
            _log.warning("fetch_recent_messages_failed", error=e.message)
            return []

    async def _fire_track_event(self, user_id: int) -> None:
        try:
            await self._user.track_event(event_type="ai_chat", user_id=user_id)
        except Exception as e:  # noqa: BLE001
            _log.debug("track_event_failed", error=str(e))

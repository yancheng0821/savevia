"""Memory extraction orchestration.

Glues the chain output to UserServiceClient writeback. Designed for
fire-and-forget invocation (`asyncio.create_task`) — every error path
logs and returns; nothing is re-raised.

Mirrors com.savevia.user.service.MemoryExtractionService.extractMemoryFromConversation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.core.logging import get_logger

if TYPE_CHECKING:
    from langchain_core.runnables import Runnable

    from app.clients.user_client import UserServiceClient

_log = get_logger("savevia-ai.memory_extraction")

MIN_MESSAGES_FOR_EXTRACTION = 4


def _build_conversation_text(messages: list[dict[str, Any]]) -> str:
    """`User: <content>\\n\\nAssistant: <content>\\n\\n` — matches Java's format."""
    parts: list[str] = []
    for m in messages:
        role = m.get("role")
        label = "User" if role == "user" else "Assistant"
        parts.append(f"{label}: {m.get('content', '')}\n")
    return "\n".join(parts)


class ExtractionService:
    def __init__(
        self,
        *,
        user_client: "UserServiceClient",
        chain: "Runnable",
    ):
        self._user = user_client
        self._chain = chain

    async def extract_and_save(
        self,
        *,
        user_id: int,
        conversation_id: int | None,
        messages: list[dict[str, Any]],
    ) -> None:
        """Run extraction + writeback. Best-effort: all errors are logged."""
        if len(messages) < MIN_MESSAGES_FOR_EXTRACTION:
            _log.debug(
                "extraction_skipped_too_few_messages",
                conversation_id=conversation_id, count=len(messages),
            )
            return

        conversation = _build_conversation_text(messages)
        try:
            result = await self._chain.ainvoke({"conversation": conversation})
        except Exception as e:  # noqa: BLE001 — best-effort
            _log.warning(
                "extraction_chain_failed",
                conversation_id=conversation_id, error=str(e),
            )
            return

        payload = result.model_dump(by_alias=True, exclude_none=True)
        try:
            await self._user.post_extracted_memory(
                user_id=user_id,
                conversation_id=conversation_id,
                extraction=payload,
            )
            _log.info(
                "memory_extraction_saved",
                user_id=user_id, conversation_id=conversation_id,
            )
        except Exception as e:  # noqa: BLE001 — best-effort
            _log.warning(
                "extraction_writeback_failed",
                conversation_id=conversation_id, error=str(e),
            )

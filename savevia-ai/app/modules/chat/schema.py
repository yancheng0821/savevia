"""Chat module DTOs (request/response shapes)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message text.")
    conversation_id: int | None = Field(
        None, alias="conversationId",
        description="Existing conversation ID, or omit for a new one.",
    )
    locale: str = Field("en", description="User locale, e.g. 'en', 'zh-CN'.")

    model_config = {"populate_by_name": True}


class SuggestionsResponse(BaseModel):
    """Wrapper to match Java's Result<List<String>> envelope shape."""
    code: int = 200
    message: str = "success"
    data: list[str]


ChatErrorCode = Literal[
    "INVALID_INPUT",
    "MESSAGE_TOO_LONG",
    "CHAT_QUOTA_EXCEEDED",
    "CONVERSATION_ERROR",
    "INTERNAL_ERROR",
]

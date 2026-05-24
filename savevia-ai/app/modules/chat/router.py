"""Chat HTTP router — POST /api/v1/chat/stream + GET /api/v1/chat/suggestions.

The router is built with a `get_service` factory so tests can inject a fake
ChatService without touching app.state.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from fastapi import APIRouter, Body, HTTPException, Header, Query
from fastapi.responses import StreamingResponse

from app.modules.chat.schema import ChatRequest, SuggestionsResponse
from app.modules.chat.suggestions import get_suggestions

if TYPE_CHECKING:
    from app.modules.chat.service import ChatService

SSE_CACHE_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",  # disable nginx buffering for SSE
}


def build_chat_router(
    get_service: "Callable[[], ChatService]",
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

    @router.post("/stream")
    async def stream_chat(
        x_user_id: str | None = Header(default=None, alias="X-User-Id"),
        body: ChatRequest = Body(...),
    ) -> StreamingResponse:
        if not x_user_id:
            raise HTTPException(status_code=401, detail="missing X-User-Id")
        try:
            user_id = int(x_user_id)
        except ValueError as e:
            raise HTTPException(status_code=401, detail="invalid X-User-Id") from e

        service = get_service()
        iterator = service.stream(
            user_id=user_id,
            message=body.message,
            locale=body.locale,
            conversation_id=body.conversation_id,
        )
        return StreamingResponse(
            iterator,
            media_type="text/event-stream",
            headers=SSE_CACHE_HEADERS,
        )

    @router.get("/suggestions", response_model=SuggestionsResponse)
    async def suggestions(
        locale: str = Query(default="en"),
    ) -> SuggestionsResponse:
        return SuggestionsResponse(data=get_suggestions(locale))

    return router

"""Per-request tool context — ContextVar-based, async-safe.

LangChain @tool functions only see LLM-supplied parameters. Anything else
(user_id, locale, the Java service clients) is plumbed through this module.

Usage from ChatService:

    with use_tool_context(
        user_id=..., locale=..., user_client=..., card_client=...,
    ):
        async for ev in agent.astream_events(...):
            ...

Usage inside a tool:

    ctx = get_tool_context()
    cards = await ctx.user_client.get_user_card_ids(ctx.user_id)
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from app.clients.card_client import CardServiceClient
    from app.clients.user_client import UserServiceClient


@dataclass(frozen=True)
class ToolContext:
    user_id: int
    locale: str
    user_client: "UserServiceClient"
    card_client: "CardServiceClient"


_tool_context_var: ContextVar[ToolContext] = ContextVar("savevia_ai_tool_context")


def get_tool_context() -> ToolContext:
    """Return the current request's ToolContext. Raises LookupError outside a request."""
    return _tool_context_var.get()


@contextmanager
def use_tool_context(
    *,
    user_id: int,
    locale: str,
    user_client: "UserServiceClient",
    card_client: "CardServiceClient",
) -> Iterator[ToolContext]:
    """Bind a ToolContext for the duration of the with-block.

    Safe for use inside `async def` — ContextVars are copied per-task by asyncio,
    so concurrent requests do not see each other's context.
    """
    ctx = ToolContext(
        user_id=user_id, locale=locale,
        user_client=user_client, card_client=card_client,
    )
    token = _tool_context_var.set(ctx)
    try:
        yield ctx
    finally:
        _tool_context_var.reset(token)

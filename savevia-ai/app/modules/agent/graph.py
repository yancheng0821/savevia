"""LangGraph ReAct agent assembly.

The agent runs ONE turn per request (no checkpointer). History comes from
Java at the start of each turn and is passed in via the `messages` list.

The same compiled agent is reused across all requests — only the input
messages, the per-request tool context (ContextVar), and the recursion
limit are per-invocation.
"""

from __future__ import annotations

from typing import Any

import httpx
from langchain_openai import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent

from app.core.config import get_settings
from app.modules.tools import TOOLS

MAX_ITERATIONS = 5
# LangGraph counts each LLM call AND each tool round-trip as a step, so we
# double our Java MAX_ITERATIONS budget.
DEFAULT_RECURSION_LIMIT = MAX_ITERATIONS * 2

FALLBACK_MESSAGE = (
    "I apologize, but I couldn't complete the request. Please try again."
)


def build_chat_model() -> ChatOpenAI:
    """Construct the streaming ChatOpenAI used by the agent.

    httpx clients are explicitly constructed with `trust_env=False` so the
    OpenAI SDK ignores shell HTTP(S)_PROXY/ALL_PROXY env vars (matches what
    BaseJavaClient does for outbound Java calls). Production traffic goes
    direct to OpenAI; developer proxies should not affect either path.
    """
    settings = get_settings()
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        base_url=f"{settings.openai_base_url.rstrip('/')}/v1",
        temperature=0.7,
        max_tokens=1000,
        streaming=True,
        http_client=httpx.Client(trust_env=False),
        http_async_client=httpx.AsyncClient(trust_env=False),
    )


def build_agent(*, model: Any | None = None) -> CompiledStateGraph:
    """Build the compiled LangGraph agent once at app startup."""
    if model is None:
        model = build_chat_model()
    return create_react_agent(model=model, tools=TOOLS)

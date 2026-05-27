"""LangChain extraction chain — turns a conversation string into a typed
MemoryExtractionResult.

The chain is intentionally tiny:
    prompt | model | (validate JSON into Pydantic)

We do NOT use PydanticOutputParser because OpenAI JSON-mode already
guarantees parseable JSON; an extra structured-output layer would only
duplicate the parsing.
"""

from __future__ import annotations

from typing import Any

import httpx
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI

from app.core.config import get_settings
from app.modules.memory.prompts import EXTRACTION_SYSTEM_PROMPT
from app.modules.memory.schema import MemoryExtractionResult


def build_extraction_model() -> ChatOpenAI:
    """Construct the (non-streaming) ChatOpenAI used for extraction.

    JSON mode is the linchpin — OpenAI guarantees the response is parseable JSON
    when `response_format={"type": "json_object"}` is set AND the prompt asks
    for JSON output (the extraction prompt does).
    """
    settings = get_settings()
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        base_url=f"{settings.openai_base_url.rstrip('/')}/v1",
        temperature=0.3,
        max_tokens=1500,
        streaming=False,
        model_kwargs={"response_format": {"type": "json_object"}},
        http_client=httpx.Client(trust_env=False),
        http_async_client=httpx.AsyncClient(trust_env=False),
    )


def _prompt() -> ChatPromptTemplate:
    """System + user template. We pass the conversation as a single user msg
    matching the Java implementation (`CONVERSATION:\\n<content>`).

    The system half is a literal SystemMessage (not a template string) because
    the extraction prompt embeds JSON braces — LangChain's f-string parser
    would otherwise try to interpret them as placeholders.
    """
    return ChatPromptTemplate.from_messages([
        SystemMessage(content=EXTRACTION_SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template("CONVERSATION:\n{conversation}"),
    ])


def _parse(message: AIMessage) -> MemoryExtractionResult:
    """Validate the LLM's JSON string into a typed result."""
    content = message.content if isinstance(message.content, str) else ""
    return MemoryExtractionResult.model_validate_json(content)


def build_extraction_chain(*, model: Any | None = None) -> Runnable:
    """Build the prompt|model|parse runnable.

    Pass `model=` to inject a stub during tests; defaults to the production
    ChatOpenAI configured by build_extraction_model().
    """
    chat = model if model is not None else build_extraction_model()
    return _prompt() | chat | _parse

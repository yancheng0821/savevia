"""Tests for the LangChain extraction chain."""

import pytest


def _stub_model(canned_content: str):
    """Build a Runnable stub that records its input and returns a canned
    AIMessage. We use RunnableLambda over AsyncMock because the chain's
    `prompt | model | parse` composition coerces non-Runnable objects via
    RunnableLambda — which sync-calls the underlying object — so AsyncMock
    would resolve to a MagicMock, not the canned message.
    """
    from langchain_core.messages import AIMessage
    from langchain_core.runnables import RunnableLambda

    captured: dict = {"input": None}

    def _call(prompt_value):
        captured["input"] = prompt_value
        return AIMessage(content=canned_content)

    return RunnableLambda(_call), captured


def test_build_extraction_model_uses_json_mode_and_low_temperature(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    from app.core.config import reset_settings_cache
    reset_settings_cache()

    from app.modules.memory.extraction_chain import build_extraction_model

    model = build_extraction_model()
    assert getattr(model, "temperature", None) == 0.3
    assert getattr(model, "max_tokens", None) == 1500
    kwargs = getattr(model, "model_kwargs", {}) or {}
    assert kwargs.get("response_format") == {"type": "json_object"}


async def test_chain_returns_parsed_extraction_result():
    from app.modules.memory.extraction_chain import build_extraction_chain
    from app.modules.memory.schema import MemoryExtractionResult

    stub, _ = _stub_model(
        '{"identity": {"user_type": "student"}, '
        '"spending": {"monthly_grocery": 400}, '
        '"summary": "Student, $400/mo grocery."}'
    )
    chain = build_extraction_chain(model=stub)
    result = await chain.ainvoke({"conversation": "User: hi\n\nAssistant: hello"})

    assert isinstance(result, MemoryExtractionResult)
    assert result.identity.user_type == "student"
    assert result.spending.monthly_grocery == 400


async def test_chain_passes_conversation_into_user_message():
    from app.modules.memory.extraction_chain import build_extraction_chain

    stub, captured = _stub_model('{"summary": "x"}')
    chain = build_extraction_chain(model=stub)
    await chain.ainvoke({"conversation": "PAYLOAD_MARKER"})

    prompt_value = captured["input"]
    msgs = prompt_value.to_messages()
    assert any("memory extraction assistant" in m.content for m in msgs)
    assert any("PAYLOAD_MARKER" in m.content for m in msgs)


async def test_chain_raises_when_llm_returns_non_json():
    from pydantic import ValidationError

    from app.modules.memory.extraction_chain import build_extraction_chain

    stub, _ = _stub_model("not json at all")
    chain = build_extraction_chain(model=stub)
    with pytest.raises((ValueError, ValidationError)):
        await chain.ainvoke({"conversation": "x"})

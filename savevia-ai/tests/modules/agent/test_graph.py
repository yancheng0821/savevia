"""Tests for the LangGraph ReAct agent assembly."""

import pytest


def test_build_agent_uses_tools_barrel():
    import httpx
    from langchain_openai import ChatOpenAI
    from langgraph.graph.state import CompiledStateGraph

    from app.modules.agent.graph import build_agent
    from app.modules.tools import TOOLS

    # Construct a ChatOpenAI without making any network calls. trust_env=False
    # avoids the dev's SOCKS proxy (also see build_chat_model's docstring).
    agent = build_agent(model=ChatOpenAI(
        api_key="sk-fake",
        model="gpt-4o-mini",
        http_client=httpx.Client(trust_env=False),
        http_async_client=httpx.AsyncClient(trust_env=False),
    ))
    assert isinstance(agent, CompiledStateGraph)
    node_names = set(agent.get_graph().nodes.keys())
    assert "tools" in node_names
    assert "agent" in node_names
    assert len(TOOLS) == 6


def test_default_recursion_limit_is_ten():
    from app.modules.agent.graph import DEFAULT_RECURSION_LIMIT, MAX_ITERATIONS
    assert MAX_ITERATIONS == 5
    assert DEFAULT_RECURSION_LIMIT == MAX_ITERATIONS * 2


def test_build_model_uses_openai_settings(monkeypatch):
    from app.modules.agent.graph import build_chat_model

    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    from app.core.config import reset_settings_cache
    reset_settings_cache()

    model = build_chat_model()
    model_name = getattr(model, "model_name", None) or getattr(model, "model", None)
    assert model_name == "gpt-4o-mini"
    assert getattr(model, "streaming", None) is True
    assert getattr(model, "temperature", None) == 0.7
    assert getattr(model, "max_tokens", None) == 1000

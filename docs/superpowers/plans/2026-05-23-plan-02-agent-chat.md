# savevia-ai Agent + Chat — Implementation Plan (Phase 2)

> **Status:** SKELETON. File-level breakdown is complete; step-level code will be filled in when Phase 2 begins, after Phase 1 (foundation) is merged. Writing detailed steps too early invites rework — early-phase decisions inevitably shape later ones.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to execute. Re-run writing-plans skill on this file to expand each task into full TDD steps once Phase 1 is done.

**Goal:** Implement the LangGraph ReAct agent with all 6 tools, SSE chat streaming endpoint, and full ChatService logic — replacing Java's `ChatStreamController`, `AgentExecutor`, `ToolRegistry`, `LlmService`, `OpenAiService`, and `ChatService`. After this plan, `POST /api/v1/chat/stream` works end-to-end and is functionally equivalent to the Java endpoint (same SSE event format, same tool behavior).

**Architecture:** Single LangGraph `create_react_agent` instance per app (built at startup). Tools are LangChain `@tool` decorated functions that internally call `UserServiceClient` / `CardServiceClient` (from Phase 1). Conversation history fetched from Java user service via HTTP at chat start; LangGraph `MemorySaver` checkpoint stores intra-conversation state in Redis. SSE streams via FastAPI `StreamingResponse` + `astream_events(v2)`, with event format **bit-identical** to current Java output.

**Tech Stack:** LangGraph 0.2+, langchain-openai, langchain-core, plus everything from Phase 1.

**Reference spec:** `docs/superpowers/specs/2026-05-23-python-rewrite-design.md` §6

**Estimated effort:** 14 person-days (2 weeks solo).

**Reference Java code (read before each task):**
- `savevia-optimizer/src/main/java/com/savevia/optimizer/agent/AgentExecutor.java`
- `savevia-optimizer/src/main/java/com/savevia/optimizer/agent/tools/*.java`
- `savevia-optimizer/src/main/java/com/savevia/optimizer/service/ChatService.java`
- `savevia-optimizer/src/main/java/com/savevia/optimizer/service/LlmService.java`
- `savevia-optimizer/src/main/java/com/savevia/optimizer/service/MemoryInjectionStrategy.java`
- `savevia-optimizer/src/main/java/com/savevia/optimizer/controller/ChatStreamController.java`

---

## File Structure (additions over Phase 1)

```
savevia-ai/app/
├── modules/
│   ├── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py                  # LangGraph create_react_agent setup
│   │   ├── state.py                  # AgentState TypedDict
│   │   ├── memory_injection.py       # state_modifier for long-term memory
│   │   └── checkpoint.py             # Redis-backed checkpointer
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── _common.py                # shared context for tools (user_id, JWT)
│   │   ├── get_user_cards.py
│   │   ├── search_cards.py
│   │   ├── get_best_card.py
│   │   ├── compare_cards.py
│   │   ├── calculate_reward.py
│   │   └── get_card_usage_guide.py
│   ├── optimizer/
│   │   ├── __init__.py
│   │   └── cashback_calculator.py    # local cashback math (mirrors Java CashbackCalculator)
│   └── chat/
│       ├── __init__.py
│       ├── router.py                  # POST /api/v1/chat/stream, /suggestions
│       ├── service.py                 # ChatService logic
│       ├── schema.py                  # ChatRequest, ChatResponse, SSE event types
│       ├── sse.py                     # SSE event serialization (matches Java format)
│       └── prompts.py                 # system prompts (verbatim copy from Java)
└── tests/
    ├── modules/
    │   ├── agent/
    │   │   ├── test_graph.py
    │   │   ├── test_memory_injection.py
    │   │   └── test_checkpoint.py
    │   ├── tools/
    │   │   ├── test_get_user_cards.py
    │   │   ├── test_search_cards.py
    │   │   ├── test_get_best_card.py
    │   │   ├── test_compare_cards.py
    │   │   ├── test_calculate_reward.py
    │   │   └── test_get_card_usage_guide.py
    │   ├── optimizer/
    │   │   └── test_cashback_calculator.py
    │   └── chat/
    │       ├── test_router.py
    │       ├── test_service.py
    │       └── test_sse.py
    └── fixtures/
        └── sse_replay/                # recorded SSE streams from prod Java for diff
```

---

## Task List

| # | Task | Files (new/modified) | Days |
|---|---|---|---|
| 1 | Add LangGraph + langchain dependencies | `pyproject.toml` | 0.5 |
| 2 | Implement `CashbackCalculator` (local algorithm) | `modules/optimizer/cashback_calculator.py` + test | 1 |
| 3 | Tool context plumbing (per-request user_id + JWT) | `modules/tools/_common.py` + test | 0.5 |
| 4 | Tool: `get_user_cards` | `modules/tools/get_user_cards.py` + test | 0.5 |
| 5 | Tool: `search_cards` | `modules/tools/search_cards.py` + test | 0.5 |
| 6 | Tool: `get_best_card` | `modules/tools/get_best_card.py` + test | 1 |
| 7 | Tool: `compare_cards` | `modules/tools/compare_cards.py` + test | 0.5 |
| 8 | Tool: `calculate_reward` | `modules/tools/calculate_reward.py` + test | 0.5 |
| 9 | Tool: `get_card_usage_guide` | `modules/tools/get_card_usage_guide.py` + test | 0.5 |
| 10 | System prompts: verbatim copy from Java | `modules/chat/prompts.py` | 0.5 |
| 11 | Memory injection state_modifier | `modules/agent/memory_injection.py` + test | 1 |
| 12 | Redis-backed LangGraph checkpointer | `modules/agent/checkpoint.py` + test | 1 |
| 13 | Assemble LangGraph agent (create_react_agent + tools + checkpoint + state_modifier) | `modules/agent/graph.py` + test | 1 |
| 14 | SSE event serialization (matches Java format) | `modules/chat/sse.py` + test | 1.5 |
| 15 | ChatService: history fetch + rate-limit check + invocation | `modules/chat/service.py` + test | 1.5 |
| 16 | Chat router: SSE endpoint, suggestions endpoint | `modules/chat/router.py` + test | 1 |
| 17 | Wire chat router into FastAPI app + integration smoke test | `app/main.py`, `tests/modules/chat/test_integration.py` | 1 |
| 18 | SSE diff regression suite: record from Java, replay against Python | `tests/fixtures/sse_replay/`, `tests/test_sse_diff.py` | 1.5 |
| | **Subtotal** | | **14** |

---

## Key Design Decisions to Confirm Before Writing Step-Level Detail

When Phase 2 begins (after Phase 1 merges), revisit these:

1. **LangGraph version**: pin to a specific minor version (e.g., 0.2.x). LangGraph API surface still moves; lock to a tested version.
2. **Checkpoint key naming in Redis**: namespace as `langgraph:checkpoint:{conversation_id}` to avoid collision with existing Java Redis keys.
3. **Tool error contract**: when a tool's HTTP call to Java fails, does the tool return a structured error message to the LLM (preferred) or raise (abort the turn)? Java current behavior dictates choice.
4. **Streaming chunk boundary**: confirm whether Java currently emits per-token deltas or per-word/sentence. Match exactly.
5. **Suggestions endpoint behavior**: Java has `/api/v1/chat/suggestions` — review what it returns (canned prompts? LLM-generated? both?) before implementing.
6. **AI usage limit enforcement**: ChatService increments usage counters. Where does that live — in Python (via HTTP write back to Java) or in a Gateway filter? Decide before Task 15.

---

## Definition of Done

- All 6 tools work, with TDD coverage that mocks Java service responses
- LangGraph agent invokes correctly end-to-end (mocked LLM)
- `POST /api/v1/chat/stream` returns SSE events identical to Java for at least 10 recorded test prompts
- `POST /api/v1/chat/suggestions` matches Java behavior
- Memory injection works (state_modifier reads from user service, injects into prompt)
- All Phase 2 unit tests pass; Phase 1 tests still pass
- Tag `savevia-ai-phase-2` on completion

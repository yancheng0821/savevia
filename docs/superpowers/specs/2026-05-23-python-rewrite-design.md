# SaveVia — Extract AI Service to Python (Design Spec)

- **Date**: 2026-05-23
- **Author**: 颜成 (with Claude brainstorming session)
- **Status**: Approved (pending implementation plan)
- **Scope**: Replace `savevia-optimizer` (Java/Spring Boot, 6,926 LOC) with a new `savevia-ai` (Python/FastAPI/LangGraph). All other Java services (user / card / gateway / common / eureka) remain unchanged.

> **History note**: An earlier version of this spec proposed a full rewrite of all 6 Java services into 2 Python services. That scope was reconsidered — the rewrite cost (~100 days) was not justified given that Auth / Push / Admin / User / Card code is stable, tested, and not on the AI critical path. This revised spec narrows scope to just the AI service, where Python ecosystem advantages (LangGraph, LangChain, future RAG) deliver concrete value.

---

## 1. Motivation

The AI agent in `savevia-optimizer` is the highest-iteration component of the backend, and the agent infrastructure is the largest in-house Java code (1,738 LOC of custom `AgentExecutor`/`ToolRegistry`/tool plumbing). Python ecosystem offers:

- **LangGraph** as a battle-tested ReAct agent framework — replaces ~1,700 LOC of custom Java with ~300 LOC of declarative graph
- **LangChain ecosystem** — checkpoints, memory savers, future RAG (vector stores, retrievers) all off-the-shelf
- **Faster iteration** on prompts, tools, model routing, multi-agent topologies
- **Better LLM SDKs** — openai/anthropic Python SDKs are reference implementations; Java equivalents lag

Other Java services (Auth, Push, Admin, User, Card) work fine, are tested in production, and rewriting them carries high risk (Apple Sign-In, ScheduledPush, JWT compatibility) with near-zero upside.

**Decision**: extract only the AI/optimizer service. Keep Java for everything else. Gateway routes traffic between Java and Python services.

---

## 2. Target Architecture

```
                    ┌─────────────────┐
                    │   savevia-web   │ React + Capacitor (unchanged)
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ savevia-gateway │ Spring Cloud Gateway (Java, unchanged)
                    │   (port 8080)   │ JWT auth + rate limit + route splitting
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────────────┐
              │              │                      │
        lb:// (Eureka)   lb:// (Eureka)        http:// (direct URL)
              │              │                      │
     ┌────────▼─────┐ ┌─────▼──────┐    ┌─────────▼─────────┐
     │ savevia-user │ │savevia-card│    │   savevia-ai      │ ← NEW
     │ (Java)       │ │ (Java)     │    │ Python/FastAPI    │
     │  port 8081   │ │ port 8082  │    │ LangGraph         │
     │              │ │            │    │  port 8002        │
     └──────▲───────┘ └─────▲──────┘    └──────┬────────────┘
            │                │                  │
            │ httpx (async) + JWT pass-through  │
            └────────────────┴──────────────────┘

            ┌──────────────┐
            │savevia-eureka│ (Java, unchanged — only Java services register)
            │ port 8761    │
            └──────────────┘

            MySQL 8 (shared RDS, schema unchanged)
            Redis 7 (shared ElastiCache, key prefixes unchanged)
```

### What Changes

| Service | Status |
|---|---|
| savevia-web | Unchanged |
| savevia-gateway | **Add 4 routes** to point AI paths at Python service |
| savevia-eureka | Unchanged (only Java services register) |
| savevia-user | Unchanged |
| savevia-card | Unchanged |
| savevia-common | Unchanged (Java common only; Python has its own minimal common) |
| savevia-optimizer | **Decommissioned** after cutover (kept running 7 days as rollback option) |
| savevia-ai | **NEW** — Python/FastAPI replacement for savevia-optimizer |

### Service Discovery

- **Java ↔ Java**: continue using Eureka (`lb://service-name`) — no change
- **Java → Python**: Spring Cloud Gateway uses direct URI (`http://savevia-ai:8002`) — Python does **not** register with Eureka
- **Python → Java**: httpx calls direct URL (`http://savevia-user:8081`, `http://savevia-card:8082`) — Python is **not** a Eureka client
- **Python → Python**: N/A (only one Python service)

Reason for Python avoiding Eureka: `py-eureka-client` is poorly maintained; current Java service instances are statically-deployed; future K8s `Service` resource is the natural successor. Eureka stays alive for the existing Java services only.

---

## 3. Tech Stack (Python service only)

| Layer | Choice |
|---|---|
| Language | Python 3.12 |
| Web framework | FastAPI + uvicorn (dev) / gunicorn+uvicorn workers (prod) |
| Validation / DTO | Pydantic v2 |
| ORM | SQLAlchemy 2.0 async + Alembic |
| MySQL driver | aiomysql |
| Redis | redis-py (async) |
| AI Agent | **LangGraph** (`create_react_agent` prebuilt) |
| LLM SDK | openai (primary), anthropic (future option) |
| Streaming | FastAPI `StreamingResponse` (SSE) |
| HTTP client (→ Java services) | httpx (async) |
| Auth (JWT decode for inbound) | PyJWT (HS256, same secret as Java) |
| Test | pytest + pytest-asyncio + httpx.AsyncClient + testcontainers |
| Dependency mgmt | uv |
| Deployment | Docker (same EC2 host) + Docker Compose |
| Logging | structlog |

No OAuth libraries (Apple/Google) — that stays in Java user service.
No push libraries (aioapns / firebase-admin) — that stays in Java user service.
No scheduling — that stays in Java user service.

---

## 4. Repository Structure

```
savevia/                            # existing repo
├── savevia-* (Java)                # 5 services unchanged
├── savevia-optimizer (Java)        # kept running until cutover + 7 days, then deleted
├── savevia-web/                    # unchanged
├── docker/mysql/init/              # SQL migrations preserved
├── docker-compose.yml              # add savevia-ai service entry
├── docs/superpowers/specs/         # this spec
└── savevia-ai/                     # NEW — Python service only
    ├── pyproject.toml              # uv project
    ├── alembic/                    # for FUTURE schema changes only
    ├── alembic.ini
    ├── app/
    │   ├── main.py                 # FastAPI app factory
    │   ├── core/
    │   │   ├── config.py           # pydantic-settings
    │   │   ├── db.py               # SQLAlchemy async engine + session
    │   │   ├── redis.py            # async redis client
    │   │   ├── security.py         # JWT decode
    │   │   └── logging.py
    │   ├── clients/                # HTTP clients to Java services
    │   │   ├── user_client.py      # → savevia-user
    │   │   └── card_client.py      # → savevia-card
    │   ├── modules/
    │   │   ├── chat/               # SSE endpoint, conversation flow
    │   │   │   ├── router.py
    │   │   │   ├── service.py
    │   │   │   └── schema.py
    │   │   ├── agent/              # LangGraph graph definition
    │   │   │   ├── graph.py
    │   │   │   ├── state.py
    │   │   │   └── memory_injection.py
    │   │   ├── tools/              # 6 LangChain @tool functions
    │   │   │   ├── get_user_cards.py
    │   │   │   ├── search_cards.py
    │   │   │   ├── get_best_card.py
    │   │   │   ├── compare_cards.py
    │   │   │   ├── calculate_reward.py
    │   │   │   └── get_card_usage_guide.py
    │   │   ├── memory/             # MemoryExtraction async chain
    │   │   ├── flinks/             # bank connection HTTP integration
    │   │   ├── transactions/       # CRUD + analysis
    │   │   ├── saved_results/      # CRUD
    │   │   ├── bank_connections/   # CRUD
    │   │   └── optimizer/          # CashbackCalculator algorithm
    │   └── tests/
    ├── Dockerfile
    └── README.md
```

### Module Internal Layout

Each module follows uniform 4-file pattern (mirrors Spring's controller/service/repo/entity):

- `router.py` — FastAPI `APIRouter`
- `service.py` — business logic
- `repository.py` — SQLAlchemy data access
- `schema.py` — Pydantic models (request/response DTOs)
- `models.py` — SQLAlchemy ORM models

---

## 5. Data Layer

### Database Ownership Split

`savevia-ai` owns the same tables `savevia-optimizer` currently owns:

| Table | Source migration | Owner after cutover |
|---|---|---|
| `transactions` | 06-v2-transaction-upgrade.sql | **savevia-ai** |
| `saved_results` | (saved_results.sql) | **savevia-ai** |
| `bank_accounts` | 06-v2-transaction-upgrade.sql | **savevia-ai** |
| `bank_connections` | 06-v2-transaction-upgrade.sql | **savevia-ai** |
| `connection_history` | 07-connection-limits.sql | **savevia-ai** |
| `merchant_categories` | 28-merchant-rules.sql | **savevia-ai** |
| `missed_cashback_reports` | (existing) | **savevia-ai** |
| `user_connection_limits` | 07-connection-limits.sql | **savevia-ai** |

Tables that **stay with Java user service** and Python reads via HTTP:

- `chat_conversations`, `chat_messages` — Java user service still owns chat history CRUD
- `user_memory` — Java user service still owns memory CRUD
- `ai_usage_limits` — Java user service still owns AI usage tracking
- All user / auth / card / push tables

### Schema Strategy

- **Same MySQL instance** — no migration, Python opens its own connection pool to same DB
- **No schema changes** — Python uses `sqlacodegen` to reverse-engineer models from current tables; manually polish naming/relationships
- **Alembic baseline**: `alembic stamp head` marks current state; only future Python-owned schema changes go through Alembic (existing 29 SQL files remain for cold-start init)

### Translation: 2 MyBatis XMLs → Python Repositories

Only 2 mappers to translate (optimizer has lean DB layer):

- `TransactionMapper.xml` → `transactions/repository.py`
- `SavedResultMapper.xml` → `saved_results/repository.py`

Other DB tables (bank_connections, merchant_categories etc.) are accessed via service-level code in Java; Python translates to Repository pattern uniformly.

### Connection Pool

- MySQL: `pool_size=10, max_overflow=5, pool_pre_ping=True` (smaller than HikariCP default — AI service has fewer concurrent DB ops than user service)
- Redis: `max_connections=30`
- Pool is local to savevia-ai (Java services keep their own pools)

---

## 6. AI Agent Design (LangGraph)

### Current Java Behavior

- Loop: `LLM → ToolCall → ToolResult → LLM → ... → FinalAnswer`
- `MAX_ITERATIONS = 5`
- SSE streaming (chunked content + tool_call events)
- 6 tools, synchronous, JSON return
- `MemoryInjectionStrategy` injects long-term memory into system prompt
- Conversation history fetched from user service, passed manually as `messages`

### Python Implementation

**Use LangGraph's prebuilt `create_react_agent` — the canonical ReAct loop.**

```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

agent = create_react_agent(
    model=ChatOpenAI(model="gpt-4o-mini"),
    tools=[get_user_cards, search_cards, get_best_card,
           compare_cards, calculate_reward, get_card_usage_guide],
    checkpointer=MemorySaver(),       # short-term conversation memory (Redis-backed)
    state_modifier=inject_memory_prompt,  # long-term memory injection
)
```

Single call replaces the 1,738-LOC Java agent framework. Auto-generates OpenAI function schemas from Pydantic-typed tool signatures.

### ReAct Mapping

| ReAct phase | Implementation |
|---|---|
| **Reason** (LLM decides) | `agent` node inside `create_react_agent` |
| **Act** (execute tool) | `tools` node inside `create_react_agent` |
| **Observe** (see result) | `ToolMessage` auto-appended to `messages` |
| **Repeat or Stop** | Built-in router: tool_calls? → tools / else → END |

Modern ReAct uses native OpenAI function calling — no need for explicit "Thought/Action/Observation" text format.

### Tool Translation (6 tools)

| Java Tool | Python Tool | Data source |
|---|---|---|
| `GetUserCardsTool` | `get_user_cards(user_id)` | HTTP → savevia-user (`/api/v1/users/{id}/cards`) |
| `SearchCardsTool` | `search_cards(query, category, ...)` | HTTP → savevia-card (`/api/v1/cards/search`) |
| `GetBestCardTool` | `get_best_card(category, amount)` | HTTP → savevia-card + local CashbackCalculator |
| `CompareCardsTool` | `compare_cards(card_ids: list[int])` | HTTP → savevia-card (`/api/v1/cards/batch`) |
| `CalculateRewardTool` | `calculate_reward(card_id, category, amount)` | HTTP → savevia-card + local CashbackCalculator |
| `GetCardUsageGuideTool` | `get_card_usage_guide(card_id)` | HTTP → savevia-card (`/api/v1/cards/{id}/usage-tips`) |

All card data lives in Java card service. Python pulls via httpx on each tool call. Add Redis caching (60s TTL) for `search_cards` / `compare_cards` to absorb repeated calls within a conversation.

### Memory System

- **Short-term (in-conversation)**: LangGraph `MemorySaver` checkpoint keyed by `conversation_id`. Backend = Redis (so AI service is stateless and can scale).
- **Conversation history (cross-session, persistent)**: Java user service still owns `chat_messages`. Python's chat router fetches history via HTTP at conversation start, feeds it into the graph as initial state.
- **Long-term user memory**: `state_modifier` reads `user_memory` via HTTP → Java user service `/api/v1/memory/users/{id}` → injected into system prompt.
- **Memory extraction** (Java's 605-LOC `MemoryExtractionService`): Python runs a separate LangChain chain async (not in main graph) after each response, posts extracted memories back to Java user service for persistence.

### SSE Streaming

```python
@router.post("/api/v1/chat/stream")
async def chat_stream(req: ChatRequest, user_id: int = Depends(current_user)):
    async def event_generator():
        async for event in graph.astream_events(
            {"messages": [HumanMessage(req.message)], "user_id": user_id, ...},
            version="v2",
            config={"configurable": {"thread_id": req.conversation_id}},
        ):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                yield f"data: {json.dumps({'type': 'content', 'delta': event['data']['chunk'].content})}\n\n"
            elif kind == "on_tool_start":
                yield f"data: {json.dumps({'type': 'tool_call', 'name': event['name']})}\n\n"
            # ... other events
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

**SSE event format must 100% match current Java output** — frontend (web + mobile) zero changes.

### Future RAG (out of scope, architected for)

When RAG is added:
- Unwrap from `create_react_agent` to a custom `StateGraph`
- Insert `retrieve` node before `agent` node
- Vector stores: card knowledge base, user spending history, bank promotions

---

## 7. Inter-Service Communication

### Gateway → Python AI (inbound)

Add 4 new routes to `savevia-gateway/src/main/resources/application.yml`:

```yaml
spring:
  cloud:
    gateway:
      routes:
        # ... existing routes for user/card unchanged ...

        # NEW routes → Python AI
        - id: savevia-ai-chat
          uri: http://savevia-ai:8002
          predicates:
            - Path=/api/v1/chat/**
        - id: savevia-ai-transactions
          uri: http://savevia-ai:8002
          predicates:
            - Path=/api/v1/transactions/**
        - id: savevia-ai-saved-results
          uri: http://savevia-ai:8002
          predicates:
            - Path=/api/v1/saved-results/**
        - id: savevia-ai-bank-connections
          uri: http://savevia-ai:8002
          predicates:
            - Path=/api/v1/bank-connections/**
```

**Old `lb://savevia-optimizer` routes are removed at cutover time.** Java optimizer service stays running but receives no Gateway traffic.

### Python AI → Java services (outbound)

httpx async client with JWT pass-through:

```python
class UserServiceClient:
    def __init__(self, settings: Settings):
        self._base_url = settings.USER_SERVICE_URL  # http://savevia-user:8081

    def for_request(self, request: Request) -> httpx.AsyncClient:
        """Returns a client scoped to the current request, forwarding the user's JWT."""
        auth = request.headers.get("Authorization", "")
        return httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Authorization": auth},
            timeout=httpx.Timeout(10.0, connect=2.0),
        )

    async def get_user_cards(self, request: Request, user_id: int):
        async with self.for_request(request) as client:
            r = await client.get(f"/api/v1/users/{user_id}/cards")
            r.raise_for_status()
            return r.json()
```

### Auth Flow

- Inbound: Spring Cloud Gateway already validates JWT before routing. Python service also re-validates (defense in depth) using **same secret** — PyJWT with `HS256` and `JWT_SECRET` from environment.
- Outbound to Java: pass through the user's `Authorization` header. Java `JwtAuthFilter` validates normally.
- **No service-to-service tokens needed** — user JWT is sufficient.

### Configuration

Both `application.yml` (Java) and `.env` (Python) read:

| Env var | Used by | Value |
|---|---|---|
| `JWT_SECRET` | Java + Python | Same value |
| `USER_SERVICE_URL` | Python | `http://savevia-user:8081` (Docker) |
| `CARD_SERVICE_URL` | Python | `http://savevia-card:8082` (Docker) |
| `AI_SERVICE_URL` | Java Gateway | `http://savevia-ai:8002` |
| `DB_URL`, `REDIS_URL` | Both | Same MySQL / Redis as Java |

---

## 8. API Compatibility (frontend zero changes)

Python service exposes the **exact same endpoints** that Java optimizer exposed:

| Java Controller | Python Module | Path |
|---|---|---|
| `ChatStreamController` | `chat/router.py` | `/api/v1/chat/stream`, `/api/v1/chat/messages` |
| `OptimizerController` | `optimizer/router.py` | `/api/v1/optimizer/*` |
| `TransactionController` | `transactions/router.py` | `/api/v1/transactions/*` |
| `SavedResultController` | `saved_results/router.py` | `/api/v1/saved-results/*` |
| `BankConnectionController` | `bank_connections/router.py` | `/api/v1/bank-connections/*` |

### Hard Rules

| Dimension | Rule |
|---|---|
| Paths | Identical |
| Request body field names | Identical (camelCase) |
| Response field names + types | Identical (mind BigDecimal/Long JSON serialization) |
| HTTP status codes | Identical |
| SSE event types and payloads | Identical (frontend parses these) |
| Error response schema | 1:1 copy of `{code, message, data}` wrapper |

### Enforcement

Pydantic alias for camelCase:

```python
class TransactionDTO(BaseModel):
    user_id: int = Field(alias="userId")
    amount: Decimal = Field(alias="amount")
    model_config = ConfigDict(populate_by_name=True)
```

FastAPI: `response_model_by_alias=True`. CI runs API snapshot diff (see §10).

---

## 9. Cutover Plan (Big Bang for AI routes only)

### T-7 days: pre-production validation

- Deploy Python `savevia-ai` to staging EC2, connect to **prod RDS read-replica**
- Deploy modified Gateway config to staging — AI routes point to Python
- Run regression: API snapshot diff + SSE event diff + tool-call comparison vs prod Java optimizer
- iOS/Android test devices through staging gateway for 24h

### T-1 day: freeze

- Pause Java optimizer code releases (other Java services keep deploying normally)
- Close Flinks new-connection acceptance for ≥1h (let in-flight callbacks complete on Java side)
- Confirm Gateway config rollback procedure ready

### T-time (3-5 AM, Canada low-traffic window)

1. Deploy `savevia-ai` to prod
2. Apply Gateway config: AI routes flip from `lb://savevia-optimizer` to `http://savevia-ai:8002`
3. Restart Gateway (or `actuator/refresh` if Spring Cloud Config used)
4. Watch core metrics 5 min: AI endpoint error rate, SSE connection count, p99 latency, tool call success rate
5. Monitor 1h — anomaly → immediate rollback

### Rollback (≤ 5 min)

- Revert Gateway config: `uri: lb://savevia-optimizer`
- Restart Gateway
- Java optimizer is still running, it picks up traffic immediately
- Zero data loss (same DB, same Redis, same JWT)

### T+7 days: observation

- Java optimizer kept running (no traffic) — rollback safety net
- 7 days clean → shut down Java optimizer, remove from docker-compose, delete `savevia-optimizer/` directory

### What Doesn't Change

- DB schema and data
- Redis keys and data
- All other Java services (user/card/gateway/eureka/common) — unchanged
- Frontend / mobile apps — no release
- JWT tokens — user sessions persist
- Push notifications — Java user service still owns them
- Apple/Google OAuth — Java user service still owns them

---

## 10. Testing Strategy

| Layer | Tooling | Coverage target |
|---|---|---|
| Unit | pytest + pytest-asyncio | CashbackCalculator, Repository queries, Tool functions |
| Integration | pytest + httpx.AsyncClient + testcontainers MySQL | AI endpoints, JWT decode, Java service mock |
| Contract test (Java↔Python) | pytest with WireMock for Java services | Verify httpx client matches Java service contracts |
| API snapshot diff | Custom script: same input → Java optimizer + Python ai → JSON diff | Enforce compat rules |
| Agent behavior comparison | Fixed prompts + mocked LLM, compare tool-call sequence vs Java | Prevent silent regression |
| SSE format diff | Replay recorded SSE streams from Java, verify Python emits same events | Frontend doesn't break |
| Smoke | `smoke_test.py`: chat / save result / transaction list / bank connection | Run repeatedly on cutover day |

**Minimum acceptance**: AI endpoint critical paths (chat, transactions, saved results) ≥70%; supporting code ≥50%.

---

## 11. Effort & Timeline

### Code Volume

- Java to delete: 6,926 LOC (savevia-optimizer)
- Python to write: **~3,200 LOC** (LangGraph compresses agent framework dramatically; LangChain handles streaming/tool schemas)

### Effort Breakdown (solo senior engineer)

| Phase | Module | Complexity | Days |
|---|---|---|---|
| **P0** | Project skeleton (uv, Docker, Alembic baseline, FastAPI app, config, logging, JWT decode) | ★★ | 3 |
| **P0** | HTTP clients to Java user/card (httpx + JWT pass-through) | ★★ | 2 |
| **P1** | SQLAlchemy models for 8 owned tables (`sqlacodegen` + polish) | ★★ | 2 |
| **P1** | Translate 2 MyBatis mappers → Repository | ★ | 1 |
| **P2** | LangGraph agent + 6 tools + system prompt translation | ★★★ | 6 |
| **P2** | SSE streaming endpoint (matches Java event format) | ★★★ | 3 |
| **P2** | ChatService logic (history fetch, rate limit check, conversation flow) | ★★★ | 5 |
| **P3** | MemoryExtraction async chain (605 LOC → ~400 LOC LangChain) | ★★★ | 5 |
| **P3** | MemoryInjection state_modifier | ★ | 1 |
| **P4** | Flinks integration (585 LOC HTTP/callback → httpx) | ★★★ | 4 |
| **P4** | CashbackOptimizer + Transaction analysis | ★★ | 4 |
| **P4** | SavedResult + ConnectionLimit + BankConnection endpoints | ★★ | 3 |
| **P5** | Gateway route config update + staging deploy | ★★ | 2 |
| **P5** | API snapshot diff + SSE diff + agent regression suite | ★★★ | 4 |
| **P5** | Load test (k6 or locust) — verify ≤+15% latency budget | ★★ | 2 |
| **P5** | Device regression (iOS + Android + Web — chat flow) | ★★ | 2 |
| **P6** | Cutover day + observation + hotfix budget | ★★ | 2 |
| **P7** | Java optimizer cleanup (delete dir, remove from docker-compose) | ★ | 1 |
| | **Core dev subtotal** | | **52** |
| | **Risk buffer (+15%)** | | **+8** |
| | **Total** | | **~60 person-days** |

### Calendar Timeline

| Mode | Duration |
|---|---|
| Solo full-time | **~6-7 weeks** |
| Part-time (3-4h/day) | ~3 months |

### Schedule (solo full-time)

```
Week 1     P0 + P1: Skeleton, HTTP clients, SQLAlchemy models, repos
Week 2     P2 (1/2): LangGraph agent + 6 tools
Week 3     P2 (2/2): SSE streaming + ChatService logic
Week 4     P3: Memory extraction + injection
Week 5     P4: Flinks + Optimizer + Transaction + SavedResult
Week 6     P5: Gateway config + staging deploy + regression + load test + device test
Week 7     P6 + P7: Cutover + 7-day observation + Java cleanup
```

---

## 12. Risk Register

Ranked by likelihood × impact:

| # | Risk | Mitigation |
|---|---|---|
| 1 🟡 | LangGraph SSE event granularity ≠ frontend expectations | Recorded SSE replay diff in CI; manual event-level alignment; on-device chat regression |
| 2 🟡 | `MemoryExtractionService` (605 LOC) prompt translation drift | Verbatim prompt copy; offline quality eval on 50 historical conversations |
| 3 🟡 | Pydantic vs Jackson serialization differences (nulls, empty arrays, Decimal precision) | CI API snapshot diff; Pydantic config tuning (`exclude_none`, `ser_json_inf_nan`) |
| 4 🟡 | httpx → Java services: timeout/retry behavior different from Feign defaults | Match Feign defaults (10s timeout, no auto-retry); add explicit retry on 5xx with backoff |
| 5 🟢 | Flinks in-flight callbacks during cutover | Close new connection acceptance 1h pre-cutover; in-flight callbacks finish on Java optimizer (which keeps running 7 days) |
| 6 🟢 | LangGraph `MemorySaver` Redis backend key conflicts with existing keys | Namespace all LangGraph keys with `langgraph:` prefix; grep verify no conflict |
| 7 🟢 | Tool call cache (Redis 60s TTL) returning stale card data | Cache key includes data version; or skip cache for `get_best_card` |
| 8 🟢 | Eureka unaware of Python service → Java services try to call it | N/A — verified that no Java service calls savevia-optimizer; only Gateway does (via updated direct URI) |
| 9 🟢 | docker-compose port conflict | Pre-cutover: `savevia-ai` on 8002 (savevia-optimizer keeps 8083) — no conflict |

### What's NOT a risk (because we're not touching it)

- ❌ JWT incompatibility — same secret, only Java decodes user-facing tokens at Gateway
- ❌ Apple Sign-In bugs — stays in Java
- ❌ ScheduledPushService timing — stays in Java
- ❌ AdminStats aggregation accuracy — stays in Java
- ❌ Database migration — none
- ❌ Mobile app re-release — none

---

## 13. Parallelizable Prep Work

Can start now without blocking main development:

- Reverse-generate SQLAlchemy models (`sqlacodegen`) for the 8 owned tables
- Extract all Java optimizer system prompts / tool descriptions into reference files for verbatim copy
- Record 20-30 representative SSE chat streams from prod Java for diff baseline
- Compile OpenAPI spec from Java optimizer controllers for compat reference

---

## 14. Out of Scope

- Rewriting any other Java service (user / card / gateway / eureka / common)
- RAG implementation (architecture supports it, not built)
- Database schema changes
- Frontend / mobile changes
- Migration to Postgres / pgvector
- Migration to K8s / ECS
- CI/CD pipeline overhaul

---

## 15. Definition of Done

- All endpoints currently served by `savevia-optimizer` implemented in `savevia-ai` and passing integration tests
- API snapshot diff vs Java optimizer: 0 mismatches on critical paths
- SSE event diff: 0 missing/extra events on 20+ recorded test conversations
- Agent behavior diff: same tool-call sequences on 50+ fixed prompts
- Load test: AI endpoint p99 latency within +15% of Java baseline
- Smoke test passes on iOS + Android + Web from staging
- Cutover executed; 7-day observation period clean
- Java `savevia-optimizer/` directory deleted from repo
- `docker-compose.yml` updated; old optimizer service entry removed
- README updated with `savevia-ai` dev workflow

---

## 16. Future Path (not committed)

If after 6-12 months of running savevia-ai we decide to migrate more services to Python, this design's pattern (Gateway routes + httpx + JWT pass-through + shared DB) is the template — each future service can follow the same playbook independently. No big-bang second wave required.

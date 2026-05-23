# SaveVia Python Rewrite — Design Spec

- **Date**: 2026-05-23
- **Author**: 颜成 (with Claude brainstorming session)
- **Status**: Approved (pending implementation plan)
- **Scope**: Full rewrite of all 6 Java/Spring Cloud microservices into 2 Python/FastAPI services

---

## 1. Motivation

Current backend (16,400 LOC Java, 6 microservices) works but is becoming a bottleneck for AI/RAG iteration. Python ecosystem offers:

- First-class LLM/agent frameworks (LangGraph, LangChain, LlamaIndex)
- Faster experimentation cycles for AI features
- Better long-term direction for the product's AI-heavy roadmap

Decision: **full rewrite, big-bang cutover, 100% API/JWT backward compatible** — mobile clients and frontend require zero changes.

---

## 2. Target Architecture

### Service Topology

```
                      ┌─────────────────┐
                      │   savevia-web   │ React + Capacitor (unchanged)
                      └────────┬────────┘
                               │
                      ┌────────▼────────┐
                      │ savevia-gateway │ Nginx
                      │   (port 8080)   │ Routing + rate limit + CORS
                      └────────┬────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
        ┌─────────▼─────────┐    ┌─────────▼─────────┐
        │   savevia-api     │    │    savevia-ai     │
        │   (port 8001)     │    │   (port 8002)     │
        │   FastAPI         │    │   FastAPI         │
        │   user/card/auth/ │    │   chat/agent/     │
        │   push/admin      │    │   memory/flinks   │
        └─────────┬─────────┘    └─────────┬─────────┘
                  │                         │
                  └────────────┬────────────┘
                               │
              MySQL 8 (RDS)   Redis 7 (ElastiCache)   ← unchanged
```

### Service Boundary Rationale

- **2 services** instead of 6: AI workloads (streaming, long-lived connections, GPU candidates, frequent model swaps) have different scaling/iteration profiles than CRUD; everything else collapses into a single FastAPI app.
- **Eureka removed**: K8s/internal DNS handles discovery in production; localhost in dev. Python ecosystem rarely uses Eureka.
- **Gateway becomes Nginx**: Config-driven, lighter than Spring Cloud Gateway. JWT is verified inside each Python service (shared secret), not at the gateway. Nginx handles routing, rate limiting (`limit_req_zone`), and CORS.
- **Shared MySQL/Redis**: Same RDS instance, same schema, same ElastiCache cluster — zero data migration risk.

---

## 3. Tech Stack

| Layer | Choice |
|---|---|
| Language | Python 3.12 |
| Web framework | FastAPI + uvicorn (dev) / gunicorn+uvicorn workers (prod) |
| Validation / DTO | Pydantic v2 |
| ORM | SQLAlchemy 2.0 async + Alembic |
| MySQL driver | aiomysql (asyncmy as backup) |
| Redis | redis-py (async) |
| AI Agent | **LangGraph** (`create_react_agent` prebuilt) + LangChain (selectively) |
| LLM SDK | openai SDK (primary), anthropic SDK (future option) |
| Streaming | FastAPI `StreamingResponse` (SSE) |
| Auth | PyJWT (HS256, same secret as Java) |
| OAuth | google-auth (Google); custom impl (Apple Sign-In) |
| Push | aioapns (iOS) + firebase-admin (FCM / Android) |
| HTTP client | httpx (async) |
| Email | aiosmtplib |
| Test | pytest + pytest-asyncio + httpx.AsyncClient + testcontainers |
| Dependency mgmt | uv (workspace mode) |
| Deployment | Docker + Docker Compose (EC2 + RDS + ElastiCache + S3+CloudFront unchanged) |
| Logging | structlog (structured) + Loguru (dev) |
| Monitoring | Prometheus client + OpenTelemetry (optional) |

---

## 4. Repository Structure

Python code coexists with Java in the current `savevia/` repo during development. Java is deleted post-cutover.

```
savevia/                      # existing repo
├── savevia-* (Java)          # kept until cutover + 7 days, then deleted
├── savevia-web/              # React frontend, unchanged
├── docker/mysql/init/        # existing SQL migrations preserved
├── docker-compose.yml        # updated to add Python services
└── savevia-python/           # NEW — all Python code
    ├── pyproject.toml        # uv workspace root
    ├── savevia-common/       # shared Pydantic models / utils
    ├── savevia-api/
    │   ├── pyproject.toml
    │   ├── alembic/
    │   ├── app/
    │   │   ├── main.py
    │   │   ├── core/         # config, security, db
    │   │   ├── modules/
    │   │   │   ├── auth/     # router/service/repo/schema/models
    │   │   │   ├── user/
    │   │   │   ├── card/
    │   │   │   ├── admin/
    │   │   │   └── push/
    │   │   └── tests/
    └── savevia-ai/
        ├── pyproject.toml
        ├── app/
        │   ├── main.py
        │   ├── core/
        │   ├── modules/
        │   │   ├── chat/     # SSE endpoint
        │   │   ├── agent/    # LangGraph graph
        │   │   ├── tools/    # 6 LangChain @tool functions
        │   │   ├── memory/   # extraction + injection
        │   │   ├── flinks/   # bank connection
        │   │   └── optimizer/  # cashback algorithm
        │   └── tests/
```

### Module Internal Layout (uniform 4-layer)

Each module contains:

- `router.py` — FastAPI `APIRouter` (≈ Spring Controller)
- `service.py` — business logic
- `repository.py` — SQLAlchemy data access
- `schema.py` — Pydantic models (DTOs)
- `models.py` — SQLAlchemy ORM models

---

## 5. Data Layer

### Database Compatibility

- **MySQL schema unchanged.** Python connects to the same RDS instance.
- All 29 existing SQL migration files (`docker/mysql/init/01~29-*.sql`) remain as-is for cold-start init.
- Use `sqlacodegen` to reverse-engineer initial SQLAlchemy models from current schema; then manually polish (naming, relationships, index comments).
- **Alembic baseline**: `alembic stamp head` to mark current schema as the starting point. All future schema changes go through Alembic.

### MyBatis → Repository Translation

20 XML mappers map to 20 Python `repository.py` files.

| MyBatis pattern | Python translation |
|---|---|
| Simple CRUD `<select>` | SQLAlchemy ORM: `session.execute(select(User).where(...))` |
| Complex JOIN / aggregation | SQLAlchemy **Core** with explicit join clauses |
| Dynamic SQL `<if>` / `<foreach>` | Python conditional `where_clauses.append(...)` |
| Truly complex (e.g. AdminStats) | `session.execute(text("..."))` with raw SQL |

**Discipline**: Service layer **never** writes raw SQL — all DB access goes through Repository.

### Transactions & Connection Pool

- Default: one `AsyncSession` per HTTP request (FastAPI `Depends`)
- Cross-repository: `async with session.begin():` in Service
- Pool config (matches HikariCP defaults): `pool_size=20, max_overflow=10, pool_pre_ping=True`
- Redis: `max_connections=50`
- Both Python services maintain **separate** connection pools

### Data Compatibility Validation (pre-cutover)

1. Schema diff: Python ORM models vs `SHOW CREATE TABLE` — 100% alignment
2. Key-query regression: 5-10 critical queries (login, card list, chat history, AdminStats) — Java vs Python output diff = 0
3. JSON field compatibility: confirm `reward_rules`, `memory_data` etc. serialize identically

---

## 6. AI Agent Design (LangGraph)

### Current Java Behavior

- Loop: `LLM → ToolCall → ToolResult → LLM → ... → FinalAnswer`
- `MAX_ITERATIONS = 5`
- SSE streaming (chunked content + tool_call events)
- 6 tools, synchronous, JSON return
- `MemoryInjectionStrategy` injects long-term memory into system prompt

### Python Implementation

**Use LangGraph's prebuilt `create_react_agent` — the canonical ReAct loop.**

```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

agent = create_react_agent(
    model=ChatOpenAI(model="gpt-4o-mini"),
    tools=[get_user_cards, search_cards, get_best_card,
           compare_cards, calculate_reward, get_card_usage_guide],
    checkpointer=MemorySaver(),       # short-term conversation memory
    state_modifier=inject_memory_prompt,  # long-term memory injection
)
```

This single call replaces the entire 1,738-LOC Java agent framework. Auto-generates OpenAI function schemas from Pydantic-typed tool signatures.

### ReAct Mapping

| ReAct phase | Implementation |
|---|---|
| **Reason** (LLM decides) | `agent` node (LLM call) |
| **Act** (execute tool) | `tools` node |
| **Observe** (see result) | `ToolMessage` appended to `messages` |
| **Repeat or Stop** | Router: tool_calls? → tools / else → END |

Modern ReAct uses native OpenAI tool calling — no need for explicit "Thought/Action/Observation" text format.

### Tool Translation (6 tools)

| Java Tool | Python Tool |
|---|---|
| `GetUserCardsTool` | `get_user_cards(user_id)` |
| `SearchCardsTool` | `search_cards(query, category, ...)` |
| `GetBestCardTool` | `get_best_card(category, amount)` |
| `CompareCardsTool` | `compare_cards(card_ids: list[int])` |
| `CalculateRewardTool` | `calculate_reward(card_id, category, amount)` |
| `GetCardUsageGuideTool` | `get_card_usage_guide(card_id)` |

### Memory System

- **Short-term**: LangGraph `MemorySaver` checkpoint keyed by `conversation_id` (Redis or MySQL backend) — replaces manually-passed `conversationHistory`
- **Long-term**: `state_modifier` reads `user_memory` table, injects into system prompt — preserves current behavior
- **Memory extraction** (605 LOC `MemoryExtractionService`): a separate LangChain chain triggered async, writes back to `user_memory` — not part of the main graph

### SSE Streaming

```python
@router.post("/chat/stream")
async def chat_stream(req: ChatRequest, user=Depends(current_user)):
    async def event_generator():
        async for event in graph.astream_events(
            {"messages": [HumanMessage(req.message)], "user_id": user.id, ...},
            version="v2",
            config={"configurable": {"thread_id": req.conversation_id}},
        ):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                yield f"data: {json.dumps({'type': 'content', 'delta': event['data']['chunk'].content})}\n\n"
            elif kind == "on_tool_start":
                yield f"data: {json.dumps({'type': 'tool_call', 'name': event['name']})}\n\n"
            # ...
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

SSE event format must **100% match** current Java output — frontend zero changes.

### Future RAG (out of scope for this rewrite, but architected for)

When RAG is added:

- Unwrap from `create_react_agent` to a custom `StateGraph`
- Insert `retrieve` node before `agent`
- Use `langchain-postgres` or `pgvector` (if migrating to Postgres later)
- Vector stores: card knowledge base / user spending history / bank promotions

### Performance Targets

| Metric | Target |
|---|---|
| First token latency | ≤ Java baseline +10% |
| Full response (5 tool calls) | ≤ Java baseline +15% |
| SSE event format | 100% compatible (no frontend changes) |
| MAX_ITERATIONS | Same as Java (5) |
| Tool behavior | Same input → same output (verified by comparison tests) |

---

## 7. API & Auth Compatibility (zero frontend changes)

### Hard Rules

| Dimension | Rule |
|---|---|
| Paths | `/api/v1/...` identical (17 controllers × ~5 endpoints ≈ 80+) |
| Request field names | Identical — no camelCase → snake_case |
| Response field names + types | Identical (mind BigDecimal/Long JSON serialization) |
| HTTP status codes | Identical (especially 4xx semantics) |
| Headers | `Authorization: Bearer ...`, `Accept-Language`, etc. unchanged |
| Error response schema | 1:1 copy of current `{code, message, data}` wrapper |

### Enforcement

Pydantic alias for camelCase:

```python
class UserCardDTO(BaseModel):
    user_id: int = Field(alias="userId")
    card_name: str = Field(alias="cardName")
    model_config = ConfigDict(populate_by_name=True)
```

FastAPI: `response_model_by_alias=True`. CI runs API snapshot diff tests (see §9).

### JWT Compatibility

| Item | Config |
|---|---|
| Algorithm | HS256 (identical) |
| Secret | Reuse existing `.env` `JWT_SECRET` |
| Claims | `userId`, `email`, `exp`, `iat`, `tokenVersion` — exact field names |
| Blacklist key format | Redis `jwt:blacklist:xxx` — unchanged |
| Refresh flow | Endpoint / params / response 1:1 |

Pre-cutover validation: same JWT decoded successfully by both Java and Python yields same user identity.

### OAuth

| Provider | Library | Config reuse |
|---|---|---|
| Google | `google-auth` + `google-auth-oauthlib` | `GOOGLE_CLIENT_ID` |
| Apple | Custom (PyJWT + cryptography for JWKS verify + httpx) | Existing `.p8` + Team ID + Key ID |

Apple Sign-In is the highest-risk component — no off-the-shelf Python SDK matches Java's. Plan 2-3 days, allow 5.

### Push Notifications Continuity

- APNs: `aioapns` reads existing `.p8` — no cert reissue
- FCM: `firebase-admin` reads existing service account JSON
- `device_token` table preserved → registered devices continue receiving pushes
- `ScheduledPushService` (676 LOC): APScheduler or FastAPI startup background task; cron expressions copied verbatim

### Flinks

- 585-LOC `FlinksService` is pure HTTP + callback handling — translate to httpx
- Callback URL unchanged
- Pre-cutover: close new Flinks connection acceptance for ≥1 hour to let in-flight callbacks complete

---

## 8. Cutover Plan (Big Bang)

### T-7 days: pre-production validation

- Deploy Python services to staging EC2, connect to **prod RDS read-replica**
- Run full regression: API snapshot diff + JWT interop + tool-call comparison
- iOS/Android test devices point to staging gateway for 24h

### T-1 day: freeze

- Pause Java code releases
- Close Flinks new-connection acceptance (let in-flight callbacks finish)
- Confirm DNS / gateway rollback scripts ready

### T-time (recommended 3-5 AM, Canada low-traffic window)

1. Nginx gateway flips upstream (Java → Python) — instantaneous
2. Watch core metrics for 5 min: QPS, error rate, p99 latency, JWT verify failure rate, SSE connection count
3. Monitor 1h — any metric anomaly → immediate rollback

### Rollback (must be ≤ 5 minutes)

- Single command: `nginx -s reload` (upstream back to Java)
- Because DB unchanged + JWT compatible: zero data loss / session loss

### T+7 days: observation

- Java services kept running (no traffic) — rollback available
- 7 days clean → shut down Java, archive code, delete from repo

### Untouched

- MySQL data: same RDS instance
- Redis data: same ElastiCache (verify key naming consistency — JWT blacklist, rate limit, chat session)
- S3, CloudFront: unchanged
- Frontend: no release

---

## 9. Testing Strategy

| Layer | Tooling | Coverage target |
|---|---|---|
| Unit | pytest + pytest-asyncio | Core algorithms (CashbackCalculator), Repository queries, Tool functions |
| Integration | pytest + httpx.AsyncClient + testcontainers MySQL | All REST endpoints, JWT flow |
| API snapshot diff | Custom script: same input → Java + Python → diff JSON | Strict enforcement of compat rules |
| Agent behavior comparison | Fixed prompts + mocked LLM, compare tool-call sequence | LangGraph cannot silently regress |
| Smoke | `smoke_test.py` covering login/cards/chat/push | Run repeatedly on cutover day |

**Minimum acceptance**: critical paths (login, card list, chat, push) ≥70% coverage; other modules ≥50%.

---

## 10. Effort & Timeline

### Code Volume Estimate

Python output: **~10,000-12,000 LOC** (vs Java 16,400 — 25-35% reduction from agent framework, DTO/Entity merging, and Nginx replacing Spring Cloud Gateway).

### Effort Breakdown (solo senior engineer)

| Phase | Module | Complexity | Days |
|---|---|---|---|
| **P0** | Project skeleton (uv workspace, Docker, Alembic baseline, CI, logging/config) | ★★ | 5 |
| **P0** | savevia-common (shared models + utils) | ★ | 2 |
| **P1** | savevia-api: Auth (JWT + Google + Apple) | ★★★★ | 8 |
| **P1** | savevia-api: User Profile / UserCard / UserSpending | ★★ | 5 |
| **P1** | savevia-api: Card (CRUD + Affiliate) | ★★ | 4 |
| **P2** | savevia-api: Admin (incl. AdminStats aggregation) | ★★★ | 5 |
| **P2** | savevia-api: Push (APNs + FCM + ScheduledPush 676 LOC) | ★★★★ | 7 |
| **P2** | savevia-api: AiUsage / AppVersion / Memory CRUD | ★★ | 3 |
| **P3** | savevia-ai: LangGraph Agent + 6 Tools + SSE | ★★★★ | 9 |
| **P3** | savevia-ai: ChatService (session/history/rate-limit) | ★★★ | 5 |
| **P4** | savevia-ai: MemoryExtraction (605 LOC → LangChain chain) | ★★★ | 5 |
| **P4** | savevia-ai: Flinks integration (585 LOC) | ★★★ | 4 |
| **P4** | savevia-ai: CashbackOptimizer + Transaction analysis | ★★ | 4 |
| **P4** | savevia-ai: SavedResult / ConnectionLimit | ★ | 2 |
| **P5** | Nginx gateway config + rate-limit scripts | ★★ | 3 |
| **P5** | Staging deploy + API snapshot diff + load test | ★★★ | 5 |
| **P5** | Device regression (iOS + Android + Web) | ★★ | 3 |
| **P6** | Cutover day + observation + hotfix | ★★ | 3 |
| **P7** | Java code archive + cleanup | ★ | 1 |
| | **Core dev subtotal** | | **83** |
| | **Risk buffer (+20%)** | | **+17** |
| | **Total** | | **~100 person-days** |

### Calendar Timeline

| Mode | Duration |
|---|---|
| Solo full-time | ~12 weeks (3 months) |
| Two engineers in parallel (api + ai) | ~7-8 weeks (2 months) |
| Part-time (3-4h/day) | ~5-6 months |

### Schedule (solo full-time)

```
Week  1     P0: Skeleton + Common
Week  2-3   P1: Auth + User + Card               ← Apple Sign-In hardest
Week  4-5   P2: Admin + Push + misc
Week  6-7   P3: AI Agent + Chat + SSE            ← LangGraph learning peak
Week  8     P4 (1/2): Memory + Flinks
Week  9     P4 (2/2): Optimizer + Transaction
Week 10     P5: Gateway + Staging deploy
Week 11     P5: Full regression + load test + device test
Week 12     P6: Cutover + 7-day observation + Java cleanup
```

---

## 11. Risk Register

Ranked by likelihood × impact:

| # | Risk | Mitigation |
|---|---|---|
| 1 🔴 | Apple Sign-In custom impl bugs | T-7 days: 100 simulated logins on staging |
| 2 🔴 | LangGraph SSE event granularity ≠ frontend expectations | Manual event format alignment + on-device chat regression |
| 3 🟡 | `ScheduledPushService` (676 LOC) cron + multi-timezone bugs | Same cron expressions + same TZ + reconcile first post-cutover push |
| 4 🟡 | `MemoryExtractionService` (605 LOC) prompt translation drift | Verbatim prompt copy + offline quality eval before cutover |
| 5 🟡 | Pydantic vs Jackson serialization differences (nulls, empty arrays, date formats) | CI API snapshot diff + Pydantic config tuning |
| 6 🟢 | Flinks in-flight callbacks during cutover | Close new connection acceptance 1h pre-cutover |
| 7 🟢 | Redis key naming inconsistency → user logout | Pre-cutover grep all Redis keys + mapping table |
| 8 🟢 | MyBatis vs SQLAlchemy transaction defaults | Explicit `isolation_level="READ COMMITTED"` |

---

## 12. Parallelizable Prep Work

Can start now without blocking main development (delegatable to AI/junior):

- Translate 20 MyBatis XMLs into Repository drafts (mechanical translation + manual review)
- Reverse-generate SQLAlchemy models (`sqlacodegen`)
- Compile all endpoint OpenAPI descriptions from Java Controller annotations
- Prepare API snapshot diff dataset

---

## 13. Out of Scope

- RAG implementation (architected for, not built)
- Database schema changes (kept identical)
- Frontend changes (zero)
- Migration to Postgres / pgvector (future consideration)
- Migration off EC2 to ECS/EKS (future consideration)
- CI/CD pipeline build-out (separate spec)

---

## 14. Definition of Done

- All endpoints in §10 phases P1-P4 implemented and passing integration tests
- API snapshot diff against Java: 0 mismatches on critical paths
- Smoke test passes on iOS + Android + Web from staging
- Cutover executed and 7-day observation period clean
- Java services archived (code remains in git history, removed from working tree)
- README updated with new Python dev/deploy workflow

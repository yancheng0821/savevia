# savevia-ai Remaining Endpoints — Implementation Plan (Phase 4)

> **Status:** SKELETON. Step-level detail to be written when Phase 4 begins.

**Goal:** Port the remaining non-chat business endpoints from Java optimizer to Python: Flinks bank connection integration, transactions analysis, saved results CRUD, bank connection CRUD, and the cashback optimizer (single-purchase recommendation endpoint). After this plan, **every endpoint currently served by `savevia-optimizer` is implemented in `savevia-ai`** — Java optimizer can be decommissioned (subject to staging validation in Phase 5).

**Architecture:** Standard FastAPI module pattern (router → service → repository). Flinks integration uses httpx for outbound HTTP and FastAPI routes for inbound webhook callbacks. CashbackCalculator (already implemented in Phase 2 Task 2) is reused by the OptimizerController endpoints.

**Tech Stack:** Everything from Phase 1+2+3. No new dependencies.

**Reference spec:** `docs/superpowers/specs/2026-05-23-python-rewrite-design.md` §11 (Phase 4)

**Estimated effort:** 11 person-days (1.5 weeks solo).

**Reference Java code:**
- `savevia-optimizer/src/main/java/com/savevia/optimizer/service/FlinksService.java` (585 LOC)
- `savevia-optimizer/src/main/java/com/savevia/optimizer/controller/BankConnectionController.java`
- `savevia-optimizer/src/main/java/com/savevia/optimizer/controller/TransactionController.java`
- `savevia-optimizer/src/main/java/com/savevia/optimizer/controller/SavedResultController.java`
- `savevia-optimizer/src/main/java/com/savevia/optimizer/controller/OptimizerController.java`
- `savevia-optimizer/src/main/java/com/savevia/optimizer/service/TransactionAnalysisService.java`
- `savevia-optimizer/src/main/java/com/savevia/optimizer/service/TransactionCategorizationService.java`
- `savevia-optimizer/src/main/java/com/savevia/optimizer/service/CashbackOptimizerService.java`
- `savevia-optimizer/src/main/java/com/savevia/optimizer/service/SavedResultService.java`
- `savevia-optimizer/src/main/java/com/savevia/optimizer/service/ConnectionLimitService.java`

---

## File Structure (additions over Phase 3)

```
savevia-ai/app/
├── modules/
│   ├── flinks/
│   │   ├── __init__.py
│   │   ├── client.py                  # httpx client to Flinks API
│   │   ├── service.py                 # business logic (connect/refresh/disconnect)
│   │   ├── webhook.py                 # FastAPI webhook handler
│   │   ├── schema.py                  # FlinksLoginRequest, FlinksAccount, etc.
│   │   └── router.py                  # not exposed; webhook only
│   ├── bank_connections/
│   │   ├── __init__.py
│   │   ├── router.py                  # /api/v1/bank-connections/*
│   │   ├── service.py
│   │   ├── repository.py              # uses BankConnection + BankAccount models
│   │   └── schema.py
│   ├── transactions/
│   │   ├── __init__.py
│   │   ├── router.py                  # /api/v1/transactions/*
│   │   ├── service.py                 # analysis + categorization
│   │   ├── categorization.py          # MCC → category mapping (merchant_categories table)
│   │   ├── analysis.py                # actual vs optimal cashback calc
│   │   └── schema.py
│   ├── saved_results/
│   │   ├── __init__.py
│   │   ├── router.py                  # /api/v1/saved-results/*
│   │   ├── service.py
│   │   └── schema.py
│   ├── optimizer_api/
│   │   ├── __init__.py
│   │   ├── router.py                  # /api/v1/optimize/* (single-purchase recommendation)
│   │   ├── service.py
│   │   └── schema.py
│   └── connection_limits/
│       ├── __init__.py
│       ├── service.py                 # daily Flinks connection cap
│       └── repository.py
└── tests/
    └── modules/
        ├── flinks/
        │   ├── test_client.py
        │   ├── test_service.py
        │   └── test_webhook.py
        ├── bank_connections/
        │   ├── test_router.py
        │   └── test_service.py
        ├── transactions/
        │   ├── test_router.py
        │   ├── test_categorization.py
        │   └── test_analysis.py
        ├── saved_results/
        │   └── test_router.py
        ├── optimizer_api/
        │   └── test_router.py
        └── connection_limits/
            └── test_service.py
```

---

## Task List

| # | Task | Files | Days |
|---|---|---|---|
| 1 | Flinks API client (httpx wrapper) — login/authorize/accounts/transactions | `modules/flinks/client.py` + test | 1 |
| 2 | Flinks service: connect, refresh, disconnect, sandbox mode | `modules/flinks/service.py` + test | 1.5 |
| 3 | Flinks webhook handler (verify signature, handle async callbacks) | `modules/flinks/webhook.py` + test | 0.5 |
| 4 | ConnectionLimit repository + service (daily cap enforcement) | `modules/connection_limits/` + test | 1 |
| 5 | Bank connection module (router/service/repository) | `modules/bank_connections/` + test | 1 |
| 6 | Transaction categorization (MCC + merchant rules from merchant_categories table) | `modules/transactions/categorization.py` + test | 1 |
| 7 | Transaction analysis (compute actual/optimal/missed cashback using CashbackCalculator) | `modules/transactions/analysis.py` + test | 1 |
| 8 | Transaction router + service (list, analyze, summary, batch-import from Flinks) | `modules/transactions/router.py`, `service.py` + tests | 1.5 |
| 9 | Saved results module | `modules/saved_results/` + test | 1 |
| 10 | Optimizer API endpoints (single-purchase recommendation) | `modules/optimizer_api/` + test | 1 |
| 11 | Wire all routers into FastAPI app | `app/main.py` (modify) | 0.5 |
| | **Subtotal** | | **11** |

---

## Key Design Decisions to Confirm Before Writing Step-Level Detail

1. **Flinks sandbox toggle**: env var `FLINKS_SANDBOX=true/false`. Match Java's current behavior — when true, return mock data without calling Flinks.
2. **Flinks webhook URL**: must remain identical to current Java endpoint path; mobile/Flinks Connect iframe is configured with that URL.
3. **Transaction import idempotency**: Java uses `flinks_transaction_id` unique-ish — replicate the dedupe logic exactly.
4. **Connection limit window**: confirm Java uses calendar-day or rolling-24h. Match exactly to avoid surprise limits hitting users at midnight.
5. **OptimizerController endpoint paths**: read the Java controller to enumerate exact routes (`/api/v1/optimize/calculate`, `/api/v1/optimize/recommend`, etc.).
6. **Transaction analysis batch vs streaming**: Java may analyze in chunks. Confirm whether to stream progress via SSE or run sync.

---

## Definition of Done

- Every endpoint currently served by `savevia-optimizer` has an equivalent in `savevia-ai`
- Endpoint paths, request/response shapes match Java exactly (CI snapshot diff)
- Flinks webhook responds correctly to sandbox callbacks
- Connection limit enforcement matches Java behavior
- Transaction analysis output matches Java for 50+ recorded transactions
- All Phase 4 unit tests pass; Phase 1-3 tests still pass
- Tag `savevia-ai-phase-4` on completion

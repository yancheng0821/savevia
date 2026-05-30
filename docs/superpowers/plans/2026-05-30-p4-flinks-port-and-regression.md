# P4 Finish — Flinks/Bank Port + AI Explanations + Real Regression — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring Python `savevia-ai` to full parity with the Java optimizer by porting the Flinks/bank-connection subsystem + AI explanations, then turn the two skipped regressions (SSE structure, memory quality) into real assertions — all on `feature/python-ai-foundation`, no merge to `main`.

**Architecture:** Standard FastAPI module pattern already used in the repo (router → service → repository, `Result<T>` envelope, Pydantic camelCase DTOs). Flinks runs demo/mock mode (no contract); the real REST path is ported but inert and `FLINKS_SANDBOX`-guarded. No webhook (Java has none). Reuses existing `CategorizationService`, `CardServiceClient`, `TransactionRepository.find_by_account_and_flinks_id`.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0 async, Pydantic v2, httpx, pytest + pytest-asyncio (auto mode), respx, langchain-openai. `uv` for deps. Working dir: `/Users/aisenyc/savevia/.worktrees/python-ai-foundation`. Run tests from `savevia-ai/` via `.venv/bin/python -m pytest`.

**Reference spec:** `docs/superpowers/specs/2026-05-30-p4-flinks-port-and-regression-design.md`
**Authoritative Java behavior source:**
- `savevia-optimizer/.../service/FlinksService.java` (585 LOC)
- `savevia-optimizer/.../controller/BankConnectionController.java` (223 LOC)
- `savevia-optimizer/.../service/ConnectionLimitService.java` (127 LOC)
- `savevia-optimizer/.../service/OpenAiService.java` (explanations)

**Parity rules (apply throughout):**
- `Result.error(String)` → **code 500**; `_ok(data)` → code 200; `timestamp` field stays `0` (repo convention; snapshot diff strips it).
- All response field names camelCase via Pydantic alias; `model_dump(by_alias=True, mode="json")`.
- All paths under `/api/v1/optimize/bank`, `X-User-Id` header carries the user id.

---

## Phase 0 — Sync feature branch & baseline

### Task 0.1: Merge `main` into the feature branch and establish a green baseline

**Files:** none created; merge commit only.

- [ ] **Step 1: Confirm clean worktree & branch**

Run: `cd /Users/aisenyc/savevia/.worktrees/python-ai-foundation && git status --porcelain && git branch --show-current`
Expected: only the two new docs files staged/committed from brainstorming; branch `feature/python-ai-foundation`.

- [ ] **Step 2: Merge main (verified conflict-free)**

Run: `git merge main -m "merge: bring Phase-5 infra + user MemoryController into feature branch"`
Expected: merge succeeds with no conflicts (main touched `deployment/docker-compose.production.yml`/`gateway application.yml`; feature touched only root `docker-compose.yml` + `savevia-ai/.env.example` — disjoint). If any conflict appears, STOP and resolve before continuing.

- [ ] **Step 3: Baseline test run**

Run: `cd savevia-ai && .venv/bin/python -m pytest -p no:cacheprovider -q -m "not live" --no-header 2>&1 | tail -5`
Expected: `302 passed, 10 skipped, 10 deselected` (the known-green baseline). If fewer pass, STOP — the merge broke something.

- [ ] **Step 4: No commit needed** (merge commit already created in Step 2).

---

## Phase C — Config & docs (fast, low-risk, do first)

### Task C.1: Add Flinks settings to `savevia-ai` config

**Files:**
- Modify: `savevia-ai/app/core/config.py`
- Modify: `savevia-ai/.env.example`
- Test: `savevia-ai/tests/test_config.py`

- [ ] **Step 1: Write the failing test** (append to `tests/test_config.py`)

```python
def test_flinks_settings_have_java_matching_defaults(monkeypatch):
    from app.core.config import Settings, reset_settings_cache
    reset_settings_cache()
    s = Settings()  # type: ignore[call-arg]
    assert s.flinks_api_url == "https://toolbox-api.private.fin.ag/v3"
    assert s.flinks_customer_id == "43387ca6-0391-4c82-857d-70d95f087ecb"
    assert s.flinks_iframe_url == "https://toolbox-iframe.private.fin.ag/"
    assert s.flinks_sandbox is True
    assert s.connection_max_per_month == 5
```

- [ ] **Step 2: Run to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_config.py::test_flinks_settings_have_java_matching_defaults -q`
Expected: FAIL (`AttributeError: ... 'flinks_api_url'`).

- [ ] **Step 3: Add fields to `Settings`** (in `config.py`, after the OpenAI block, before "Service identity")

```python
    # Flinks bank-data integration (defaults match Java FlinksService @Value)
    flinks_api_url: str = Field(
        default="https://toolbox-api.private.fin.ag/v3", alias="FLINKS_API_URL"
    )
    flinks_customer_id: str = Field(
        default="43387ca6-0391-4c82-857d-70d95f087ecb", alias="FLINKS_CUSTOMER_ID"
    )
    flinks_iframe_url: str = Field(
        default="https://toolbox-iframe.private.fin.ag/", alias="FLINKS_IFRAME_URL"
    )
    flinks_sandbox: bool = Field(default=True, alias="FLINKS_SANDBOX")
    connection_max_per_month: int = Field(
        default=5, alias="SAVEVIA_CONNECTION_MAX_PER_MONTH"
    )
```

- [ ] **Step 4: Mirror into `.env.example`** (append a Flinks block)

```
# Flinks bank-data integration (demo mode unless a real contract is configured)
FLINKS_API_URL=https://toolbox-api.private.fin.ag/v3
FLINKS_CUSTOMER_ID=43387ca6-0391-4c82-857d-70d95f087ecb
FLINKS_IFRAME_URL=https://toolbox-iframe.private.fin.ag/
FLINKS_SANDBOX=true
SAVEVIA_CONNECTION_MAX_PER_MONTH=5
```

- [ ] **Step 5: Run to verify pass**

Run: `.venv/bin/python -m pytest tests/test_config.py -q`
Expected: PASS (all config tests).

- [ ] **Step 6: Commit**

```bash
git add savevia-ai/app/core/config.py savevia-ai/.env.example savevia-ai/tests/test_config.py
git commit -m "feat(savevia-ai): Flinks settings + connection-cap config (Java parity defaults)"
```

### Task C.2: Add deploy env vars to `deployment/.env.template`

**Files:** Modify: `deployment/.env.template`

- [ ] **Step 1: Inspect current AI/share block**

Run: `grep -n "SAVEVIA_AI_URL\|SHARE_BASE_URL\|OPENAI_ENABLED" deployment/.env.template`
Expected: no `SAVEVIA_AI_URL`/`SHARE_BASE_URL` lines (the gap).

- [ ] **Step 2: Add the two vars** (insert after the existing `OPENAI_*` block, before the Flinks block at line ~52)

```
# Python AI service (savevia-ai) — gateway upstream + share link base
SAVEVIA_AI_URL=http://savevia-ai:8002
SHARE_BASE_URL=https://savevia.app
```

- [ ] **Step 3: Verify**

Run: `grep -n "SAVEVIA_AI_URL\|SHARE_BASE_URL" deployment/.env.template`
Expected: both present.

- [ ] **Step 4: Commit**

```bash
git add deployment/.env.template
git commit -m "chore(deploy): declare SAVEVIA_AI_URL + SHARE_BASE_URL in .env.template"
```

### Task C.3: Reconcile plan-05 / cutover-runbook to the "full port" end-state

**Files:**
- Modify: `docs/superpowers/plans/2026-05-23-plan-05-cutover.md`
- Modify: `docs/runbooks/cutover-runbook.md`

- [ ] **Step 1: Edit plan-05 Task 19** — change the P7 note so it reflects a full port: the `optimizer-bank` gateway route flips to `http://savevia-ai:8002` and `savevia-optimizer/` is deleted (remove any "Flinks stays on Java / trim dead code only" hedge). Add a sentence: *"These are cutover-time steps (Phase 6/7), executed after this round; the Flinks/bank endpoints are now ported to Python (see 2026-05-30 plan)."*

- [ ] **Step 2: Edit `cutover-runbook.md` T+7d section** — replace the "trim dead Java code (Flinks stays)" wording with "flip `optimizer-bank` route to Python; delete `savevia-optimizer/`". Keep it marked as deferred/cutover-day.

- [ ] **Step 3: Verify no remaining contradiction**

Run: `grep -rn "stays on Java\|trim dead\|Flinks.*Java" docs/superpowers/plans/2026-05-23-plan-05-cutover.md docs/runbooks/cutover-runbook.md`
Expected: no lines implying Flinks remains on Java permanently.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/plans/2026-05-23-plan-05-cutover.md docs/runbooks/cutover-runbook.md
git commit -m "docs: reconcile cutover plan/runbook to full Flinks port end-state"
```

---

## Phase A — Flinks / bank-connection port

> All new files under `savevia-ai/`. Run tests from `savevia-ai/`.

### Task A.1: Bank DTOs (schema)

**Files:**
- Create: `savevia-ai/app/modules/bank/__init__.py` (empty)
- Create: `savevia-ai/app/modules/bank/schema.py`
- Create: `savevia-ai/tests/modules/bank/__init__.py` (empty)
- Test: `savevia-ai/tests/modules/bank/test_schema.py`

- [ ] **Step 1: Write the failing test**

```python
from datetime import datetime
from decimal import Decimal


def test_bank_connection_dto_camelcase_and_datetime_format():
    from app.modules.bank.schema import BankAccountDTO, BankConnectionDTO

    dto = BankConnectionDTO(
        id=7,
        institution_name="TD Canada Trust",
        status="CONNECTED",
        last_sync_at=datetime(2026, 5, 30, 9, 8, 7),
        error_message=None,
        created_at=datetime(2026, 5, 1, 0, 0, 0),
        accounts=[
            BankAccountDTO(
                id=11, account_type="CREDIT_CARD", account_name="TD Cash Back Visa",
                account_number_masked="****1234", balance=Decimal("1234.50"),
                is_active=True,
            )
        ],
    )
    data = dto.model_dump(by_alias=True, mode="json")
    assert data["institutionName"] == "TD Canada Trust"
    assert data["lastSyncAt"] == "2026-05-30T09:08:07"   # no millis, no tz
    assert data["createdAt"] == "2026-05-01T00:00:00"
    assert data["accounts"][0]["accountNumberMasked"] == "****1234"
    assert data["accounts"][0]["isActive"] is True


def test_flinks_connect_request_parses_camelcase_body():
    from app.modules.bank.schema import FlinksConnectRequest

    req = FlinksConnectRequest.model_validate(
        {"loginId": "demo-abc", "institutionName": "TD", "userCardIds": [1, 2]}
    )
    assert req.login_id == "demo-abc"
    assert req.user_card_ids == [1, 2]
```

- [ ] **Step 2: Run to verify it fails**

Run: `.venv/bin/python -m pytest tests/modules/bank/test_schema.py -q`
Expected: FAIL (`ModuleNotFoundError: app.modules.bank.schema`).

- [ ] **Step 3: Implement `schema.py`**

```python
"""Bank-connection DTOs — wire parity with Java BankConnectionDTO /
FlinksConnectRequest. Datetimes serialize as `yyyy-MM-dd'T'HH:mm:ss`."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_serializer


def _camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


class _BankModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=_camel, populate_by_name=True, extra="ignore"
    )


class FlinksConnectRequest(_BankModel):
    login_id: str | None = None
    institution_name: str | None = None
    account_id: str | None = None
    user_card_ids: list[int] | None = None


class BankAccountDTO(_BankModel):
    id: int
    account_type: str | None = None
    account_name: str | None = None
    account_number_masked: str | None = None
    balance: Decimal | None = None
    is_active: bool | None = None


class BankConnectionDTO(_BankModel):
    id: int
    institution_name: str | None = None
    status: str | None = None
    last_sync_at: datetime | None = None
    error_message: str | None = None
    accounts: list[BankAccountDTO] = Field(default_factory=list)
    created_at: datetime | None = None

    @field_serializer("last_sync_at", "created_at", when_used="json")
    def _fmt_dt(self, dt: datetime | None) -> str | None:
        return dt.strftime("%Y-%m-%dT%H:%M:%S") if dt is not None else None
```

- [ ] **Step 4: Run to verify pass**

Run: `.venv/bin/python -m pytest tests/modules/bank/test_schema.py -q`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add savevia-ai/app/modules/bank/__init__.py savevia-ai/app/modules/bank/schema.py \
        savevia-ai/tests/modules/bank/__init__.py savevia-ai/tests/modules/bank/test_schema.py
git commit -m "feat(savevia-ai): bank-connection DTOs (camelCase + Java datetime format)"
```

### Task A.2: ConnectionLimit repository

**Files:**
- Create: `savevia-ai/app/repositories/connection_limit_repository.py`
- Test: `savevia-ai/tests/test_connection_limit_repository.py`

Translates `ConnectionLimitMapper`: `find_by_user_and_month`, `insert`, `update_connection_count`, `insert_history`. Mirror the integration-test gating used in `tests/test_transaction_repository.py` (skip unless `INTEGRATION_TESTS=1`), plus a signature smoke test that always runs.

- [ ] **Step 1: Write the failing test**

```python
import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("INTEGRATION_TESTS") != "1",
    reason="requires MySQL (set INTEGRATION_TESTS=1)",
)


def test_signatures_exist():
    from app.repositories.connection_limit_repository import ConnectionLimitRepository
    for m in ("find_by_user_and_month", "insert", "update_connection_count", "insert_history"):
        assert hasattr(ConnectionLimitRepository, m)
```

> Note: keep `test_signatures_exist` OUTSIDE the skip by moving `pytestmark` to only the integration tests. Simpler: put the signature test in its own module-level function and gate only DB tests with `@pytest.mark.skipif(...)` decorators. Follow the exact structure of `tests/test_transaction_repository.py`.

- [ ] **Step 2: Run to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_connection_limit_repository.py::test_signatures_exist -q`
Expected: FAIL (`ModuleNotFoundError`).

- [ ] **Step 3: Implement `connection_limit_repository.py`**

```python
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.connection_history import ConnectionHistory
from app.models.user_connection_limit import UserConnectionLimit
from app.repositories.base import BaseRepository


class ConnectionLimitRepository(BaseRepository[UserConnectionLimit]):
    """Async translation of ConnectionLimitMapper."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, UserConnectionLimit)

    async def find_by_user_and_month(
        self, user_id: int, year_month: str
    ) -> UserConnectionLimit | None:
        stmt = select(UserConnectionLimit).where(
            UserConnectionLimit.user_id == user_id,
            UserConnectionLimit.year_month == year_month,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def insert(self, limit: UserConnectionLimit) -> UserConnectionLimit:
        return await self.add(limit)

    async def update_connection_count(self, limit: UserConnectionLimit) -> int:
        stmt = (
            update(UserConnectionLimit)
            .where(UserConnectionLimit.id == limit.id)
            .values(connection_count=limit.connection_count)
        )
        result = await self.session.execute(stmt)
        return result.rowcount or 0

    async def insert_history(self, history: ConnectionHistory) -> ConnectionHistory:
        self.session.add(history)
        await self.session.flush()
        return history
```

- [ ] **Step 4: Run to verify pass**

Run: `.venv/bin/python -m pytest tests/test_connection_limit_repository.py -q`
Expected: PASS (signature test; DB tests skip without `INTEGRATION_TESTS=1`).

- [ ] **Step 5: Commit**

```bash
git add savevia-ai/app/repositories/connection_limit_repository.py savevia-ai/tests/test_connection_limit_repository.py
git commit -m "feat(savevia-ai): ConnectionLimitRepository (translates ConnectionLimitMapper)"
```

### Task A.3: BankConnection repository

**Files:**
- Create: `savevia-ai/app/repositories/bank_connection_repository.py`
- Test: `savevia-ai/tests/test_bank_connection_repository.py` (signature test always-on; DB tests gated)

Translates `BankConnectionMapper`: `find_by_user_id` (order by created_at desc), `find_by_id`, `find_by_user_and_login_id`, `find_by_user_and_institution`, `insert`, `update_status` (writes status, flinks_login_id, last_sync_at, error_message).

- [ ] **Step 1: Write the failing signature test**

```python
def test_signatures_exist():
    from app.repositories.bank_connection_repository import BankConnectionRepository
    for m in ("find_by_user_id", "find_by_id", "find_by_user_and_login_id",
              "find_by_user_and_institution", "insert", "update_status"):
        assert hasattr(BankConnectionRepository, m)
```

- [ ] **Step 2: Run to verify it fails** — `.venv/bin/python -m pytest tests/test_bank_connection_repository.py -q` → FAIL.

- [ ] **Step 3: Implement**

```python
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bank_connection import BankConnection
from app.repositories.base import BaseRepository


class BankConnectionRepository(BaseRepository[BankConnection]):
    """Async translation of BankConnectionMapper."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, BankConnection)

    async def find_by_user_id(self, user_id: int) -> list[BankConnection]:
        stmt = (
            select(BankConnection)
            .where(BankConnection.user_id == user_id)
            .order_by(BankConnection.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, connection_id: int) -> BankConnection | None:
        return await self.get_by_id(connection_id)

    async def find_by_user_and_login_id(
        self, user_id: int, login_id: str
    ) -> BankConnection | None:
        stmt = select(BankConnection).where(
            BankConnection.user_id == user_id,
            BankConnection.flinks_login_id == login_id,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def find_by_user_and_institution(
        self, user_id: int, institution_name: str
    ) -> BankConnection | None:
        stmt = select(BankConnection).where(
            BankConnection.user_id == user_id,
            BankConnection.institution_name == institution_name,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def insert(self, connection: BankConnection) -> BankConnection:
        return await self.add(connection)

    async def update_status(self, connection: BankConnection) -> int:
        stmt = (
            update(BankConnection)
            .where(BankConnection.id == connection.id)
            .values(
                status=connection.status,
                flinks_login_id=connection.flinks_login_id,
                last_sync_at=connection.last_sync_at,
                error_message=connection.error_message,
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount or 0
```

- [ ] **Step 4: Run to verify pass** — `.venv/bin/python -m pytest tests/test_bank_connection_repository.py -q` → PASS.

- [ ] **Step 5: Commit**

```bash
git add savevia-ai/app/repositories/bank_connection_repository.py savevia-ai/tests/test_bank_connection_repository.py
git commit -m "feat(savevia-ai): BankConnectionRepository (translates BankConnectionMapper)"
```

### Task A.4: BankAccount repository

**Files:**
- Create: `savevia-ai/app/repositories/bank_account_repository.py`
- Test: `savevia-ai/tests/test_bank_account_repository.py` (signature test)

Translates `BankAccountMapper`: `find_by_connection_id`, `insert`, `update` (balance + linked_card_id).

- [ ] **Step 1: Failing signature test**

```python
def test_signatures_exist():
    from app.repositories.bank_account_repository import BankAccountRepository
    for m in ("find_by_connection_id", "insert", "update"):
        assert hasattr(BankAccountRepository, m)
```

- [ ] **Step 2: Run to verify it fails** → FAIL.

- [ ] **Step 3: Implement**

```python
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bank_account import BankAccount
from app.repositories.base import BaseRepository


class BankAccountRepository(BaseRepository[BankAccount]):
    """Async translation of BankAccountMapper."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, BankAccount)

    async def find_by_connection_id(self, connection_id: int) -> list[BankAccount]:
        stmt = select(BankAccount).where(BankAccount.connection_id == connection_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def insert(self, account: BankAccount) -> BankAccount:
        return await self.add(account)

    async def update(self, account: BankAccount) -> int:
        stmt = (
            update(BankAccount)
            .where(BankAccount.id == account.id)
            .values(balance=account.balance, linked_card_id=account.linked_card_id)
        )
        result = await self.session.execute(stmt)
        return result.rowcount or 0
```

- [ ] **Step 4: Run to verify pass** → PASS.

- [ ] **Step 5: Commit**

```bash
git add savevia-ai/app/repositories/bank_account_repository.py savevia-ai/tests/test_bank_account_repository.py
git commit -m "feat(savevia-ai): BankAccountRepository (translates BankAccountMapper)"
```

### Task A.5: ConnectionLimit service

**Files:**
- Create: `savevia-ai/app/modules/connection_limits/__init__.py` (empty)
- Create: `savevia-ai/app/modules/connection_limits/service.py`
- Create: `savevia-ai/tests/modules/connection_limits/__init__.py` (empty)
- Test: `savevia-ai/tests/modules/connection_limits/test_service.py`

Port `ConnectionLimitService`. Month key = `yyyy-MM` from an **injectable** "today" callable (default `date.today`) so tests are deterministic. `UserConnectionLimit` has no `canConnect`/`remaining` methods in Python — compute inline: `remaining = max(max_connections - connection_count, 0)`, `can_connect = connection_count < max_connections`.

- [ ] **Step 1: Write the failing test**

```python
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock


def _limit(*, id=1, user_id=42, ym="2026-05", count=0, mx=5):
    return SimpleNamespace(
        id=id, user_id=user_id, year_month=ym,
        connection_count=count, max_connections=mx,
    )


def _service(repo, *, today=date(2026, 5, 30), default_max=5):
    from app.modules.connection_limits.service import ConnectionLimitService
    return ConnectionLimitService(
        repository=repo, default_max_connections=default_max, today=lambda: today,
    )


async def test_get_creates_row_when_absent():
    repo = AsyncMock()
    repo.find_by_user_and_month.return_value = None
    repo.insert.side_effect = lambda row: row
    svc = _service(repo)
    row = await svc.get_connection_limit(42)
    repo.find_by_user_and_month.assert_awaited_once_with(42, "2026-05")
    repo.insert.assert_awaited_once()
    assert row.year_month == "2026-05"
    assert row.max_connections == 5
    assert row.connection_count == 0


async def test_can_connect_true_until_cap():
    repo = AsyncMock()
    repo.find_by_user_and_month.return_value = _limit(count=4, mx=5)
    assert await _service(repo).can_connect(42) is True
    repo.find_by_user_and_month.return_value = _limit(count=5, mx=5)
    assert await _service(repo).can_connect(42) is False


async def test_record_connection_increments_and_logs_history():
    repo = AsyncMock()
    repo.find_by_user_and_month.return_value = _limit(count=2, mx=5)
    svc = _service(repo)
    ok = await svc.record_connection(42, "TD", "demo-x")
    assert ok is True
    repo.update_connection_count.assert_awaited_once()
    # history row written with action CONNECT
    hist = repo.insert_history.await_args.args[0]
    assert hist.action.value == "CONNECT"
    assert hist.user_id == 42


async def test_record_connection_refuses_when_at_cap():
    repo = AsyncMock()
    repo.find_by_user_and_month.return_value = _limit(count=5, mx=5)
    ok = await _service(repo).record_connection(42, "TD", "demo-x")
    assert ok is False
    repo.update_connection_count.assert_not_called()


async def test_record_disconnect_writes_history_only():
    repo = AsyncMock()
    await _service(repo).record_disconnect(42, "TD", "demo-x")
    hist = repo.insert_history.await_args.args[0]
    assert hist.action.value == "DISCONNECT"
    repo.update_connection_count.assert_not_called()
```

- [ ] **Step 2: Run to verify it fails** → FAIL (`ModuleNotFoundError`).

- [ ] **Step 3: Implement `service.py`**

```python
"""ConnectionLimitService — Python port of
com.savevia.optimizer.service.ConnectionLimitService.

Calendar-month quota keyed `yyyy-MM`. `today` is injectable for tests.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date

from app.core.logging import get_logger
from app.models.connection_history import ConnectionHistory, ConnectionHistoryAction
from app.models.user_connection_limit import UserConnectionLimit
from app.repositories.connection_limit_repository import ConnectionLimitRepository

_log = get_logger("savevia-ai.connection-limit")


class ConnectionLimitService:
    def __init__(
        self,
        *,
        repository: ConnectionLimitRepository,
        default_max_connections: int = 5,
        today: Callable[[], date] = date.today,
    ):
        self._repo = repository
        self._default_max = default_max_connections
        self._today = today

    def _current_year_month(self) -> str:
        return self._today().strftime("%Y-%m")

    async def get_connection_limit(self, user_id: int) -> UserConnectionLimit:
        ym = self._current_year_month()
        limit = await self._repo.find_by_user_and_month(user_id, ym)
        if limit is None:
            limit = UserConnectionLimit(
                user_id=user_id,
                year_month=ym,
                connection_count=0,
                max_connections=self._default_max,
            )
            await self._repo.insert(limit)
            _log.info("connection_limit_created", user_id=user_id, year_month=ym)
        return limit

    @staticmethod
    def _can(limit: UserConnectionLimit) -> bool:
        return (limit.connection_count or 0) < (limit.max_connections or 0)

    @staticmethod
    def _remaining(limit: UserConnectionLimit) -> int:
        return max((limit.max_connections or 0) - (limit.connection_count or 0), 0)

    async def can_connect(self, user_id: int) -> bool:
        return self._can(await self.get_connection_limit(user_id))

    async def get_remaining_connections(self, user_id: int) -> int:
        return self._remaining(await self.get_connection_limit(user_id))

    async def record_connection(
        self, user_id: int, institution_name: str, flinks_login_id: str | None
    ) -> bool:
        limit = await self.get_connection_limit(user_id)
        if not self._can(limit):
            _log.warning(
                "connection_limit_reached",
                user_id=user_id,
                used=limit.connection_count,
                max=limit.max_connections,
            )
            return False
        limit.connection_count = (limit.connection_count or 0) + 1
        await self._repo.update_connection_count(limit)
        await self._write_history(user_id, institution_name, flinks_login_id,
                                  ConnectionHistoryAction.CONNECT)
        return True

    async def record_disconnect(
        self, user_id: int, institution_name: str, flinks_login_id: str | None
    ) -> None:
        await self._write_history(user_id, institution_name, flinks_login_id,
                                  ConnectionHistoryAction.DISCONNECT)

    async def record_refresh(
        self, user_id: int, institution_name: str, flinks_login_id: str | None
    ) -> None:
        await self._write_history(user_id, institution_name, flinks_login_id,
                                  ConnectionHistoryAction.REFRESH)

    async def _write_history(
        self, user_id: int, institution_name: str, flinks_login_id: str | None,
        action: ConnectionHistoryAction,
    ) -> None:
        await self._repo.insert_history(
            ConnectionHistory(
                user_id=user_id,
                institution_name=institution_name,
                action=action,
                flinks_login_id=flinks_login_id,
            )
        )
```

- [ ] **Step 4: Run to verify pass** — `.venv/bin/python -m pytest tests/modules/connection_limits/test_service.py -q` → PASS (5).

- [ ] **Step 5: Commit**

```bash
git add savevia-ai/app/modules/connection_limits savevia-ai/tests/modules/connection_limits
git commit -m "feat(savevia-ai): ConnectionLimitService (month quota + history, injectable clock)"
```

### Task A.6: Flinks demo-data generator (seedable)

**Files:**
- Create: `savevia-ai/app/modules/flinks/__init__.py` (empty)
- Create: `savevia-ai/app/modules/flinks/demo_data.py`
- Create: `savevia-ai/tests/modules/flinks/__init__.py` (empty)
- Test: `savevia-ai/tests/modules/flinks/test_demo_data.py`

Port `generateMockAccountsData` + `generateMockDebitTransactions` + `generateMockCreditTransactions` (Java `FlinksService.java:467-584`). Inject a `random.Random` instance + a uuid factory so output is deterministic in tests. **Copy the mock data tables verbatim from the Java source** (credit-card mocks `:483-489`, debit table `:526-535`, credit table `:559-570`). Mirror Java exactly: debit txns use key `"Debit"`; credit txns ALSO use key `"Debit"` (Java bug-for-bug — see line 577); date = `now - randint(0, 89) days` ISO string; account ids include a short uuid suffix.

- [ ] **Step 1: Write the failing test**

```python
import random
from datetime import datetime


def _factory(seed: int = 7):
    from app.modules.flinks.demo_data import DemoDataGenerator
    rng = random.Random(seed)
    counter = {"n": 0}

    def fake_uuid() -> str:
        counter["n"] += 1
        return f"uuid{counter['n']:04d}"

    return DemoDataGenerator(rng=rng, uuid_factory=fake_uuid,
                             now=lambda: datetime(2026, 5, 30, 12, 0, 0))


def test_generate_accounts_is_deterministic_with_seed():
    a = _factory(7).generate_accounts_data()
    b = _factory(7).generate_accounts_data()
    assert a == b  # same seed → identical structure


def test_generate_accounts_has_one_chequing_plus_credit_cards():
    data = _factory(7).generate_accounts_data()
    accounts = data["Accounts"]
    types = [acc["Type"] for acc in accounts]
    assert types[0] == "Chequing"               # always first
    assert any(t == "Credit" for t in types)    # 1-2 credit cards
    assert 2 <= len(accounts) <= 3
    # every txn carries Id/Description/Debit/Date
    for acc in accounts:
        for txn in acc["Transactions"]:
            assert {"Id", "Description", "Debit", "Date"} <= set(txn)
```

- [ ] **Step 2: Run to verify it fails** → FAIL.

- [ ] **Step 3: Implement `demo_data.py`**

```python
"""Demo/sandbox account+transaction generator — port of FlinksService's
generateMock* helpers. Randomness is injected so tests are deterministic;
production passes a fresh random.Random() and uuid4."""

from __future__ import annotations

import random
import uuid
from collections.abc import Callable
from datetime import datetime, timezone

# Verbatim from FlinksService.java:483-489
_CREDIT_CARD_MOCKS = [
    ("demo-cc-001", "TD Cash Back Visa Infinite", "****1234"),
    ("demo-cc-002", "TD Aeroplan Visa Infinite", "****5678"),
    ("demo-cc-003", "RBC Avion Visa Infinite", "****9012"),
    ("demo-cc-004", "Scotiabank Scene+ Visa", "****3456"),
    ("demo-cc-005", "CIBC Dividend Visa Infinite", "****7890"),
]
# Verbatim from FlinksService.java:526-535 (description, amount, category-hint)
_DEBIT_MOCKS = [
    ("INTERAC PURCHASE - LOBLAWS #1234", "178.45"),
    ("INTERAC PURCHASE - PETRO-CANADA", "72.50"),
    ("INTERAC PURCHASE - SHOPPERS DRUG MART", "38.99"),
    ("INTERAC PURCHASE - COSTCO WHOLESALE", "285.67"),
    ("INTERAC PURCHASE - SHELL", "58.00"),
    ("INTERAC PURCHASE - SOBEYS", "112.30"),
    ("INTERAC PURCHASE - REXALL PHARMA", "25.50"),
    ("INTERAC PURCHASE - ESSO", "45.00"),
]
# Verbatim from FlinksService.java:559-570
_CREDIT_MOCKS = [
    ("UBER EATS", "25.99"),
    ("NETFLIX.COM", "16.99"),
    ("TIM HORTONS", "8.45"),
    ("AMAZON.CA", "89.99"),
    ("ROGERS WIRELESS", "85.00"),
    ("STARBUCKS", "6.75"),
    ("PRESTO", "20.00"),
    ("UBER", "18.50"),
    ("BOSTON PIZZA", "52.30"),
    ("SPOTIFY", "9.99"),
]


class DemoDataGenerator:
    def __init__(
        self,
        *,
        rng: random.Random | None = None,
        uuid_factory: Callable[[], str] | None = None,
        now: Callable[[], datetime] | None = None,
    ):
        self._rng = rng or random.Random()
        self._uuid = uuid_factory or (lambda: str(uuid.uuid4()))
        self._now = now or (lambda: datetime.now(timezone.utc))

    def _date(self) -> str:
        # Java: now.minusDays(rand.nextInt(90)).toString()
        from datetime import timedelta
        return (self._now() - timedelta(days=self._rng.randint(0, 89))).isoformat()

    def _debit_txns(self) -> list[dict]:
        # Java generates 5-8 then iterates min(n, table_len)
        n = min(5 + self._rng.randint(0, 3), len(_DEBIT_MOCKS))
        return [
            {"Id": f"demo-debit-{self._uuid()}", "Description": d, "Debit": amt,
             "Date": self._date()}
            for d, amt in _DEBIT_MOCKS[:n]
        ]

    def _credit_txns(self) -> list[dict]:
        n = min(6 + self._rng.randint(0, 4), len(_CREDIT_MOCKS))
        return [
            {"Id": f"demo-credit-{self._uuid()}", "Description": d, "Debit": amt,
             "Date": self._date()}
            for d, amt in _CREDIT_MOCKS[:n]
        ]

    def generate_accounts_data(self) -> dict:
        accounts: list[dict] = [
            {
                "Id": f"demo-chk-{self._uuid()[:8]}",
                "Type": "Chequing",
                "Title": "Chequing Account",
                "AccountNumber": f"****{1000 + self._rng.randint(0, 8999)}",
                "Balance": str(2000 + self._rng.randint(0, 7999)),
                "Transactions": self._debit_txns(),
            }
        ]
        num_cards = 1 + self._rng.randint(0, 1)
        chosen: list[int] = []
        while len(chosen) < num_cards and len(chosen) < len(_CREDIT_CARD_MOCKS):
            idx = self._rng.randint(0, len(_CREDIT_CARD_MOCKS) - 1)
            if idx not in chosen:
                chosen.append(idx)
        for idx in chosen:
            cid, title, masked = _CREDIT_CARD_MOCKS[idx]
            accounts.append({
                "Id": f"{cid}-{self._uuid()[:8]}",
                "Type": "Credit",
                "Title": title,
                "AccountNumber": masked,
                "Balance": str(500 + self._rng.randint(0, 2999)),
                "Transactions": self._credit_txns(),
            })
        return {"Accounts": accounts}
```

- [ ] **Step 4: Run to verify pass** → PASS (3).

- [ ] **Step 5: Commit**

```bash
git add savevia-ai/app/modules/flinks/__init__.py savevia-ai/app/modules/flinks/demo_data.py \
        savevia-ai/tests/modules/flinks/__init__.py savevia-ai/tests/modules/flinks/test_demo_data.py
git commit -m "feat(savevia-ai): Flinks demo-data generator (seedable, verbatim mock tables)"
```

### Task A.7: Flinks HTTP client (real path, inert)

**Files:**
- Create: `savevia-ai/app/modules/flinks/client.py`
- Test: `savevia-ai/tests/modules/flinks/test_client.py`

Port `authorizeWithFlinks` + `getAccountsDetail` real branches (Java `:198-290`) using httpx. Demo branch lives in the service (Task A.8), not the client. Client is only reached when `FLINKS_SANDBOX=false` and loginId not `demo-`. Use `respx` to test request shape; do NOT call the network.

- [ ] **Step 1: Write the failing test**

```python
import httpx
import respx


@respx.mock
async def test_authorize_posts_loginid_and_returns_request_id():
    from app.modules.flinks.client import FlinksClient

    base = "https://flinks.test/v3"
    cust = "cust-1"
    route = respx.post(f"{base}/{cust}/BankingServices/Authorize").mock(
        return_value=httpx.Response(200, json={"RequestId": "req-123"})
    )
    client = FlinksClient(base_url=base, customer_id=cust)
    rid = await client.authorize("login-xyz")
    assert rid == "req-123"
    assert route.called
    sent = route.calls.last.request
    assert b"login-xyz" in sent.content
    await client.aclose()
```

- [ ] **Step 2: Run to verify it fails** → FAIL.

- [ ] **Step 3: Implement `client.py`**

```python
"""Real Flinks Toolbox REST client. INERT in normal operation (no contract):
reached only when FLINKS_SANDBOX=false and loginId is not a demo id. Mirrors
FlinksService.authorizeWithFlinks + getAccountsDetail."""

from __future__ import annotations

import asyncio

import httpx

from app.core.logging import get_logger

_log = get_logger("savevia-ai.flinks")


class FlinksError(RuntimeError):
    pass


class FlinksClient:
    def __init__(self, *, base_url: str, customer_id: str,
                 client: httpx.AsyncClient | None = None):
        self._base = base_url.rstrip("/")
        self._customer = customer_id
        self._client = client or httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=5.0))

    async def authorize(self, login_id: str) -> str:
        url = f"{self._base}/{self._customer}/BankingServices/Authorize"
        resp = await self._client.post(url, json={"LoginId": login_id, "MostRecentCached": True})
        resp.raise_for_status()
        body = resp.json()
        request_id = body.get("RequestId")
        if not request_id:
            raise FlinksError("Failed to get RequestId from Flinks authorization")
        return request_id

    async def get_accounts_detail(self, request_id: str, *, max_retries: int = 10,
                                  sleep_seconds: float = 3.0) -> dict:
        url = f"{self._base}/{self._customer}/BankingServices/GetAccountsDetail"
        body = {"RequestId": request_id, "WithTransactions": True,
                "DaysOfTransactions": "Days90"}
        last_error: Exception | None = None
        for attempt in range(max_retries):
            try:
                resp = await self._client.post(url, json=body)
                if resp.status_code == 200:
                    data = resp.json()
                    if "Accounts" in data:
                        return data
            except Exception as e:  # noqa: BLE001 — mirror Java retry-on-any
                last_error = e
                _log.warning("flinks_attempt_failed", attempt=attempt + 1, error=str(e))
            await asyncio.sleep(sleep_seconds)
        raise FlinksError(f"Failed to retrieve bank data: {last_error or 'timeout'}")

    async def aclose(self) -> None:
        await self._client.aclose()
```

- [ ] **Step 4: Run to verify pass** → PASS.

- [ ] **Step 5: Commit**

```bash
git add savevia-ai/app/modules/flinks/client.py savevia-ai/tests/modules/flinks/test_client.py
git commit -m "feat(savevia-ai): inert Flinks REST client (authorize + poll GetAccountsDetail)"
```

### Task A.8: Flinks service (connect / refresh / force_refresh / persist)

**Files:**
- Create: `savevia-ai/app/modules/flinks/service.py`
- Test: `savevia-ai/tests/modules/flinks/test_service.py`

Port `FlinksService` orchestration (Java `:49-461`). Constructor injects: `bank_connection_repo`, `bank_account_repo`, `transaction_repo`, `categorization` (has `.categorize(name)`), `card_client` (`get_cards_batch`), `connection_limits` service, `demo_factory: Callable[[], DemoDataGenerator]`, `flinks_client_factory`, `sandbox: bool`. Methods: `connect_bank(user_id, request)`, `refresh_bank_data(connection)`, `force_refresh_bank_data(connection, user_card_ids)`, plus private `_fetch_flinks_data`, `_authorize`, `_get_accounts_detail`, `_save_or_update_account`, `_match_credit_card_to_user_card`, `_save_transactions`, `_map_account_type`, `_mask_account_number`.

Key parity rules (from Java):
- `_authorize`: if `sandbox` OR `login_id.startswith("demo-")` → return `"demo-request-" + uuid`. Else use `flinks_client_factory().authorize(login_id)`.
- `_get_accounts_detail`: if `request_id.startswith("demo-")` → `demo_factory().generate_accounts_data()`. Else `flinks_client.get_accounts_detail(request_id)`.
- `connect_bank`: dedup by login_id (→ REFRESHING + refresh + record_refresh), then by institution (→ same + update login_id), then limit check (raise `RuntimeError("LIMIT_EXCEEDED:...")`), create PENDING, fetch, on success CONNECTED + last_sync_at(utc now) + record_connection, on failure ERROR + error_message (do NOT count).
- `refresh_bank_data`: status→CONNECTED, error_message None, **no fetch, no last_sync_at write**.
- transaction amount = `Decimal(Debit)` if `Debit` present else `Decimal("-" + Credit)`; date parsed from first 19 chars; category via `categorization.categorize(merchant)`; `card_used_id` = account.linked_card_id only for CREDIT_CARD accounts; dedupe via `transaction_repo.find_by_account_and_flinks_id` (skip if non-empty).
- `_match_credit_card_to_user_card`: verbatim scoring (Java `:348-393`): bank-short-name gate, keyword length score for keywords ≥3 chars, type-hint bonuses, threshold `>= 3`. Card dict keys: `bank`, `name`, `id`.
- `_map_account_type` + `_mask_account_number`: verbatim (Java `:439-461`).

- [ ] **Step 1: Write the failing tests** (use AsyncMock repos + a seeded demo factory)

```python
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest


class _Cat:
    def categorize(self, name):  # deterministic stub
        return "DINING" if name and "UBER" in name.upper() else "OTHER"


def _demo_factory():
    import random
    from app.modules.flinks.demo_data import DemoDataGenerator
    c = {"n": 0}

    def u():
        c["n"] += 1
        return f"uuid{c['n']:04d}"

    return lambda: DemoDataGenerator(
        rng=random.Random(1), uuid_factory=u, now=lambda: datetime(2026, 5, 30),
    )


def _service(*, sandbox=True, conn_repo=None, acct_repo=None, txn_repo=None,
             card=None, limits=None):
    from app.modules.flinks.service import FlinksService
    return FlinksService(
        bank_connection_repo=conn_repo or AsyncMock(),
        bank_account_repo=acct_repo or AsyncMock(),
        transaction_repo=txn_repo or AsyncMock(),
        categorization=_Cat(),
        card_client=card or AsyncMock(),
        connection_limits=limits or AsyncMock(),
        demo_factory=_demo_factory(),
        flinks_client_factory=lambda: AsyncMock(),
        sandbox=sandbox,
    )


def _conn(**kw):
    base = dict(id=1, user_id=42, flinks_login_id="demo-x", institution_name="TD",
                status="PENDING", last_sync_at=None, error_message=None)
    base.update(kw)
    return SimpleNamespace(**base)


async def test_match_credit_card_scoring_threshold():
    svc = _service()
    cards = [{"id": 9, "bank": "TD", "name": "TD Cash Back Visa Infinite"}]
    matched = svc._match_credit_card_to_user_card(
        "TD Cash Back Visa Infinite", "TD Canada Trust", cards,
    )
    assert matched == 9
    # different bank → no match
    assert svc._match_credit_card_to_user_card(
        "TD Cash Back Visa", "RBC Royal Bank", cards,
    ) is None


async def test_map_account_type_and_mask():
    svc = _service()
    assert svc._map_account_type("Chequing") == "CHECKING"
    assert svc._map_account_type("Credit") == "CREDIT_CARD"
    assert svc._map_account_type(None) == "OTHER"
    assert svc._mask_account_number("123456789") == "****6789"
    assert svc._mask_account_number("12") == "****"


async def test_connect_existing_login_triggers_refresh_not_new_quota():
    conn_repo = AsyncMock()
    existing = _conn(status="CONNECTED")
    conn_repo.find_by_user_and_login_id.return_value = existing
    limits = AsyncMock()
    svc = _service(conn_repo=conn_repo, limits=limits)
    from app.modules.bank.schema import FlinksConnectRequest
    out = await svc.connect_bank(42, FlinksConnectRequest(login_id="demo-x", institution_name="TD"))
    assert out is existing
    limits.record_refresh.assert_awaited()        # refresh path
    limits.record_connection.assert_not_called()  # no new quota


async def test_connect_new_demo_saves_accounts_and_counts_quota():
    conn_repo = AsyncMock()
    conn_repo.find_by_user_and_login_id.return_value = None
    conn_repo.find_by_user_and_institution.return_value = None
    acct_repo = AsyncMock()
    acct_repo.find_by_connection_id.return_value = []
    txn_repo = AsyncMock()
    txn_repo.find_by_account_and_flinks_id.return_value = []
    limits = AsyncMock()
    limits.can_connect.return_value = True
    card = AsyncMock()
    card.get_cards_batch.return_value = [{"id": 9, "bank": "TD", "name": "TD Cash Back Visa Infinite"}]
    svc = _service(conn_repo=conn_repo, acct_repo=acct_repo, txn_repo=txn_repo,
                   limits=limits, card=card)

    from app.modules.bank.schema import FlinksConnectRequest
    conn_repo.insert.side_effect = lambda c: setattr(c, "id", 1) or c
    out = await svc.connect_bank(42, FlinksConnectRequest(
        login_id="demo-new", institution_name="TD", user_card_ids=[9],
    ))
    assert out.status == "CONNECTED"
    assert out.last_sync_at is not None
    limits.record_connection.assert_awaited_once()
    assert acct_repo.insert.await_count >= 1     # at least chequing + 1 cc
    assert txn_repo.insert.await_count >= 1       # transactions saved


async def test_connect_blocked_when_over_limit():
    conn_repo = AsyncMock()
    conn_repo.find_by_user_and_login_id.return_value = None
    conn_repo.find_by_user_and_institution.return_value = None
    limits = AsyncMock()
    limits.can_connect.return_value = False
    limits.get_remaining_connections.return_value = 0
    svc = _service(conn_repo=conn_repo, limits=limits)
    from app.modules.bank.schema import FlinksConnectRequest
    with pytest.raises(RuntimeError, match="LIMIT_EXCEEDED"):
        await svc.connect_bank(42, FlinksConnectRequest(login_id="demo-z", institution_name="TD"))


async def test_refresh_is_local_only_no_timestamp():
    conn_repo = AsyncMock()
    svc = _service(conn_repo=conn_repo)
    conn = _conn(status="REFRESHING", last_sync_at=None)
    await svc.refresh_bank_data(conn)
    assert conn.status == "CONNECTED"
    assert conn.last_sync_at is None              # NOT updated
    conn_repo.update_status.assert_awaited()
```

- [ ] **Step 2: Run to verify it fails** → FAIL.

- [ ] **Step 3: Implement `service.py`** — translate `FlinksService.java`. The non-mechanical core:

```python
"""FlinksService — Python port of com.savevia.optimizer.service.FlinksService.
Demo/sandbox is the live path; the real REST client is inert (no contract)."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from app.core.logging import get_logger
from app.models.bank_account import BankAccount
from app.models.bank_connection import BankConnection

if TYPE_CHECKING:
    from app.modules.bank.schema import FlinksConnectRequest

_log = get_logger("savevia-ai.flinks")


class FlinksService:
    def __init__(self, *, bank_connection_repo, bank_account_repo, transaction_repo,
                 categorization, card_client, connection_limits,
                 demo_factory: Callable[[], Any], flinks_client_factory: Callable[[], Any],
                 sandbox: bool):
        self._conn_repo = bank_connection_repo
        self._acct_repo = bank_account_repo
        self._txn_repo = transaction_repo
        self._cat = categorization
        self._card = card_client
        self._limits = connection_limits
        self._demo_factory = demo_factory
        self._flinks_client_factory = flinks_client_factory
        self._sandbox = sandbox

    async def connect_bank(self, user_id: int, request: "FlinksConnectRequest") -> BankConnection:
        existing = await self._conn_repo.find_by_user_and_login_id(user_id, request.login_id)
        if existing is not None:
            existing.status = "REFRESHING"
            await self._conn_repo.update_status(existing)
            await self.refresh_bank_data(existing)
            await self._limits.record_refresh(user_id, existing.institution_name,
                                              existing.flinks_login_id)
            return existing

        by_inst = await self._conn_repo.find_by_user_and_institution(
            user_id, request.institution_name)
        if by_inst is not None:
            by_inst.status = "REFRESHING"
            by_inst.flinks_login_id = request.login_id
            await self._conn_repo.update_status(by_inst)
            await self.refresh_bank_data(by_inst)
            await self._limits.record_refresh(user_id, by_inst.institution_name,
                                              by_inst.flinks_login_id)
            return by_inst

        if not await self._limits.can_connect(user_id):
            remaining = await self._limits.get_remaining_connections(user_id)
            _log.warning("connect_limit_reached", user_id=user_id, remaining=remaining)
            raise RuntimeError(
                "LIMIT_EXCEEDED:You have reached your monthly bank connection limit "
                "(5 per month). Please try again next month."
            )

        connection = BankConnection(
            user_id=user_id, flinks_login_id=request.login_id,
            institution_name=request.institution_name, status="PENDING",
        )
        await self._conn_repo.insert(connection)
        try:
            await self._fetch_flinks_data(connection, request.user_card_ids)
            connection.status = "CONNECTED"
            connection.last_sync_at = datetime.now(timezone.utc).replace(tzinfo=None)
            await self._limits.record_connection(user_id, request.institution_name,
                                                 request.login_id)
        except Exception as e:  # noqa: BLE001 — mirror Java
            _log.error("flinks_fetch_failed", error=str(e))
            connection.status = "ERROR"
            connection.error_message = str(e)
        await self._conn_repo.update_status(connection)
        return connection

    async def refresh_bank_data(self, connection: BankConnection) -> None:
        connection.status = "CONNECTED"
        connection.error_message = None
        await self._conn_repo.update_status(connection)

    async def force_refresh_bank_data(self, connection: BankConnection,
                                      user_card_ids: list[int] | None) -> None:
        try:
            await self._fetch_flinks_data(connection, user_card_ids)
            connection.status = "CONNECTED"
            connection.last_sync_at = datetime.now(timezone.utc).replace(tzinfo=None)
            connection.error_message = None
        except Exception as e:  # noqa: BLE001
            _log.error("flinks_force_refresh_failed", error=str(e))
            connection.status = "ERROR"
            connection.error_message = str(e)
        await self._conn_repo.update_status(connection)

    async def _authorize(self, login_id: str) -> str:
        if self._sandbox or login_id.startswith("demo-"):
            return f"demo-request-{uuid.uuid4()}"
        return await self._flinks_client_factory().authorize(login_id)

    async def _get_accounts_detail(self, request_id: str) -> dict:
        if request_id.startswith("demo-"):
            return self._demo_factory().generate_accounts_data()
        return await self._flinks_client_factory().get_accounts_detail(request_id)

    async def _fetch_flinks_data(self, connection: BankConnection,
                                 user_card_ids: list[int] | None) -> None:
        user_cards: list[dict] = []
        if user_card_ids:
            try:
                user_cards = await self._card.get_cards_batch(user_card_ids) or []
            except Exception as e:  # noqa: BLE001
                _log.warning("fetch_user_cards_failed", error=str(e))
        request_id = await self._authorize(connection.flinks_login_id)
        data = await self._get_accounts_detail(request_id)
        for account_data in data.get("Accounts", []) or []:
            await self._save_or_update_account(connection, account_data, user_cards)

    async def _save_or_update_account(self, connection, account_data, user_cards) -> None:
        flinks_account_id = account_data.get("Id")
        account_type = self._map_account_type(account_data.get("Type"))
        account_name = account_data.get("Title")
        existing = await self._acct_repo.find_by_connection_id(connection.id)
        account = next((a for a in existing if a.flinks_account_id == flinks_account_id), None)

        linked_card_id = None
        if account_type == "CREDIT_CARD" and user_cards:
            linked_card_id = self._match_credit_card_to_user_card(
                account_name, connection.institution_name, user_cards)

        if account is None:
            account = BankAccount(
                connection_id=connection.id, user_id=connection.user_id,
                flinks_account_id=flinks_account_id, account_type=account_type,
                account_name=account_name,
                account_number_masked=self._mask_account_number(account_data.get("AccountNumber")),
                institution_name=connection.institution_name, is_active=True,
                linked_card_id=linked_card_id,
            )
            await self._acct_repo.insert(account)
        elif linked_card_id is not None and account.linked_card_id is None:
            account.linked_card_id = linked_card_id

        balance = account_data.get("Balance")
        if balance is not None:
            account.balance = Decimal(str(balance))
            await self._acct_repo.update(account)

        await self._save_transactions(account, account_data.get("Transactions") or [])

    async def _save_transactions(self, account, transactions_data) -> None:
        from app.models.transaction import Transaction
        for txn_data in transactions_data:
            flinks_id = txn_data.get("Id")
            existing = await self._txn_repo.find_by_account_and_flinks_id(account.id, flinks_id)
            if existing:
                continue
            debit = txn_data.get("Debit")
            credit = txn_data.get("Credit")
            amount = Decimal(str(debit)) if debit is not None else Decimal("-" + str(credit))
            merchant = txn_data.get("Description")
            date_str = txn_data.get("Date")
            txn = Transaction(
                user_id=account.user_id, account_id=account.id,
                flinks_transaction_id=flinks_id, amount=amount,
                merchant=merchant, description=merchant,
                transaction_date=datetime.fromisoformat(date_str[:19]) if date_str else None,
                category=self._cat.categorize(merchant), is_analyzed=False,
            )
            if account.account_type == "CREDIT_CARD" and account.linked_card_id is not None:
                txn.card_used_id = account.linked_card_id
            await self._txn_repo.insert(txn)

    def _match_credit_card_to_user_card(self, account_name, institution_name, user_cards):
        # Verbatim port of FlinksService.java:348-393
        if not account_name or not institution_name:
            return None
        norm_name = account_name.upper()
        bank_short = institution_name.upper().split(" ")[0]
        best_match = None
        best_score = 0
        for card in user_cards:
            bank = (card.get("bank") or "").upper()
            if bank_short not in bank and bank not in bank_short:
                continue
            score = 0
            for kw in (card.get("name") or "").upper().split(" "):
                if len(kw) >= 3 and kw in norm_name:
                    score += len(kw)
            for hint, need in (("VISA", "VISA"), ("MASTERCARD", "MASTERCARD"),
                               ("AMEX", "AMEX"), ("CASHBACK", "CASH"), ("INFINITE", "INFINITE")):
                if hint in norm_name and need in (card.get("name") or "").upper():
                    score += 5
            if score > best_score:
                best_score = score
                best_match = card
        return best_match.get("id") if best_score >= 3 and best_match else None

    @staticmethod
    def _map_account_type(flinks_type: str | None) -> str:
        if not flinks_type:
            return "OTHER"
        return {
            "CHEQUING": "CHECKING", "CHECKING": "CHECKING", "SAVINGS": "SAVINGS",
            "CREDIT": "CREDIT_CARD", "CREDITCARD": "CREDIT_CARD",
            "LOC": "LINE_OF_CREDIT", "LINEOFCREDIT": "LINE_OF_CREDIT",
        }.get(flinks_type.upper(), "OTHER")

    @staticmethod
    def _mask_account_number(account_number: str | None) -> str:
        if not account_number or len(account_number) < 4:
            return "****"
        return "****" + account_number[-4:]
```

- [ ] **Step 4: Run to verify pass** — `.venv/bin/python -m pytest tests/modules/flinks/test_service.py -q` → PASS (6).

- [ ] **Step 5: Commit**

```bash
git add savevia-ai/app/modules/flinks/service.py savevia-ai/tests/modules/flinks/test_service.py
git commit -m "feat(savevia-ai): FlinksService port (connect/refresh/resync, demo+inert-real, card match)"
```

### Task A.9: Bank service (controller-level orchestration + DTO assembly)

**Files:**
- Create: `savevia-ai/app/modules/bank/service.py`
- Test: `savevia-ai/tests/modules/bank/test_service.py`

Holds `BankConnectionController` logic: `get_flinks_config`, `get_connection_limit`, `connect`, `get_connections`, `get_connection`, `refresh`, `resync`, `disconnect`, `_to_dto`. Owns owner-check semantics (return `None` → router emits 500 "Connection not found"). Constructed per-request from a session + injected `card_client`, `categorization`, `settings`.

- [ ] **Step 1: Write the failing tests** (AsyncMock the repos + flinks + limits via a builder seam)

```python
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock


def _acct(**kw):
    base = dict(id=11, account_type="CREDIT_CARD", account_name="TD Visa",
                account_number_masked="****1234", balance=Decimal("50.00"), is_active=True)
    base.update(kw)
    return SimpleNamespace(**base)


def _conn(**kw):
    base = dict(id=1, user_id=42, institution_name="TD", status="CONNECTED",
                last_sync_at=datetime(2026, 5, 30), error_message=None,
                created_at=datetime(2026, 5, 1), flinks_login_id="demo-x")
    base.update(kw)
    return SimpleNamespace(**base)


def _service(*, conn_repo=None, acct_repo=None, limits=None, flinks=None):
    from app.modules.bank.service import BankConnectionService
    svc = BankConnectionService.__new__(BankConnectionService)
    svc._conn_repo = conn_repo or AsyncMock()
    svc._acct_repo = acct_repo or AsyncMock()
    svc._limits = limits or AsyncMock()
    svc._flinks = flinks or AsyncMock()
    svc._customer_id = "cust-1"
    svc._iframe_url = "https://iframe/"
    svc._sandbox = True
    return svc


async def test_get_connection_returns_none_for_wrong_owner():
    conn_repo = AsyncMock()
    conn_repo.find_by_id.return_value = _conn(user_id=99)
    svc = _service(conn_repo=conn_repo)
    assert await svc.get_connection(42, 1) is None


async def test_to_dto_includes_accounts():
    acct_repo = AsyncMock()
    acct_repo.find_by_connection_id.return_value = [_acct()]
    svc = _service(acct_repo=acct_repo)
    dto = await svc._to_dto(_conn())
    assert dto.institution_name == "TD"
    assert dto.accounts[0].account_number_masked == "****1234"


async def test_disconnect_sets_status_and_records_history():
    conn_repo = AsyncMock()
    conn = _conn()
    conn_repo.find_by_id.return_value = conn
    acct_repo = AsyncMock()
    acct_repo.find_by_connection_id.return_value = []
    limits = AsyncMock()
    svc = _service(conn_repo=conn_repo, acct_repo=acct_repo, limits=limits)
    ok = await svc.disconnect(42, 1)
    assert ok is True
    assert conn.status == "DISCONNECTED"
    conn_repo.update_status.assert_awaited()
    limits.record_disconnect.assert_awaited_once()


async def test_resync_blocked_over_limit_returns_limit_error():
    conn_repo = AsyncMock()
    conn_repo.find_by_id.return_value = _conn()
    limits = AsyncMock()
    limits.can_connect.return_value = False
    svc = _service(conn_repo=conn_repo, limits=limits)
    result = await svc.resync(42, 1, user_card_ids=None)
    assert result == "LIMIT_EXCEEDED"
```

- [ ] **Step 2: Run to verify it fails** → FAIL.

- [ ] **Step 3: Implement `service.py`**

```python
"""BankConnectionService — port of BankConnectionController logic
(DTO assembly, owner checks, config, delegating to Flinks + ConnectionLimit)."""

from __future__ import annotations

from typing import Literal

from app.modules.bank.schema import BankAccountDTO, BankConnectionDTO, FlinksConnectRequest

ResyncResult = Literal["OK", "NOT_FOUND", "LIMIT_EXCEEDED"]


class BankConnectionService:
    def __init__(self, *, session, card_client, categorization, settings):
        from app.modules.connection_limits.service import ConnectionLimitService
        from app.modules.flinks.client import FlinksClient
        from app.modules.flinks.demo_data import DemoDataGenerator
        from app.modules.flinks.service import FlinksService
        from app.repositories.bank_account_repository import BankAccountRepository
        from app.repositories.bank_connection_repository import BankConnectionRepository
        from app.repositories.connection_limit_repository import ConnectionLimitRepository
        from app.repositories.transaction_repository import TransactionRepository

        self._conn_repo = BankConnectionRepository(session)
        self._acct_repo = BankAccountRepository(session)
        self._session = session
        self._customer_id = settings.flinks_customer_id
        self._iframe_url = settings.flinks_iframe_url
        self._sandbox = settings.flinks_sandbox
        self._limits = ConnectionLimitService(
            repository=ConnectionLimitRepository(session),
            default_max_connections=settings.connection_max_per_month,
        )
        self._flinks = FlinksService(
            bank_connection_repo=self._conn_repo,
            bank_account_repo=self._acct_repo,
            transaction_repo=TransactionRepository(session),
            categorization=categorization,
            card_client=card_client,
            connection_limits=self._limits,
            demo_factory=lambda: DemoDataGenerator(),
            flinks_client_factory=lambda: FlinksClient(
                base_url=settings.flinks_api_url, customer_id=settings.flinks_customer_id,
            ),
            sandbox=settings.flinks_sandbox,
        )

    async def get_flinks_config(self, user_id: int) -> dict:
        limit = await self._limits.get_connection_limit(user_id)
        full_iframe = self._iframe_url
        if self._customer_id:
            full_iframe = f"{self._iframe_url}?customerId={self._customer_id}"
        cfg = {
            "customerId": self._customer_id,
            "iframeUrl": self._iframe_url,
            "sandbox": self._sandbox,
            "connectUrl": full_iframe,
            "connectionLimit": self._limit_summary(limit),
        }
        await self._session.commit()
        return cfg

    async def get_connection_limit(self, user_id: int) -> dict:
        limit = await self._limits.get_connection_limit(user_id)
        out = {**self._limit_summary(limit), "yearMonth": limit.year_month}
        await self._session.commit()
        return out

    @staticmethod
    def _limit_summary(limit) -> dict:
        used = limit.connection_count or 0
        mx = limit.max_connections or 0
        return {"used": used, "max": mx, "remaining": max(mx - used, 0),
                "canConnect": used < mx}

    async def connect(self, user_id: int, request: FlinksConnectRequest) -> BankConnectionDTO:
        connection = await self._flinks.connect_bank(user_id, request)
        dto = await self._to_dto(connection)
        await self._session.commit()
        return dto

    async def get_connections(self, user_id: int) -> list[BankConnectionDTO]:
        rows = await self._conn_repo.find_by_user_id(user_id)
        return [await self._to_dto(r) for r in rows]

    async def get_connection(self, user_id: int, connection_id: int) -> BankConnectionDTO | None:
        conn = await self._conn_repo.find_by_id(connection_id)
        if conn is None or conn.user_id != user_id:
            return None
        return await self._to_dto(conn)

    async def refresh(self, user_id: int, connection_id: int) -> BankConnectionDTO | None:
        conn = await self._conn_repo.find_by_id(connection_id)
        if conn is None or conn.user_id != user_id:
            return None
        await self._flinks.refresh_bank_data(conn)
        dto = await self._to_dto(conn)
        await self._session.commit()
        return dto

    async def resync(self, user_id: int, connection_id: int,
                     *, user_card_ids: list[int] | None) -> ResyncResult | BankConnectionDTO:
        conn = await self._conn_repo.find_by_id(connection_id)
        if conn is None or conn.user_id != user_id:
            return "NOT_FOUND"
        if not await self._limits.can_connect(user_id):
            return "LIMIT_EXCEEDED"
        await self._flinks.force_refresh_bank_data(conn, user_card_ids)
        await self._limits.record_connection(user_id, conn.institution_name, conn.flinks_login_id)
        dto = await self._to_dto(conn)
        await self._session.commit()
        return dto

    async def disconnect(self, user_id: int, connection_id: int) -> bool:
        conn = await self._conn_repo.find_by_id(connection_id)
        if conn is None or conn.user_id != user_id:
            return False
        conn.status = "DISCONNECTED"
        await self._conn_repo.update_status(conn)
        await self._limits.record_disconnect(user_id, conn.institution_name, conn.flinks_login_id)
        await self._session.commit()
        return True

    async def _to_dto(self, connection) -> BankConnectionDTO:
        accounts = await self._acct_repo.find_by_connection_id(connection.id)
        return BankConnectionDTO(
            id=connection.id,
            institution_name=connection.institution_name,
            status=connection.status if isinstance(connection.status, str)
            else getattr(connection.status, "value", None),
            last_sync_at=connection.last_sync_at,
            error_message=connection.error_message,
            created_at=connection.created_at,
            accounts=[
                BankAccountDTO(
                    id=a.id, account_type=a.account_type, account_name=a.account_name,
                    account_number_masked=a.account_number_masked, balance=a.balance,
                    is_active=a.is_active,
                )
                for a in accounts
            ],
        )
```

> NOTE on `status`: the SQLAlchemy column maps to `BankConnectionStatus` enum on load but the service sets plain strings (`"CONNECTED"`). The `_to_dto` guard handles both.

- [ ] **Step 4: Run to verify pass** → PASS (4).

- [ ] **Step 5: Commit**

```bash
git add savevia-ai/app/modules/bank/service.py savevia-ai/tests/modules/bank/test_service.py
git commit -m "feat(savevia-ai): BankConnectionService (controller logic, DTO assembly, owner checks)"
```

### Task A.10: Bank router (8 endpoints)

**Files:**
- Create: `savevia-ai/app/modules/bank/router.py`
- Test: `savevia-ai/tests/modules/bank/test_router.py`

Factory `build_bank_router(get_card_client, get_categorization)` returning an `APIRouter(prefix="/api/v1/optimize/bank")`. Each handler: `Depends(get_db)` → construct `BankConnectionService(session, card_client, categorization, get_settings())`; parse `X-User-Id` (401 if missing); `Result` envelope via local `_ok`/`_error`. **Parity:** missing connection → `_error(500, "Connection not found")`; over-limit on resync → `_error(500, "LIMIT_EXCEEDED:Monthly connection limit reached (5/month). Please try again next month.")`; connect `RuntimeError("LIMIT_EXCEEDED:...")` → `_error(500, <message>)`.

- [ ] **Step 1: Write the failing tests** (mock the service via dependency seam, like `test_router.py` for transactions)

```python
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def app_and_service(monkeypatch):
    from fastapi import FastAPI

    from app.core.db import get_db
    from app.modules.bank import router as bank_router_mod

    service = AsyncMock()

    # Patch the service constructor used inside the router to return our mock.
    monkeypatch.setattr(bank_router_mod, "BankConnectionService",
                        lambda **kw: service)

    async def _fake_db():
        yield object()

    app = FastAPI()
    app.dependency_overrides[get_db] = _fake_db
    app.include_router(bank_router_mod.build_bank_router(
        get_card_client=lambda: AsyncMock(),
        get_categorization=lambda: object(),
    ))
    return app, service


@pytest.fixture
async def client(app_and_service):
    app, _ = app_and_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


async def test_connections_requires_user_id(client):
    resp = await client.get("/api/v1/optimize/bank/connections")
    assert resp.json()["code"] == 401


async def test_get_connection_not_found_is_500(client, app_and_service):
    _, service = app_and_service
    service.get_connection.return_value = None
    resp = await client.get("/api/v1/optimize/bank/connections/9",
                            headers={"X-User-Id": "42"})
    body = resp.json()
    assert body["code"] == 500
    assert body["message"] == "Connection not found"


async def test_connect_limit_exceeded_maps_to_500(client, app_and_service):
    _, service = app_and_service
    service.connect.side_effect = RuntimeError("LIMIT_EXCEEDED:You have reached ...")
    resp = await client.post("/api/v1/optimize/bank/connect",
                             headers={"X-User-Id": "42"},
                             json={"loginId": "demo-x", "institutionName": "TD"})
    body = resp.json()
    assert body["code"] == 500
    assert body["message"].startswith("LIMIT_EXCEEDED")


async def test_resync_over_limit_returns_limit_message(client, app_and_service):
    _, service = app_and_service
    service.resync.return_value = "LIMIT_EXCEEDED"
    resp = await client.post("/api/v1/optimize/bank/connections/9/resync",
                             headers={"X-User-Id": "42"}, json={})
    body = resp.json()
    assert body["code"] == 500
    assert "Monthly connection limit reached" in body["message"]


async def test_flinks_config_ok(client, app_and_service):
    _, service = app_and_service
    service.get_flinks_config.return_value = {"customerId": "c", "sandbox": True}
    resp = await client.get("/api/v1/optimize/bank/flinks-config",
                            headers={"X-User-Id": "42"})
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["customerId"] == "c"
```

- [ ] **Step 2: Run to verify it fails** → FAIL.

- [ ] **Step 3: Implement `router.py`**

```python
"""Bank-connection router — /api/v1/optimize/bank/** (Java parity)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_db
from app.modules.bank.schema import FlinksConnectRequest
from app.modules.bank.service import BankConnectionService

_LIMIT_MSG = ("LIMIT_EXCEEDED:Monthly connection limit reached (5/month). "
              "Please try again next month.")


def _ok(data: object | None) -> dict:
    return {"code": 200, "message": "success", "data": data, "timestamp": 0}


def _error(code: int, message: str) -> dict:
    return {"code": code, "message": message, "data": None, "timestamp": 0}


def _parse_user_id(raw: str | None) -> int | None:
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def build_bank_router(
    get_card_client: Callable[[], Any],
    get_categorization: Callable[[], Any],
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/optimize/bank", tags=["bank"])

    def _svc(session: AsyncSession) -> BankConnectionService:
        return BankConnectionService(
            session=session, card_client=get_card_client(),
            categorization=get_categorization(), settings=get_settings(),
        )

    @router.get("/flinks-config")
    async def flinks_config(
        x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
        session: AsyncSession = Depends(get_db),
    ):
        uid = _parse_user_id(x_user_id)
        if uid is None:
            return _error(401, "User not authenticated")
        return _ok(await _svc(session).get_flinks_config(uid))

    @router.get("/connection-limit")
    async def connection_limit(
        x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
        session: AsyncSession = Depends(get_db),
    ):
        uid = _parse_user_id(x_user_id)
        if uid is None:
            return _error(401, "User not authenticated")
        return _ok(await _svc(session).get_connection_limit(uid))

    @router.post("/connect")
    async def connect(
        body: FlinksConnectRequest = Body(...),
        x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
        session: AsyncSession = Depends(get_db),
    ):
        uid = _parse_user_id(x_user_id)
        if uid is None:
            return _error(401, "User not authenticated")
        try:
            dto = await _svc(session).connect(uid, body)
        except RuntimeError as e:
            return _error(500, str(e))
        return _ok(dto.model_dump(by_alias=True, mode="json"))

    @router.get("/connections")
    async def connections(
        x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
        session: AsyncSession = Depends(get_db),
    ):
        uid = _parse_user_id(x_user_id)
        if uid is None:
            return _error(401, "User not authenticated")
        dtos = await _svc(session).get_connections(uid)
        return _ok([d.model_dump(by_alias=True, mode="json") for d in dtos])

    @router.get("/connections/{connection_id}")
    async def connection(
        connection_id: int,
        x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
        session: AsyncSession = Depends(get_db),
    ):
        uid = _parse_user_id(x_user_id)
        if uid is None:
            return _error(401, "User not authenticated")
        dto = await _svc(session).get_connection(uid, connection_id)
        if dto is None:
            return _error(500, "Connection not found")
        return _ok(dto.model_dump(by_alias=True, mode="json"))

    @router.post("/connections/{connection_id}/refresh")
    async def refresh(
        connection_id: int,
        x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
        session: AsyncSession = Depends(get_db),
    ):
        uid = _parse_user_id(x_user_id)
        if uid is None:
            return _error(401, "User not authenticated")
        dto = await _svc(session).refresh(uid, connection_id)
        if dto is None:
            return _error(500, "Connection not found")
        return _ok(dto.model_dump(by_alias=True, mode="json"))

    @router.post("/connections/{connection_id}/resync")
    async def resync(
        connection_id: int,
        body: dict | None = Body(default=None),
        x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
        session: AsyncSession = Depends(get_db),
    ):
        uid = _parse_user_id(x_user_id)
        if uid is None:
            return _error(401, "User not authenticated")
        user_card_ids = None
        if body and body.get("userCardIds") is not None:
            user_card_ids = [int(x) for x in body["userCardIds"]]
        result = await _svc(session).resync(uid, connection_id, user_card_ids=user_card_ids)
        if result == "NOT_FOUND":
            return _error(500, "Connection not found")
        if result == "LIMIT_EXCEEDED":
            return _error(500, _LIMIT_MSG)
        return _ok(result.model_dump(by_alias=True, mode="json"))

    @router.delete("/connections/{connection_id}")
    async def disconnect(
        connection_id: int,
        x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
        session: AsyncSession = Depends(get_db),
    ):
        uid = _parse_user_id(x_user_id)
        if uid is None:
            return _error(401, "User not authenticated")
        ok = await _svc(session).disconnect(uid, connection_id)
        if not ok:
            return _error(500, "Connection not found")
        return _ok(None)

    return router
```

- [ ] **Step 4: Run to verify pass** → PASS (5).

- [ ] **Step 5: Commit**

```bash
git add savevia-ai/app/modules/bank/router.py savevia-ai/tests/modules/bank/test_router.py
git commit -m "feat(savevia-ai): bank router (8 endpoints, Result-500 parity for errors)"
```

### Task A.11: Wire bank router into the app

**Files:**
- Modify: `savevia-ai/app/main.py`
- Test: `savevia-ai/tests/modules/bank/test_wiring.py`

- [ ] **Step 1: Write the failing test**

```python
async def test_bank_routes_registered():
    from app.main import create_app
    app = create_app()
    paths = {r.path for r in app.routes}
    assert "/api/v1/optimize/bank/connections" in paths
    assert "/api/v1/optimize/bank/connect" in paths
    assert "/api/v1/optimize/bank/flinks-config" in paths
```

- [ ] **Step 2: Run to verify it fails** → FAIL (routes absent).

- [ ] **Step 3: Wire in `main.py`** — add import and `include_router`:

```python
# add near other module imports
from app.modules.bank.router import build_bank_router

# inside create_app(), after the transactions router include:
    app.include_router(build_bank_router(
        get_card_client=lambda: app.state.card_client,
        get_categorization=lambda: app.state.categorization_service,
    ))
```

- [ ] **Step 4: Run to verify pass** → PASS.

- [ ] **Step 5: Full regression checkpoint**

Run: `.venv/bin/python -m pytest -p no:cacheprovider -q -m "not live" --no-header 2>&1 | tail -3`
Expected: previous count + all new bank/connection/flinks tests pass; 0 failures.

- [ ] **Step 6: Commit**

```bash
git add savevia-ai/app/main.py savevia-ai/tests/modules/bank/test_wiring.py
git commit -m "feat(savevia-ai): wire bank router into FastAPI app (Phase 4 endpoints complete)"
```

---

## Phase B — AI per-recommendation explanations

### Task B.1: Explanations helper (port OpenAiService.generateExplanations)

**Files:**
- Create: `savevia-ai/app/modules/optimizer_api/explanations.py`
- Test: `savevia-ai/tests/modules/optimizer_api/test_explanations.py`

Port `OpenAiService` (Java `service/OpenAiService.java`): `generate_explanations(recommendations, user_cards, locale)` mutates each `CategoryRecommendation.ai_explanation`. Use `langchain_openai.ChatOpenAI` (already a dep) with `model=settings.openai_model`, `temperature=0.8`. **Copy the system message + single-category prompt + language instruction verbatim** from Java `OpenAiService.buildSystemMessage` (`:127-156`), `buildSinglePrompt` (`:187-246`), `getLanguageInstruction` (`:171-184`). Concurrency: `asyncio.gather` across categories, bounded by a semaphore (e.g. 5). Inject the chat model factory for testability (default builds `ChatOpenAI`). Swallow per-item errors (leave explanation empty), matching Java.

- [ ] **Step 1: Write the failing test** (mocked model — no spend)

```python
from decimal import Decimal
from unittest.mock import AsyncMock


def _rec(category="DINING"):
    from app.modules.optimizer_api.schema import CategoryRecommendation
    return CategoryRecommendation(
        category=category, monthly_spend=Decimal("200"),
        recommended_card={"id": 1, "bank": "TD", "name": "TD Cash Back Visa"},
        reward_rate=Decimal("0.04"), monthly_reward=Decimal("8.00"),
    )


async def test_generate_explanations_fills_ai_explanation():
    from app.modules.optimizer_api.explanations import ExplanationGenerator

    fake_model = AsyncMock()
    fake_model.ainvoke.return_value = type("M", (), {"content": "Use TD for dining."})()
    gen = ExplanationGenerator(model_factory=lambda: fake_model)

    recs = [_rec("DINING"), _rec("GROCERY")]
    await gen.generate_explanations(recs, user_cards=[{"id": 1, "bank": "TD", "name": "TD Cash Back Visa"}], locale="en")
    assert recs[0].ai_explanation == "Use TD for dining."
    assert recs[1].ai_explanation == "Use TD for dining."
    assert fake_model.ainvoke.await_count == 2


async def test_generate_explanations_swallows_errors():
    from app.modules.optimizer_api.explanations import ExplanationGenerator

    fake_model = AsyncMock()
    fake_model.ainvoke.side_effect = RuntimeError("openai down")
    gen = ExplanationGenerator(model_factory=lambda: fake_model)
    recs = [_rec("DINING")]
    await gen.generate_explanations(recs, user_cards=[], locale="en")  # must not raise
    assert recs[0].ai_explanation is None
```

- [ ] **Step 2: Run to verify it fails** → FAIL.

- [ ] **Step 3: Implement `explanations.py`** — structure below; fill the prompt strings verbatim from the cited Java methods.

```python
"""ExplanationGenerator — port of OpenAiService.generateExplanations.
Per-recommendation, locale-aware LLM explanations. Errors are swallowed
(explanation stays empty), matching Java behavior."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from app.core.config import get_settings
from app.core.logging import get_logger

if TYPE_CHECKING:
    from app.modules.optimizer_api.schema import CategoryRecommendation

_log = get_logger("savevia-ai.explanations")
_MAX_CONCURRENCY = 5


def _default_model_factory() -> Any:
    from langchain_openai import ChatOpenAI
    s = get_settings()
    return ChatOpenAI(model=s.openai_model, temperature=0.8, api_key=s.openai_api_key)


class ExplanationGenerator:
    def __init__(self, *, model_factory: Callable[[], Any] = _default_model_factory):
        self._model_factory = model_factory

    async def generate_explanations(
        self, recommendations: list["CategoryRecommendation"],
        user_cards: list[dict], locale: str | None,
    ) -> None:
        if not recommendations:
            return
        model = self._model_factory()
        sem = asyncio.Semaphore(_MAX_CONCURRENCY)
        system = self._build_system_message(locale)

        async def _one(rec: "CategoryRecommendation") -> None:
            async with sem:
                try:
                    prompt = self._build_single_prompt(rec, user_cards)
                    msg = await model.ainvoke(
                        [{"role": "system", "content": system},
                         {"role": "user", "content": prompt}]
                    )
                    rec.ai_explanation = (msg.content or "").strip() or None
                except Exception as e:  # noqa: BLE001 — mirror Java swallow
                    _log.warning("explanation_failed", category=rec.category, error=str(e))

        await asyncio.gather(*(_one(r) for r in recommendations))

    def _build_system_message(self, locale: str | None) -> str:
        # VERBATIM from OpenAiService.buildSystemMessage (:127-156) +
        # getLanguageInstruction (:171-184). Reproduce the exact strings.
        ...

    def _build_single_prompt(self, rec: "CategoryRecommendation", user_cards: list[dict]) -> str:
        # VERBATIM from OpenAiService.buildSinglePrompt (:187-246), using
        # rec.category / rec.monthly_spend / rec.recommended_card / rec.reward_rate.
        ...
```

> The two `...` bodies MUST be filled with the exact prompt text from the cited Java lines during implementation (read the file, translate string-for-string). Do not paraphrase — Risk #2 in the spec is prompt drift.

- [ ] **Step 4: Run to verify pass** → PASS (2).

- [ ] **Step 5: Commit**

```bash
git add savevia-ai/app/modules/optimizer_api/explanations.py savevia-ai/tests/modules/optimizer_api/test_explanations.py
git commit -m "feat(savevia-ai): AI explanation generator (verbatim OpenAiService prompts)"
```

### Task B.2: Wire explanations into the optimizer service

**Files:**
- Modify: `savevia-ai/app/modules/optimizer_api/service.py` (constructor + the AI block at `:133-154`)
- Modify: `savevia-ai/app/main.py` (pass generator into `CashbackOptimizerService`)
- Test: `savevia-ai/tests/modules/optimizer_api/test_service.py` (add a case)

- [ ] **Step 1: Write the failing test** (extend the existing service test)

```python
async def test_ai_explanations_fill_recommendation_when_allowed(clients):
    from unittest.mock import AsyncMock

    from app.modules.optimizer_api.schema import OptimizationRequest

    card, user = clients
    card.get_cards_batch.return_value = [_card(id=1, name="A", base="0.02")]
    user.check_can_use_ai.return_value = True

    gen = AsyncMock()
    async def _fill(recs, **kw):
        for r in recs:
            r.ai_explanation = "explained"
    gen.generate_explanations.side_effect = _fill

    from app.modules.optimizer_api.service import CashbackOptimizerService
    svc = CashbackOptimizerService(card_client=card, user_client=user, explanation_generator=gen)
    result = await svc.optimize(OptimizationRequest(
        user_id=42, card_ids=[1], monthly_spending={"DINING": Decimal("100")},
        enable_ai_explanation=True,
    ))
    assert result.recommendations[0].ai_explanation == "explained"
    user.record_ai_usage.assert_awaited_once_with(user_id=42)
```

- [ ] **Step 2: Run to verify it fails** → FAIL (constructor has no `explanation_generator`).

- [ ] **Step 3: Modify `service.py`** — add optional `explanation_generator` param (default `None`); in the AI block, when `allowed`, call it before recording usage:

```python
    def __init__(self, *, card_client, user_client, explanation_generator=None):
        self._card = card_client
        self._user = user_client
        self._explanations = explanation_generator
```

Replace the `# TODO(plan-04 follow-up)` lines with:

```python
                    if self._explanations is not None:
                        await self._explanations.generate_explanations(
                            recommendations, user_cards=user_cards, locale=request.locale,
                        )
                    try:
                        await self._user.record_ai_usage(user_id=request.user_id)
                    except JavaServiceError as e:
                        _log.warning("record_ai_usage_failed", error=e.message)
```

Also remove the now-stale "deferred" note in the module docstring (`:7-10`).

- [ ] **Step 4: Wire in `main.py`** — construct + inject:

```python
from app.modules.optimizer_api.explanations import ExplanationGenerator
# ...
    app.state.optimizer_service = CashbackOptimizerService(
        card_client=app.state.card_client,
        user_client=app.state.user_client,
        explanation_generator=ExplanationGenerator(),
    )
```

- [ ] **Step 5: Run to verify pass**

Run: `.venv/bin/python -m pytest tests/modules/optimizer_api/ -q`
Expected: PASS (all existing + the new case).

- [ ] **Step 6: Commit**

```bash
git add savevia-ai/app/modules/optimizer_api/service.py savevia-ai/app/main.py savevia-ai/tests/modules/optimizer_api/test_service.py
git commit -m "feat(savevia-ai): wire AI explanations into /optimize/calculate (remove deferred TODO)"
```

---

## Phase D — Real regression

### Task D.1: Expand memory-quality fixtures to 20+

**Files:**
- Modify: `savevia-ai/tests/modules/memory/fixtures/sample_conversations.json`

- [ ] **Step 1: Inspect current count**

Run: `cd savevia-ai && .venv/bin/python -c "import json;print(len(json.load(open('tests/modules/memory/fixtures/sample_conversations.json'))))"`
Expected: `10`.

- [ ] **Step 2: Add 10+ new cases** following the existing object shape (read one entry first to match keys exactly: conversation messages + expected extracted facts/recommendations). Cover spending patterns, lifestyle facts, card preferences, travel, dining, multi-fact conversations. Keep them realistic and in the same schema.

- [ ] **Step 3: Verify count + schema loads**

Run: `.venv/bin/python -c "import json;d=json.load(open('tests/modules/memory/fixtures/sample_conversations.json'));print(len(d));assert len(d)>=20"`
Expected: `>= 20`, no JSON error.

- [ ] **Step 4: Confirm the quality test still collects**

Run: `.venv/bin/python -m pytest tests/modules/memory/test_extraction_quality.py --collect-only -q | tail -3`
Expected: collects (will skip without `-m live`).

- [ ] **Step 5: Commit**

```bash
git add savevia-ai/tests/modules/memory/fixtures/sample_conversations.json
git commit -m "test(savevia-ai): expand memory-quality fixtures to 20+ conversations"
```

### Task D.2: Run the memory-quality live regression

**Files:** none (records a result).

- [ ] **Step 1: Confirm OpenAI key present**

Run: `cd /Users/aisenyc/savevia && grep -q "OPENAI_API_KEY=..*[A-Za-z0-9]" .env && echo HAVE_KEY`
Expected: `HAVE_KEY`. Export it for the test env: `export OPENAI_API_KEY=$(grep '^OPENAI_API_KEY=' .env | cut -d= -f2-)`.

- [ ] **Step 2: Run the live quality test**

Run: `cd savevia-ai && OPENAI_API_KEY="$OPENAI_API_KEY" .venv/bin/python -m pytest tests/modules/memory/test_extraction_quality.py -m live -q 2>&1 | tail -20`
Expected: PASS with ≥80% match ratio. If it FAILS on threshold, capture the measured ratio and the diverging cases; fix obvious fixture mistakes (not the prompt) and re-run. If it's a genuine model-quality gap, record the number and report — do not weaken the assertion silently.

- [ ] **Step 3: Record the result** in the commit message of the next doc/commit (measured ratio + date). No code commit if nothing changed.

### Task D.3: Boot the Java stack & capture SSE fixtures

**Files:**
- Create: `savevia-ai/tests/fixtures/sse_replay/cases.json` (populated)
- Create: `savevia-ai/tests/fixtures/sse_replay/<case-id>.expected.json` (per case)
- Possibly create: `savevia-ai/scripts/capture_java_sse.py` (capture helper)

- [ ] **Step 1: Read the regression contract** — open `tests/modules/chat/test_sse_regression.py` and `tests/fixtures/sse_replay/README.md` to learn the exact `cases.json` schema, the normalization (event-name sequence + tool-call set + done/error framing, content deltas dropped), and the 10 canonical prompt ids.

- [ ] **Step 2: Bring up the Java stack** (MySQL/Redis already up via Docker)

Run (from repo root, background each): start `savevia-eureka`, then `savevia-card`, `savevia-user`, `savevia-optimizer` from the built jars (use `restart-backend.sh` if it works in this env, else `java -jar savevia-<svc>/target/*.jar` with the right `--spring.profiles`/env).
Expected: optimizer health (`curl localhost:8083/actuator/health` or the service's health path) returns UP; eureka shows card+user+optimizer registered. **If the stack cannot boot cleanly here, STOP this task, record which services failed and why, and proceed to the fallback in Step 5.**

- [ ] **Step 3: Seed a known user + cards** and capture SSE for the 10 prompts

Run a capture script that POSTs each canonical prompt to Java `POST /api/v1/chat/stream` (through gateway or direct to 8083 with `X-User-Id`), saving the raw SSE. Normalize each stream to the event-structure shape the regression expects; write `cases.json` + `<case-id>.expected.json`.

- [ ] **Step 4: Tear down the Java stack** (stop the 4 Java services; leave MySQL/Redis).

- [ ] **Step 5 (fallback if Step 2 failed):** record whatever subset booted; for unreachable cases, document the exact capture procedure in `tests/fixtures/sse_replay/README.md` and leave those cases out of `cases.json`. Never fabricate expected output.

- [ ] **Step 6: Commit** the captured fixtures (or the documented partial + procedure)

```bash
git add savevia-ai/tests/fixtures/sse_replay/ savevia-ai/scripts/capture_java_sse.py
git commit -m "test(savevia-ai): record Java SSE structure fixtures for regression"
```

### Task D.4: Flip the SSE regression to assert and run

**Files:**
- Modify: `savevia-ai/tests/modules/chat/test_sse_regression.py`

- [ ] **Step 1: Replace the skip guard** — change `@pytest.mark.skipif(not CASES, ...)` so that, when `cases.json` is non-empty, the parametrized test runs and asserts the Python serializer reproduces each case's event structure. Keep a skip ONLY for cases explicitly marked pending in `cases.json` (fallback partial).

- [ ] **Step 2: Run the regression**

Run: `cd savevia-ai && .venv/bin/python -m pytest tests/modules/chat/test_sse_regression.py -q 2>&1 | tail -15`
Expected: the recorded cases PASS (assert structure matches); pending cases (if any) skip with a clear reason.

- [ ] **Step 3: Commit**

```bash
git add savevia-ai/tests/modules/chat/test_sse_regression.py
git commit -m "test(savevia-ai): assert SSE event structure vs recorded Java fixtures"
```

---

## Final gate

### Task Z.1: Full suite green + summary

- [ ] **Step 1: Run the non-live suite**

Run: `cd savevia-ai && .venv/bin/python -m pytest -p no:cacheprovider -q -m "not live" --no-header 2>&1 | tail -3`
Expected: `0 failed`. Count = 302 baseline + all new tests (schema, repos, connection_limits, flinks demo/client/service, bank service/router/wiring, explanations, plus the now-asserting SSE cases).

- [ ] **Step 2: Confirm no stale TODO**

Run: `grep -rn "generateExplanations\|plan-04 follow-up\|TODO" savevia-ai/app/modules/optimizer_api/`
Expected: no `plan-04 follow-up` TODO remains.

- [ ] **Step 3: Confirm bank endpoints exist end-to-end**

Run: `.venv/bin/python -c "from app.main import create_app; app=create_app(); print(sorted(r.path for r in app.routes if '/bank' in r.path))"`
Expected: all 8 `/api/v1/optimize/bank/**` paths listed.

- [ ] **Step 4: Final commit (if any pending changes)** — otherwise the work is already committed task-by-task.

---

## Self-Review (run after writing — completed)

**Spec coverage:** A (Tasks A.1–A.11) ⇒ spec §4; B (B.1–B.2) ⇒ §5; C (C.1–C.3) ⇒ §6; D (D.1–D.4) ⇒ §7; Step 0 ⇒ §3. DoD items in §11 each map to a task (bank endpoints→A.10/A.11; connection-limit→A.5; flinks demo/real→A.6/A.7/A.8; ai_explanation→B.1/B.2; .env→C.2; docs→C.3; memory live→D.1/D.2; SSE→D.3/D.4; full green→Z.1).

**Placeholder scan:** the only intentional `...` are the two prompt bodies in B.1, each annotated "VERBATIM from <Java file:line>, fill during implementation" with a drift warning — acceptable because the exact strings live in the cited source and must be copied, not invented.

**Type consistency:** `BankConnectionService` methods (`connect/get_connections/get_connection/refresh/resync/disconnect/get_flinks_config/get_connection_limit/_to_dto`) are used identically in router (A.10) and tests (A.9/A.10). `FlinksService` method names (`connect_bank/refresh_bank_data/force_refresh_bank_data`) consistent across A.8 and A.9. `ConnectionLimitService` (`get_connection_limit/can_connect/get_remaining_connections/record_connection/record_disconnect/record_refresh`) consistent A.5↔A.8↔A.9. `ExplanationGenerator.generate_explanations(recommendations, user_cards, locale)` consistent B.1↔B.2. Repos match the `BaseRepository` pattern + the Java mapper method names.

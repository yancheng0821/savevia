"""Bank-connection DTOs — wire parity with Java BankConnectionDTO /
FlinksConnectRequest.

- Field names are camelCase via a Pydantic alias generator.
- `lastSyncAt` / `createdAt` serialize as `yyyy-MM-dd'T'HH:mm:ss` (no millis,
  no timezone) to match Java's `@JsonFormat`.
- `balance` uses `Money` so it serializes as a JSON number (Jackson BigDecimal).
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.core.types import Money


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
    balance: Money | None = None
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

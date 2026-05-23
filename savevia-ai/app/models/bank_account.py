from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class BankAccount(Base):
    """An account exposed by a Flinks bank connection."""

    __tablename__ = "bank_accounts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    connection_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    flinks_account_id: Mapped[str] = mapped_column(String(255), nullable=False)

    account_type: Mapped[str | None] = mapped_column(String(50), default="OTHER")
    account_name: Mapped[str | None] = mapped_column(String(100))
    account_number_masked: Mapped[str | None] = mapped_column(String(20))
    institution_name: Mapped[str | None] = mapped_column(String(100))
    balance: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), default=Decimal("0.00"))
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    linked_card_id: Mapped[int | None] = mapped_column(BigInteger)

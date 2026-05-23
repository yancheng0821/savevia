from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Transaction(Base):
    """User transactions ingested from Flinks and used for cashback analysis."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    transaction_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    account_id: Mapped[int | None] = mapped_column(BigInteger)
    merchant: Mapped[str | None] = mapped_column(String(255))
    mcc: Mapped[str | None] = mapped_column(String(10))
    category: Mapped[str | None] = mapped_column(String(50))
    card_used_id: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    flinks_transaction_id: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(500))
    best_card_id: Mapped[int | None] = mapped_column(BigInteger)
    actual_cashback: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 4), default=Decimal("0.0000")
    )
    optimal_cashback: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 4), default=Decimal("0.0000")
    )
    missed_cashback: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 4), default=Decimal("0.0000")
    )
    is_analyzed: Mapped[bool | None] = mapped_column(Boolean, default=False)

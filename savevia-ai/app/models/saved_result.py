from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SavedResult(Base):
    """Persisted cashback optimization result (shareable via share_id)."""

    __tablename__ = "saved_results"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    result_json: Mapped[str] = mapped_column(Text, nullable=False)

    share_id: Mapped[str | None] = mapped_column(String(32), unique=True, index=True)
    user_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    net_annual_savings: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00")
    )
    annual_reward: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    total_annual_fees: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00")
    )
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)

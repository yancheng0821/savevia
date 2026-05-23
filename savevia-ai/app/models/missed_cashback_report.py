from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import JSON, BigInteger, Date, DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MissedCashbackReport(Base):
    """Aggregated missed-cashback analysis report (weekly / monthly / yearly)."""

    __tablename__ = "missed_cashback_reports"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    report_type: Mapped[str] = mapped_column(String(20), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    total_transactions: Mapped[int | None] = mapped_column(Integer, default=0)
    total_spending: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), default=Decimal("0.00"))
    total_actual_cashback: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00")
    )
    total_optimal_cashback: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00")
    )
    total_missed_cashback: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00")
    )
    category_breakdown: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    top_recommendations: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

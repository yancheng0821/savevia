from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UserConnectionLimit(Base):
    """Tracks per-user monthly Flinks connect quota."""

    __tablename__ = "user_connection_limits"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    # NOTE: column is literally named `year_month` in MySQL; not a reserved word
    # but quoted by SQLAlchemy automatically when needed.
    year_month: Mapped[str] = mapped_column(String(7), nullable=False)

    connection_count: Mapped[int | None] = mapped_column(Integer, default=0)
    max_connections: Mapped[int | None] = mapped_column(Integer, default=5)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

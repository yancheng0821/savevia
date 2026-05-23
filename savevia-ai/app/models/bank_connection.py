from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import BigInteger, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class BankConnectionStatus(str, PyEnum):
    """Lifecycle states for a Flinks bank connection."""

    PENDING = "PENDING"
    CONNECTED = "CONNECTED"
    REFRESHING = "REFRESHING"
    ERROR = "ERROR"
    DISCONNECTED = "DISCONNECTED"


class BankConnection(Base):
    """Per-user Flinks bank login record."""

    __tablename__ = "bank_connections"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    flinks_login_id: Mapped[str] = mapped_column(String(255), nullable=False)

    institution_name: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[BankConnectionStatus | None] = mapped_column(
        Enum(
            BankConnectionStatus,
            values_callable=lambda cls: [m.value for m in cls],
        ),
        default=BankConnectionStatus.PENDING,
        index=True,
    )
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime)
    error_message: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

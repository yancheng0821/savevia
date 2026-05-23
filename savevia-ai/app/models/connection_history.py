from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import BigInteger, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ConnectionHistoryAction(str, PyEnum):
    """Audit actions tracked for bank connection lifecycle events."""

    CONNECT = "CONNECT"
    DISCONNECT = "DISCONNECT"
    REFRESH = "REFRESH"


class ConnectionHistory(Base):
    """Audit log of bank connection events per user."""

    __tablename__ = "connection_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    institution_name: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[ConnectionHistoryAction] = mapped_column(
        Enum(
            ConnectionHistoryAction,
            values_callable=lambda cls: [m.value for m in cls],
        ),
        nullable=False,
    )

    flinks_login_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp(), index=True
    )

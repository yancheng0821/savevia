"""Shared formatting helpers for tool output text."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.modules.optimizer.cashback_calculator import format_rate_as_percentage


def card_header(card: dict[str, Any]) -> str:
    """'TD Cash Visa' style heading."""
    return f"{card.get('bank', '')} {card.get('name', '')}".strip()


def format_rate(value: Any) -> str:
    """Accepts string/Decimal/None and returns percentage string."""
    if value is None or value == "":
        return "1%"
    return format_rate_as_percentage(Decimal(str(value)))

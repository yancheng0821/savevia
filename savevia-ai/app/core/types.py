"""Shared field types for Pydantic schemas.

`Money` — a `Decimal` that serializes to a JSON number (not a string) so
the frontend can call `.toFixed()` / arithmetic on it directly. Java's
Jackson + BigDecimal default emits a number; this keeps Python responses
identical-shape.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from pydantic import PlainSerializer

Money = Annotated[
    Decimal,
    PlainSerializer(
        lambda v: float(v) if v is not None else None,
        return_type=float,
        when_used="json",
    ),
]

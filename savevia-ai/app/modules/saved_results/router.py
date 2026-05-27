"""Saved-results HTTP router — POST /share, GET /share/{id}, GET /share/{id}/og,
POST /user-result, GET /user-result.

Mirrors com.savevia.optimizer.controller.SavedResultController. Java's
controller mounted these under /api/v1/optimize — we keep that path so the
frontend doesn't change. The OG page returns HTML; everything else returns
the standard Java Result<T> envelope.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Header
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_db
from app.modules.saved_results.schema import (
    OptimizationResult,
    SaveResultRequest,
    SaveResultResponse,
)
from app.modules.saved_results.service import SavedResultService

router = APIRouter(prefix="/api/v1/optimize", tags=["saved-results"])


class _Envelope(BaseModel):
    code: int = 200
    message: str = "success"
    data: object | None = None
    timestamp: int = Field(default=0)


def _ok(data: object | None) -> dict:
    return {"code": 200, "message": "success", "data": data, "timestamp": 0}


def _error(code: int, message: str) -> dict:
    return {"code": code, "message": message, "data": None, "timestamp": 0}


def _parse_user_id(raw: str | None) -> int | None:
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def _service(session: AsyncSession) -> SavedResultService:
    return SavedResultService(
        session=session,
        share_base_url=get_settings().share_base_url,
    )


# ---- /share ------------------------------------------------------------

@router.post("/share")
async def share_result(
    body: SaveResultRequest,
    x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
    session: AsyncSession = Depends(get_db),
):
    response = await _service(session).save_result(
        body.result, user_id=_parse_user_id(x_user_id),
    )
    return _ok(response.model_dump(by_alias=True))


@router.get("/share/{share_id}")
async def get_shared_result(
    share_id: str,
    session: AsyncSession = Depends(get_db),
):
    result = await _service(session).get_by_share_id(share_id)
    if result is None:
        return _error(404, "Shared result not found or expired")
    return _ok(result.model_dump(by_alias=True, exclude_none=False, mode="json"))


# ---- OG share page (HTML for crawlers) --------------------------------

_OG_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>

    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{share_url}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{logo_url}">
    <meta property="og:site_name" content="SaveVia">

    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="{share_url}">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{logo_url}">

    <link rel="canonical" href="{share_url}">
</head>
<body>
    <h1>{title}</h1>
    <p>{description}</p>
    <a href="{share_url}">View on SaveVia</a>
</body>
</html>
"""


@router.get("/share/{share_id}/og", response_class=HTMLResponse)
async def share_og_page(
    share_id: str,
    session: AsyncSession = Depends(get_db),
):
    settings = get_settings()
    frontend = settings.frontend_url.rstrip("/")

    result = await _service(session).get_by_share_id(share_id)

    title = "SaveVia - Credit Card Cashback Optimizer"
    description = "Optimize your credit card rewards with SaveVia"

    if result is not None and result.net_annual_savings is not None:
        savings = result.net_annual_savings.quantize(
            Decimal("1"), rounding=ROUND_HALF_UP,
        )
        title = f"I'm saving ${savings}/year with SaveVia!"
        description = (
            f"I optimized my credit card rewards and I'm saving ${savings} "
            "per year. Try SaveVia for free!"
        )

    return _OG_PAGE_TEMPLATE.format(
        title=title,
        description=description,
        share_url=f"{frontend}/share/{share_id}",
        logo_url=f"{frontend}/logo-og.png",
    )


# ---- /user-result ------------------------------------------------------

@router.post("/user-result")
async def save_user_result(
    body: SaveResultRequest = Body(...),
    x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
    session: AsyncSession = Depends(get_db),
):
    user_id = _parse_user_id(x_user_id)
    if user_id is None:
        return _error(401, "User not authenticated")
    await _service(session).save_user_result(body.result, user_id=user_id)
    return _ok(None)


@router.get("/user-result")
async def get_user_result(
    x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
    session: AsyncSession = Depends(get_db),
):
    user_id = _parse_user_id(x_user_id)
    if user_id is None:
        return _error(401, "User not authenticated")
    result = await _service(session).get_user_result(user_id)
    if result is None:
        return _ok(None)
    return _ok(result.model_dump(by_alias=True, exclude_none=False, mode="json"))


__all__ = ["router", "SaveResultResponse", "OptimizationResult"]

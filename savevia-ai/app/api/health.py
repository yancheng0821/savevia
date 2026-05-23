from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.service_name,
        "version": "0.1.0",
        "environment": settings.environment,
    }


@router.get("/ready")
async def ready(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    """Readiness probe — verifies DB connectivity."""
    try:
        await db.execute(text("SELECT 1"))
        return JSONResponse({"status": "ready", "db": "ok"})
    except Exception as e:
        return JSONResponse(
            {"status": "not_ready", "db": "error", "error": str(e)},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

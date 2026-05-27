"""Optimizer-API HTTP router — POST /api/v1/optimize/calculate."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from fastapi import APIRouter, Body

from app.modules.optimizer_api.schema import OptimizationRequest, OptimizationResult
from app.modules.optimizer_api.service import OptimizerInputError

if TYPE_CHECKING:
    from app.modules.optimizer_api.service import CashbackOptimizerService


def _ok(data: object | None) -> dict:
    return {"code": 200, "message": "success", "data": data, "timestamp": 0}


def _error(code: int, message: str) -> dict:
    return {"code": code, "message": message, "data": None, "timestamp": 0}


def build_optimizer_router(
    get_service: "Callable[[], CashbackOptimizerService]",
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/optimize", tags=["optimizer"])

    @router.post("/calculate")
    async def calculate(body: OptimizationRequest = Body(...)) -> dict:
        try:
            result: OptimizationResult = await get_service().optimize(body)
        except OptimizerInputError as e:
            return _error(400, e.message)
        return _ok(result.model_dump(by_alias=True, mode="json"))

    return router

"""Real Flinks Toolbox REST client. INERT in normal operation (no contract):
reached only when FLINKS_SANDBOX=false and loginId is not a demo id. Mirrors
FlinksService.authorizeWithFlinks + getAccountsDetail (FlinksService.java:198-290).
"""

from __future__ import annotations

import asyncio

import httpx

from app.core.logging import get_logger

_log = get_logger("savevia-ai.flinks")


class FlinksError(RuntimeError):
    pass


class FlinksClient:
    def __init__(
        self,
        *,
        base_url: str,
        customer_id: str,
        client: httpx.AsyncClient | None = None,
    ):
        self._base = base_url.rstrip("/")
        self._customer = customer_id
        self._client = client or httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=5.0),
            # Reach Flinks directly, never through a developer's local proxy
            # (mirrors BaseJavaClient).
            trust_env=False,
        )

    async def authorize(self, login_id: str) -> str:
        url = f"{self._base}/{self._customer}/BankingServices/Authorize"
        resp = await self._client.post(
            url, json={"LoginId": login_id, "MostRecentCached": True}
        )
        resp.raise_for_status()
        body = resp.json()
        request_id = body.get("RequestId")
        if not request_id:
            raise FlinksError("Failed to get RequestId from Flinks authorization")
        return request_id

    async def get_accounts_detail(
        self, request_id: str, *, max_retries: int = 10, sleep_seconds: float = 3.0
    ) -> dict:
        url = f"{self._base}/{self._customer}/BankingServices/GetAccountsDetail"
        body = {
            "RequestId": request_id,
            "WithTransactions": True,
            "DaysOfTransactions": "Days90",
        }
        last_error: Exception | None = None
        for attempt in range(max_retries):
            try:
                resp = await self._client.post(url, json=body)
                if resp.status_code == 200:
                    data = resp.json()
                    if "Accounts" in data:
                        return data
            except Exception as e:  # noqa: BLE001 — mirror Java retry-on-any
                last_error = e
                _log.warning("flinks_attempt_failed", attempt=attempt + 1, error=str(e))
            await asyncio.sleep(sleep_seconds)
        raise FlinksError(f"Failed to retrieve bank data: {last_error or 'timeout'}")

    async def aclose(self) -> None:
        await self._client.aclose()

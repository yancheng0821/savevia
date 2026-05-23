"""Base HTTP client for calls to Java services.

Java services return a `Result<T>` envelope:
    {"code": 200, "message": "success", "data": <T>, "timestamp": <ms>}

This base client:
- Holds a persistent httpx.AsyncClient for connection pooling
- Forwards user identity as `X-User-Id` header per call (the same
  header the gateway sets internally after validating the inbound JWT).
  We do NOT forward the raw JWT to internal Java services.
- Unwraps the `Result` envelope, returning only the `data` payload
- Raises `JavaServiceError` on non-200 envelope code or HTTP error
- Retries idempotent GETs on 5xx / timeout (max 2 attempts)
"""

from __future__ import annotations

import asyncio
import random
from typing import Any

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger

_log = get_logger("savevia-ai.clients")


class JavaServiceError(Exception):
    def __init__(
        self,
        service: str,
        status_code: int | None,
        message: str,
        path: str | None = None,
        method: str | None = None,
    ):
        super().__init__(f"[{service}] {method or ''} {path or ''} -> {status_code}: {message}")
        self.service = service
        self.status_code = status_code
        self.message = message
        self.path = path
        self.method = method


class BaseJavaClient:
    """Async HTTP client base for calls to Java services.

    Holds a persistent httpx.AsyncClient. Caller passes user_id per-call;
    we forward it as X-User-Id header (the same header the gateway uses
    internally after validating the inbound JWT). We do NOT forward the
    JWT itself to internal Java services.
    """

    service_name: str = "unknown"

    def __init__(self, base_url: str):
        settings = get_settings()
        self._base_url = base_url.rstrip("/")
        self._timeout = httpx.Timeout(
            settings.http_timeout_seconds,
            connect=settings.http_connect_timeout_seconds,
        )
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
                # Ignore shell HTTP(S)_PROXY/ALL_PROXY env vars — Java services
                # are always reached directly via Eureka-style hostnames,
                # never through a developer's local proxy.
                trust_env=False,
                headers={"Accept": "application/json"},
            )
        return self._client

    async def aclose(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()

    def _build_headers(self, user_id: int | None) -> dict[str, str]:
        h: dict[str, str] = {}
        if user_id is not None:
            h["X-User-Id"] = str(user_id)
        return h

    def _unwrap(self, response: httpx.Response) -> Any:
        """Parse `Result<T>` envelope. Returns `data`; raises on non-200 code."""
        try:
            body = response.json()
        except Exception as e:
            raise JavaServiceError(
                self.service_name,
                response.status_code,
                f"non-JSON response: {response.text[:200]}",
            ) from e

        if not isinstance(body, dict) or "code" not in body:
            raise JavaServiceError(
                self.service_name,
                response.status_code,
                f"unexpected response shape: {body}",
            )

        code = body.get("code")
        if code != 200:
            raise JavaServiceError(
                self.service_name,
                status_code=code if isinstance(code, int) else response.status_code,
                message=body.get("message") or "java business error",
            )
        return body.get("data")

    async def _get(
        self,
        path: str,
        user_id: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        return await self._request("GET", path, user_id=user_id, params=params)

    async def _post(
        self,
        path: str,
        user_id: int | None = None,
        json: Any = None,
    ) -> Any:
        return await self._request("POST", path, user_id=user_id, json=json)

    async def _request(
        self,
        method: str,
        path: str,
        user_id: int | None = None,
        params: dict[str, Any] | None = None,
        json: Any = None,
    ) -> Any:
        client = self._get_client()
        headers = self._build_headers(user_id)

        # Retry policy: only GET, only 5xx/timeout, max 2 attempts
        max_attempts = 2 if method == "GET" else 1
        delays = [0.1, 0.25]

        last_error: Exception | None = None
        for attempt in range(max_attempts):
            try:
                response = await client.request(
                    method, path, headers=headers, params=params, json=json
                )
                # Retry on 5xx for GETs
                if method == "GET" and response.status_code >= 500 and attempt < max_attempts - 1:
                    _log.warning(
                        "java_service_5xx_retry",
                        service=self.service_name,
                        method=method,
                        path=path,
                        status=response.status_code,
                        attempt=attempt + 1,
                    )
                    await asyncio.sleep(delays[attempt] + random.uniform(0, 0.05))
                    continue
                # HTTP-level error (4xx or non-retried 5xx)
                if response.status_code >= 400:
                    _raise_http_error(self.service_name, response, method, path)
                return self._unwrap(response)
            except httpx.TimeoutException as e:
                last_error = e
                if method == "GET" and attempt < max_attempts - 1:
                    _log.warning(
                        "java_service_timeout_retry",
                        service=self.service_name,
                        method=method,
                        path=path,
                        attempt=attempt + 1,
                    )
                    await asyncio.sleep(delays[attempt] + random.uniform(0, 0.05))
                    continue
                raise JavaServiceError(
                    self.service_name,
                    None,
                    f"timeout: {e}",
                    path=path,
                    method=method,
                ) from e
            except httpx.RequestError as e:
                raise JavaServiceError(
                    self.service_name,
                    None,
                    f"network error: {e}",
                    path=path,
                    method=method,
                ) from e

        # Should not reach here, but defensive
        raise JavaServiceError(
            self.service_name,
            None,
            f"exhausted retries: {last_error}",
            path=path,
            method=method,
        )


def _raise_http_error(service: str, response: httpx.Response, method: str, path: str) -> None:
    try:
        body = response.json()
        msg = body.get("message") or body.get("error") or response.text[:200]
    except Exception:
        msg = response.text[:200]
    raise JavaServiceError(service, response.status_code, msg, path=path, method=method)

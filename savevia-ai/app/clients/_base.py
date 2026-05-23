from typing import Any

import httpx

from app.core.config import get_settings


class JavaServiceError(Exception):
    def __init__(self, service: str, status_code: int | None, message: str):
        super().__init__(f"[{service}] {message}")
        self.service = service
        self.status_code = status_code
        self.message = message


class BaseJavaClient:
    """Async HTTP client base for calls to Java services."""

    service_name: str = "unknown"

    def __init__(self, base_url: str, jwt_token: str):
        settings = get_settings()
        self._base_url = base_url.rstrip("/")
        self._jwt_token = jwt_token
        self._timeout = httpx.Timeout(
            settings.http_timeout_seconds,
            connect=settings.http_connect_timeout_seconds,
        )

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {self._jwt_token}",
                "Accept": "application/json",
            },
            timeout=self._timeout,
            # Ignore shell HTTP(S)_PROXY/ALL_PROXY env vars — Java services are
            # always reached directly via Eureka-style hostnames, never through
            # a developer's local proxy.
            trust_env=False,
        )

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        try:
            async with self._client() as c:
                r = await c.get(path, params=params)
                self._raise_for_status(r)
                return r.json()
        except httpx.TimeoutException as e:
            raise JavaServiceError(self.service_name, None, f"timeout: {e}") from e
        except httpx.RequestError as e:
            raise JavaServiceError(self.service_name, None, f"network error: {e}") from e

    async def _post(self, path: str, json: dict[str, Any] | None = None) -> Any:
        try:
            async with self._client() as c:
                r = await c.post(path, json=json)
                self._raise_for_status(r)
                return r.json()
        except httpx.TimeoutException as e:
            raise JavaServiceError(self.service_name, None, f"timeout: {e}") from e
        except httpx.RequestError as e:
            raise JavaServiceError(self.service_name, None, f"network error: {e}") from e

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.status_code >= 400:
            try:
                body = response.json()
                msg = body.get("message") or body.get("error") or response.text
            except Exception:
                msg = response.text
            raise JavaServiceError(self.service_name, response.status_code, msg)

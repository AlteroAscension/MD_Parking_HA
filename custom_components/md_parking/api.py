"""Async client for the local MD Parking Bridge API."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from aiohttp import ClientError, ClientSession, ClientTimeout


class BridgeApiError(RuntimeError):
    """Secret-safe bridge API failure."""

    def __init__(self, code: str, status: int | None = None) -> None:
        super().__init__(code)
        self.code = code
        self.status = status


def normalize_bridge_url(value: str) -> str:
    """Validate and normalize the local bridge origin."""
    parts = urlsplit(value.strip())
    if (
        parts.scheme not in {"http", "https"}
        or not parts.hostname
        or parts.username is not None
        or parts.password is not None
        or parts.query
        or parts.fragment
        or parts.path not in {"", "/"}
    ):
        raise ValueError("invalid bridge URL")
    hostname = parts.hostname
    if ":" in hostname and not hostname.startswith("["):
        hostname = f"[{hostname}]"
    netloc = hostname if parts.port is None else f"{hostname}:{parts.port}"
    return urlunsplit((parts.scheme, netloc, "", "", ""))


@dataclass(slots=True)
class BridgeClient:
    session: ClientSession
    base_url: str
    token: str = ""

    def __post_init__(self) -> None:
        self.base_url = normalize_bridge_url(self.base_url)

    @property
    def headers(self) -> dict[str, str]:
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}

    async def _request(
        self,
        method: str,
        path: str,
        *,
        payload: dict | None = None,
        timeout: int = 15,
        authenticated: bool = True,
    ) -> dict:
        headers = self.headers if authenticated else {}
        try:
            async with self.session.request(
                method,
                self.base_url + path,
                json=payload,
                headers=headers,
                timeout=ClientTimeout(total=timeout),
            ) as response:
                try:
                    value = await response.json(content_type=None)
                except (ValueError, TypeError) as exc:
                    raise BridgeApiError("invalid_response", response.status) from exc
                if not isinstance(value, dict):
                    raise BridgeApiError("invalid_response", response.status)
                if response.status < 200 or response.status >= 300:
                    code = value.get("error")
                    raise BridgeApiError(
                        code if isinstance(code, str) else "bridge_error",
                        response.status,
                    )
                return value
        except BridgeApiError:
            raise
        except (ClientError, asyncio.TimeoutError) as exc:
            raise BridgeApiError("cannot_connect") from exc

    async def pair(self) -> str:
        payload = await self._request(
            "POST", "/v1/pair", authenticated=False, timeout=10
        )
        token = payload.get("api_token")
        if not isinstance(token, str) or not token:
            raise BridgeApiError("invalid_response")
        self.token = token
        return token

    async def diagnostics(self) -> dict:
        return await self._request("GET", "/diagnostics")

    async def cameras(self) -> list[dict]:
        payload = await self._request("GET", "/v1/cameras")
        value = payload.get("cameras")
        if not isinstance(value, list):
            raise BridgeApiError("invalid_response")
        return [item for item in value if isinstance(item, dict)]

    async def barriers(self) -> dict:
        return await self._request("GET", "/v1/barriers")

    async def request_code(self, phone: str, object_id: str | None = None) -> dict:
        payload = {"phone": phone}
        if object_id:
            payload["object_id"] = object_id
        return await self._request(
            "POST", "/v1/auth/request-code", payload=payload, timeout=25
        )

    async def authorize(self, phone: str, object_id: str, code: str) -> dict:
        return await self._request(
            "POST",
            "/v1/auth/authorize",
            payload={"phone": phone, "object_id": object_id, "code": code},
            timeout=35,
        )

    async def open_barrier(self, barrier_id: str) -> dict:
        return await self._request(
            "POST",
            f"/v1/barriers/{barrier_id}/open",
            payload={"confirm": True},
            timeout=25,
        )

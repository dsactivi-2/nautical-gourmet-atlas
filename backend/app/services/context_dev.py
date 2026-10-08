import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import Any

import httpx

from app.schemas.context_map import MappedUrl, MapUrlsRequest, MapUrlsResult


CONTEXT_DEV_BASE_URL = "https://api.context.dev/v1"
_TRANSIENT_STATUS_CODES = frozenset({408, 409, 429, 500, 502, 503})
_MAX_RETRY_AFTER_SECONDS = 60

Sleep = Callable[[float], Awaitable[None]]


class ContextDevError(Exception):
    """Failure while calling Context.dev or reading its response."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        error_code: str | None = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.request_id = request_id


def public_status(upstream_status: int) -> int:
    """Map a Context.dev status onto a status for this API."""
    if upstream_status in {400, 422}:
        return 400
    if upstream_status == 404:
        return 404
    if upstream_status == 408:
        return 504
    if upstream_status == 429:
        return 429
    return 502


class ContextDevClient:
    """Server-side client for Context.dev Map URLs (``GET /web/urls``)."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = CONTEXT_DEV_BASE_URL,
        http: httpx.AsyncClient | None = None,
        timeout: float = 60.0,
        max_retries: int = 2,
        sleep: Sleep | None = None,
    ) -> None:
        if not api_key:
            raise ContextDevError(
                "CONTEXT_DEV_API_KEY is not configured",
                status_code=503,
                error_code="NOT_CONFIGURED",
            )
        self._api_key = api_key
        self._base_url = base_url
        self._http = http
        self._timeout = timeout
        self._max_retries = max_retries
        self._sleep = sleep or asyncio.sleep

    async def map_urls(self, query: MapUrlsRequest) -> MapUrlsResult:
        """Discover URLs for a domain, bounded by ``maxLinks``."""
        params = {"domain": query.domain, "maxLinks": query.max_links}
        owns_client = self._http is None
        client = self._http or httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
        )
        try:
            return await self._map_urls(client, params)
        finally:
            if owns_client:
                await client.aclose()

    async def _map_urls(
        self,
        client: httpx.AsyncClient,
        params: dict[str, Any],
    ) -> MapUrlsResult:
        attempt = 0
        while True:
            try:
                response = await client.get(
                    "/web/urls",
                    params=params,
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Accept": "application/json",
                    },
                )
            except httpx.TransportError as exc:
                if attempt >= self._max_retries:
                    raise ContextDevError(
                        "Context.dev request failed before a response was received",
                        status_code=503,
                        error_code="TRANSPORT_ERROR",
                    ) from exc
                await self._sleep(self._backoff(attempt))
                attempt += 1
                continue

            if response.status_code == 200:
                return self._parse_success(response)

            if (
                response.status_code in _TRANSIENT_STATUS_CODES
                and attempt < self._max_retries
            ):
                await self._sleep(self._retry_delay(response, attempt))
                attempt += 1
                continue

            raise self._error_from_response(response)

    def _parse_success(self, response: httpx.Response) -> MapUrlsResult:
        payload = self._json_object(response)
        request_id = payload.get("request_id") or response.headers.get("X-Request-Id")
        if payload.get("success") is not True:
            raise ContextDevError(
                "Context.dev did not return a successful map result",
                status_code=200,
                error_code="INVALID_RESPONSE",
                request_id=_optional_str(request_id),
            )
        if not isinstance(request_id, str) or not request_id:
            raise ContextDevError(
                "Context.dev map response is missing request_id",
                status_code=200,
                error_code="INVALID_RESPONSE",
            )

        domain = payload.get("domain")
        if not isinstance(domain, str) or not domain:
            raise ContextDevError(
                "Context.dev map response is missing domain",
                status_code=200,
                error_code="INVALID_RESPONSE",
                request_id=request_id,
            )

        partial = payload.get("partial", False)
        if not isinstance(partial, bool):
            raise ContextDevError(
                "Context.dev map response has an invalid partial flag",
                status_code=200,
                error_code="INVALID_RESPONSE",
                request_id=request_id,
            )

        urls_payload = payload.get("urls")
        if not isinstance(urls_payload, list):
            raise ContextDevError(
                "Context.dev map response is missing urls",
                status_code=200,
                error_code="INVALID_RESPONSE",
                request_id=request_id,
            )

        credits_consumed, credits_remaining = _credits(payload.get("key_metadata"))
        return MapUrlsResult(
            success=True,
            domain=domain,
            urls=[_mapped_url(item, index, request_id) for index, item in enumerate(urls_payload)],
            partial=partial,
            request_id=request_id,
            credits_consumed=credits_consumed,
            credits_remaining=credits_remaining,
        )

    def _error_from_response(self, response: httpx.Response) -> ContextDevError:
        request_id = response.headers.get("X-Request-Id")
        message = "Context.dev request failed"
        error_code: str | None = None
        payload = _optional_json_object(response)
        if payload is not None:
            raw_message = payload.get("message")
            if isinstance(raw_message, str) and raw_message:
                message = raw_message
            raw_code = payload.get("error_code")
            if isinstance(raw_code, str) and raw_code:
                error_code = raw_code
            raw_request_id = payload.get("request_id")
            if isinstance(raw_request_id, str) and raw_request_id:
                request_id = raw_request_id
        return ContextDevError(
            self._redact(message),
            status_code=response.status_code,
            error_code=error_code,
            request_id=request_id,
        )

    def _json_object(self, response: httpx.Response) -> dict[str, Any]:
        payload = _optional_json_object(response)
        if payload is None:
            raise ContextDevError(
                "Context.dev returned a response that is not a JSON object",
                status_code=response.status_code,
                error_code="INVALID_RESPONSE",
                request_id=response.headers.get("X-Request-Id"),
            )
        return payload

    def _redact(self, message: str) -> str:
        if self._api_key and self._api_key in message:
            return message.replace(self._api_key, "[redacted]")
        return message

    def _retry_delay(self, response: httpx.Response, attempt: int) -> float:
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            if retry_after is not None and retry_after.isdigit():
                return float(min(int(retry_after), _MAX_RETRY_AFTER_SECONDS))
        return self._backoff(attempt)

    @staticmethod
    def _backoff(attempt: int) -> float:
        return min(0.2 * (2**attempt), 8.0) + random.uniform(0, 0.1)


def _optional_json_object(response: httpx.Response) -> dict[str, Any] | None:
    try:
        payload = response.json()
    except ValueError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _optional_str(value: Any) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None


def _credits(metadata: Any) -> tuple[int | None, int | None]:
    if not isinstance(metadata, dict):
        return None, None
    return _optional_int(metadata.get("credits_consumed")), _optional_int(
        metadata.get("credits_remaining")
    )


def _optional_int(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _mapped_url(item: Any, index: int, request_id: str) -> MappedUrl:
    if not isinstance(item, dict):
        raise ContextDevError(
            f"urls[{index}] is not an object",
            status_code=200,
            error_code="INVALID_RESPONSE",
            request_id=request_id,
        )
    url = item.get("url")
    if not isinstance(url, str) or not url:
        raise ContextDevError(
            f"urls[{index}] is missing url",
            status_code=200,
            error_code="INVALID_RESPONSE",
            request_id=request_id,
        )
    title = item.get("title")
    description = item.get("description")
    language = item.get("language")
    keywords = item.get("keywords")
    if keywords is not None and (
        not isinstance(keywords, list) or not all(isinstance(keyword, str) for keyword in keywords)
    ):
        raise ContextDevError(
            f"urls[{index}].keywords must be a list of strings",
            status_code=200,
            error_code="INVALID_RESPONSE",
            request_id=request_id,
        )
    return MappedUrl(
        url=url,
        title=title if isinstance(title, str) else None,
        description=description if isinstance(description, str) else None,
        keywords=keywords,
        language=language if isinstance(language, str) else None,
    )

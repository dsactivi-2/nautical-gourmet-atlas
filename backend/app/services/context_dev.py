"""Client for the Context.dev Map URLs endpoint.

Calls ``GET https://api.context.dev/v1/web/urls`` and accepts both the
documented ``urls`` inventory and a count-only body whose ``urlCount`` field
is the number of discovered URLs.
"""

from collections.abc import Mapping
from typing import Any

import httpx
from pydantic import ValidationError

from app.schemas.context_dev import DomainUrlCount

DEFAULT_BASE_URL = "https://api.context.dev/v1"
_MIN_DOMAIN_LENGTH = 3
_MAX_DOMAIN_LENGTH = 253
_MAX_LINKS = 100_000
_MAX_URL_REGEX_LENGTH = 256
_MIN_SEARCH_LENGTH = 2
_MAX_SEARCH_LENGTH = 200


class ContextDevError(Exception):
    """Base error for Context.dev calls and response handling."""


class ContextDevConfigError(ContextDevError):
    """The API key or base URL is missing."""


class ContextDevRequestError(ContextDevError):
    """The call was rejected locally, before any credits were spent."""


class ContextDevAPIError(ContextDevError):
    """Context.dev returned an error status or ``success`` was not true."""

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

    def public_detail(self) -> dict[str, str | None]:
        return {
            "message": self.message,
            "error_code": self.error_code,
            "request_id": self.request_id,
        }


class ContextDevResponseError(ContextDevError):
    """A successful HTTP response did not match the Map URLs contract."""

    def __init__(self, message: str, *, request_id: str | None = None) -> None:
        super().__init__(message)
        self.request_id = request_id


def parse_domain_url_count(payload: Mapping[str, Any]) -> DomainUrlCount:
    """Validate a Map URLs body, including the count-only example shape."""
    if payload.get("success") is not True:
        raise ContextDevAPIError(
            _error_message(payload),
            status_code=200,
            error_code=_optional_str(payload.get("error_code")),
            request_id=_optional_str(payload.get("request_id")),
        )
    try:
        return DomainUrlCount.model_validate(payload)
    except ValidationError as exc:
        raise ContextDevResponseError(
            "Context.dev returned a Map URLs body that could not be read",
            request_id=_optional_str(payload.get("request_id")),
        ) from exc


class ContextDevClient:
    """Async client for ``GET /web/urls``."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 60.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if not api_key or not api_key.strip():
            raise ContextDevConfigError("CONTEXT_DEV_API_KEY is not set")
        if not base_url or not base_url.strip():
            raise ContextDevConfigError("CONTEXT_DEV_BASE_URL is not set")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._transport = transport

    async def count_urls(
        self,
        domain: str,
        *,
        include_subdomains: bool = False,
        max_links: int | None = None,
        url_regex: str | None = None,
        search: str | None = None,
    ) -> DomainUrlCount:
        """Map a domain and return its URL count, credits, and request id."""
        params = _query_params(
            domain,
            include_subdomains=include_subdomains,
            max_links=max_links,
            url_regex=url_regex,
            search=search,
        )
        async with httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            transport=self._transport,
        ) as client:
            response = await client.get(
                "/web/urls",
                params=params,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Accept": "application/json",
                },
            )
        return _read_response(response)


def _query_params(
    domain: str,
    *,
    include_subdomains: bool,
    max_links: int | None,
    url_regex: str | None,
    search: str | None,
) -> dict[str, str | int | bool]:
    cleaned = _validate_domain(domain)
    params: dict[str, str | int | bool] = {"domain": cleaned}
    if include_subdomains:
        params["includeSubdomains"] = "true"
    if max_links is not None:
        if max_links < 1 or max_links > _MAX_LINKS:
            raise ContextDevRequestError(
                f"max_links must be between 1 and {_MAX_LINKS}"
            )
        params["maxLinks"] = max_links
    if url_regex is not None:
        if not url_regex or len(url_regex) > _MAX_URL_REGEX_LENGTH:
            raise ContextDevRequestError(
                f"url_regex must be 1 to {_MAX_URL_REGEX_LENGTH} characters"
            )
        params["urlRegex"] = url_regex
    if search is not None:
        if len(search) < _MIN_SEARCH_LENGTH or len(search) > _MAX_SEARCH_LENGTH:
            raise ContextDevRequestError(
                f"search must be {_MIN_SEARCH_LENGTH} to {_MAX_SEARCH_LENGTH} characters"
            )
        params["search"] = search
    return params


def _validate_domain(domain: str) -> str:
    cleaned = domain.strip().lower().rstrip(".")
    if "://" in cleaned or "/" in cleaned or "@" in cleaned:
        raise ContextDevRequestError(
            "domain must be a bare hostname such as cookbook.openai.com"
        )
    if len(cleaned) < _MIN_DOMAIN_LENGTH or len(cleaned) > _MAX_DOMAIN_LENGTH:
        raise ContextDevRequestError(
            f"domain must be {_MIN_DOMAIN_LENGTH} to {_MAX_DOMAIN_LENGTH} characters"
        )
    if any(char.isspace() for char in cleaned) or ".." in cleaned:
        raise ContextDevRequestError("domain must be a bare hostname")
    labels = cleaned.split(".")
    if len(labels) < 2:
        raise ContextDevRequestError("domain must include a hostname and a suffix")
    for label in labels:
        if not label or label.startswith("-") or label.endswith("-"):
            raise ContextDevRequestError("domain must be a bare hostname")
        if not all(char.isalnum() or char == "-" for char in label):
            raise ContextDevRequestError("domain must be a bare hostname")
    return cleaned


def _read_response(response: httpx.Response) -> DomainUrlCount:
    try:
        payload = response.json()
    except ValueError as exc:
        raise ContextDevResponseError(
            "Context.dev returned a response that is not JSON",
            request_id=response.headers.get("X-Request-Id"),
        ) from exc
    if not isinstance(payload, dict):
        raise ContextDevResponseError(
            "Context.dev returned a JSON value that is not an object",
            request_id=response.headers.get("X-Request-Id"),
        )
    if response.status_code >= 400 or payload.get("success") is not True:
        raise ContextDevAPIError(
            _error_message(payload),
            status_code=response.status_code,
            error_code=_optional_str(payload.get("error_code")),
            request_id=_optional_str(payload.get("request_id"))
            or response.headers.get("X-Request-Id"),
        )
    return parse_domain_url_count(payload)


def _error_message(payload: Mapping[str, Any]) -> str:
    message = payload.get("message")
    if isinstance(message, str) and message.strip():
        return message
    error_code = payload.get("error_code")
    if isinstance(error_code, str) and error_code.strip():
        return error_code
    return "Context.dev request failed"


def _optional_str(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value
    return None


def status_for_api_error(error: ContextDevAPIError) -> int:
    """Map a Context.dev failure onto an HTTP status for this API."""
    if error.status_code == 429 or error.error_code == "RATE_LIMITED":
        return 429
    if error.error_code == "USAGE_EXCEEDED":
        return 402
    if error.status_code == 400:
        return 400
    if error.status_code == 408 or error.error_code == "REQUEST_TIMEOUT":
        return 504
    return 502


import httpx
import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.api import context as context_api
from app.api.context import get_context_client, map_domain_urls
from app.schemas.context_map import MapUrlsRequest
from app.services.context_dev import ContextDevClient, ContextDevError, public_status


EXAMPLE_QUERY = {
    "domain": "cookbook.openai.com",
    "maxLinks": "150",
}

MAP_RESPONSE = {
    "success": True,
    "domain": "cookbook.openai.com",
    "urls": [
        {
            "url": "https://cookbook.openai.com/examples/gpt-5-coding-examples",
            "title": "GPT-5 coding examples",
            "description": "Cookbook recipes for coding agents",
            "keywords": ["openai", "cookbook"],
            "language": "en",
        },
        {"url": "https://cookbook.openai.com/"},
    ],
    "partial": False,
    "request_id": "3f1c2a6e-8b4d-4c1e-9f0a-2d7b5e6c8a91",
    "key_metadata": {"credits_consumed": 1, "credits_remaining": 99},
}


def test_example_payload_coerces_string_max_links():
    query = MapUrlsRequest.model_validate(EXAMPLE_QUERY)

    assert query.domain == "cookbook.openai.com"
    assert query.max_links == 150


def _client(handler, **kwargs) -> ContextDevClient:
    return ContextDevClient(
        api_key="test-key",
        http=httpx.AsyncClient(
            transport=httpx.MockTransport(handler),
            base_url="https://api.context.dev/v1",
        ),
        **kwargs,
    )


def test_example_payload_rejects_protocol_and_out_of_range_limit():
    with pytest.raises(ValidationError):
        MapUrlsRequest.model_validate(
            {"domain": "https://cookbook.openai.com", "maxLinks": "150"}
        )

    with pytest.raises(ValidationError):
        MapUrlsRequest.model_validate(
            {"domain": "cookbook.openai.com", "maxLinks": "100001"}
        )


@pytest.mark.asyncio
async def test_map_urls_sends_example_query_and_reads_response():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/v1/web/urls"
        assert request.url.params["domain"] == "cookbook.openai.com"
        assert request.url.params["maxLinks"] == "150"
        assert request.headers["authorization"] == "Bearer test-key"
        return httpx.Response(200, json=MAP_RESPONSE)

    client = _client(handler, max_retries=0)

    result = await client.map_urls(MapUrlsRequest.model_validate(EXAMPLE_QUERY))

    assert result.domain == "cookbook.openai.com"
    assert result.partial is False
    assert result.request_id == MAP_RESPONSE["request_id"]
    assert result.credits_consumed == 1
    assert result.credits_remaining == 99
    assert [item.url for item in result.urls] == [
        "https://cookbook.openai.com/examples/gpt-5-coding-examples",
        "https://cookbook.openai.com/",
    ]
    assert result.urls[0].title == "GPT-5 coding examples"
    assert result.urls[1].title is None


@pytest.mark.asyncio
async def test_validation_errors_are_not_retried():
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            400,
            json={
                "message": "domain is invalid",
                "error_code": "INPUT_VALIDATION_ERROR",
                "request_id": "req-400",
            },
        )

    client = _client(handler, max_retries=2)

    with pytest.raises(ContextDevError) as caught:
        await client.map_urls(MapUrlsRequest.model_validate(EXAMPLE_QUERY))

    assert calls == 1
    assert caught.value.status_code == 400
    assert caught.value.error_code == "INPUT_VALIDATION_ERROR"
    assert caught.value.request_id == "req-400"


@pytest.mark.asyncio
async def test_rate_limit_is_retried_then_succeeds():
    calls = 0
    delays: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(
                429,
                headers={"Retry-After": "1"},
                json={
                    "message": "slow down",
                    "error_code": "RATE_LIMITED",
                    "request_id": "req-429",
                },
            )
        return httpx.Response(200, json=MAP_RESPONSE)

    async def record_sleep(delay: float) -> None:
        delays.append(delay)

    client = _client(handler, max_retries=2, sleep=record_sleep)

    result = await client.map_urls(MapUrlsRequest.model_validate(EXAMPLE_QUERY))

    assert calls == 2
    assert delays == [1.0]
    assert result.request_id == MAP_RESPONSE["request_id"]


@pytest.mark.asyncio
async def test_api_key_is_redacted_from_error_messages():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "message": "rejected key test-key",
                "error_code": "NOT_FOUND",
                "request_id": "req-401",
            },
        )

    client = _client(handler, max_retries=2)

    with pytest.raises(ContextDevError) as caught:
        await client.map_urls(MapUrlsRequest.model_validate(EXAMPLE_QUERY))

    assert "test-key" not in caught.value.message
    assert "[redacted]" in caught.value.message


@pytest.mark.asyncio
async def test_incomplete_success_payload_is_rejected():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"success": True, "domain": "cookbook.openai.com"})

    client = _client(handler, max_retries=0)

    with pytest.raises(ContextDevError) as caught:
        await client.map_urls(MapUrlsRequest.model_validate(EXAMPLE_QUERY))

    assert caught.value.error_code == "INVALID_RESPONSE"


@pytest.mark.asyncio
async def test_map_endpoint_handles_example_payload():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["maxLinks"] == "150"
        return httpx.Response(200, json=MAP_RESPONSE)

    result = await map_domain_urls(
        MapUrlsRequest.model_validate(EXAMPLE_QUERY),
        object(),
        _client(handler, max_retries=0),
    )

    assert result.domain == "cookbook.openai.com"
    assert result.success is True
    assert len(result.urls) == 2
    assert result.request_id == MAP_RESPONSE["request_id"]


@pytest.mark.asyncio
async def test_map_endpoint_surfaces_rate_limit():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            429,
            json={
                "message": "slow down",
                "error_code": "RATE_LIMITED",
                "request_id": "req-429",
            },
        )

    with pytest.raises(HTTPException) as caught:
        await map_domain_urls(
            MapUrlsRequest.model_validate(EXAMPLE_QUERY),
            object(),
            _client(handler, max_retries=0),
        )

    assert caught.value.status_code == 429
    assert caught.value.detail["error_code"] == "RATE_LIMITED"
    assert caught.value.detail["request_id"] == "req-429"


def test_missing_api_key_is_unavailable(monkeypatch):
    monkeypatch.setattr(context_api.settings, "CONTEXT_DEV_API_KEY", "")

    with pytest.raises(HTTPException) as caught:
        get_context_client()

    assert caught.value.status_code == 503
    assert caught.value.detail == "Context.dev is not configured"


def test_upstream_statuses_are_mapped_for_callers():
    assert public_status(400) == 400
    assert public_status(401) == 502
    assert public_status(408) == 504
    assert public_status(429) == 429
    assert public_status(500) == 502

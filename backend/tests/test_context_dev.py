import json

import httpx
import pytest
from pydantic import ValidationError

from app.api.context import get_context_client
from app.main import app
from app.models.user import User
from app.schemas.context_dev import DomainUrlCount
from app.services.auth import get_current_user
from app.services.context_dev import (
    ContextDevAPIError,
    ContextDevClient,
    ContextDevConfigError,
    ContextDevRequestError,
    ContextDevResponseError,
    parse_domain_url_count,
    status_for_api_error,
)

EXAMPLE = {
    "success": True,
    "domain": "cookbook.openai.com",
    "urlCount": 150,
    "key_metadata": {
        "credits_consumed": 1,
        "credits_remaining": 1189,
    },
    "request_id": "4fd693c6-eaf6-40d9-8f64-8f61501d7ddf",
}

REQUEST_ID = "4fd693c6-eaf6-40d9-8f64-8f61501d7ddf"


def test_parse_example_count_response():
    parsed = parse_domain_url_count(EXAMPLE)

    assert parsed.success is True
    assert parsed.domain == "cookbook.openai.com"
    assert parsed.url_count == 150
    assert parsed.key_metadata is not None
    assert parsed.key_metadata.credits_consumed == 1
    assert parsed.key_metadata.credits_remaining == 1189
    assert str(parsed.request_id) == REQUEST_ID
    assert parsed.partial is False
    assert parsed.to_context_payload() == EXAMPLE


def test_parse_example_from_json_text():
    parsed = DomainUrlCount.model_validate(json.loads(json.dumps(EXAMPLE)))

    assert parsed.url_count == 150
    assert parsed.to_context_payload() == EXAMPLE


def test_parse_url_inventory_uses_list_length():
    payload = {
        "success": True,
        "domain": "cookbook.openai.com",
        "urls": [
            {"url": "https://cookbook.openai.com/a", "title": "A"},
            {"url": "https://cookbook.openai.com/b"},
        ],
        "partial": True,
        "key_metadata": {"credits_consumed": 1, "credits_remaining": 10},
        "request_id": REQUEST_ID,
    }

    parsed = parse_domain_url_count(payload)

    assert parsed.url_count == 2
    assert parsed.partial is True
    assert parsed.to_context_payload()["urlCount"] == 2
    assert parsed.to_context_payload()["partial"] is True


def test_explicit_url_count_wins_over_truncated_list():
    payload = {
        **EXAMPLE,
        "urls": [{"url": "https://cookbook.openai.com/only-one"}],
    }

    assert parse_domain_url_count(payload).url_count == 150


def test_string_url_list_is_counted():
    payload = {
        "success": True,
        "domain": "cookbook.openai.com",
        "urls": ["https://cookbook.openai.com/a", "https://cookbook.openai.com/b"],
        "request_id": REQUEST_ID,
    }

    parsed = parse_domain_url_count(payload)

    assert parsed.url_count == 2
    assert parsed.key_metadata is None
    assert "key_metadata" not in parsed.to_context_payload()


def test_failed_body_keeps_error_code_and_request_id():
    with pytest.raises(ContextDevAPIError) as caught:
        parse_domain_url_count(
            {
                "success": False,
                "message": "Not enough credits",
                "error_code": "USAGE_EXCEEDED",
                "request_id": REQUEST_ID,
                "key_metadata": {"credits_consumed": 0, "credits_remaining": 0},
            }
        )

    assert caught.value.error_code == "USAGE_EXCEEDED"
    assert caught.value.request_id == REQUEST_ID
    assert "Not enough credits" in str(caught.value)


def test_missing_count_and_urls_is_a_response_error():
    with pytest.raises(ContextDevResponseError):
        parse_domain_url_count(
            {
                "success": True,
                "domain": "cookbook.openai.com",
                "request_id": REQUEST_ID,
            }
        )


def test_invalid_request_id_is_rejected():
    with pytest.raises(ValidationError):
        DomainUrlCount.model_validate({**EXAMPLE, "request_id": "not-a-uuid"})


def test_negative_url_count_is_rejected():
    with pytest.raises(ContextDevResponseError):
        parse_domain_url_count({**EXAMPLE, "urlCount": -1})


def test_incomplete_key_metadata_is_rejected():
    with pytest.raises(ContextDevResponseError):
        parse_domain_url_count({**EXAMPLE, "key_metadata": {"credits_consumed": 1}})


def test_status_mapping():
    usage = ContextDevAPIError("no credits", status_code=401, error_code="USAGE_EXCEEDED")
    limited = ContextDevAPIError("slow down", status_code=429, error_code="RATE_LIMITED")
    invalid = ContextDevAPIError("bad domain", status_code=400, error_code="INPUT_VALIDATION_ERROR")
    timeout = ContextDevAPIError("too slow", status_code=408, error_code="REQUEST_TIMEOUT")
    other = ContextDevAPIError("down", status_code=500, error_code="INTERNAL_ERROR")

    assert status_for_api_error(usage) == 402
    assert status_for_api_error(limited) == 429
    assert status_for_api_error(invalid) == 400
    assert status_for_api_error(timeout) == 504
    assert status_for_api_error(other) == 502


def test_client_requires_api_key():
    with pytest.raises(ContextDevConfigError):
        ContextDevClient("  ")


@pytest.mark.asyncio
async def test_client_reads_example_response():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        seen["domain"] = request.url.params["domain"]
        seen["include"] = request.url.params["includeSubdomains"]
        seen["max"] = request.url.params["maxLinks"]
        seen["authorization"] = request.headers["authorization"]
        seen["accept"] = request.headers["accept"]
        return httpx.Response(200, json=EXAMPLE)

    client = ContextDevClient(
        "ctxt_test_key",
        base_url="https://api.context.dev/v1",
        transport=httpx.MockTransport(handler),
    )

    parsed = await client.count_urls(
        " cookbook.openai.com. ",
        include_subdomains=True,
        max_links=150,
    )

    assert parsed.to_context_payload() == EXAMPLE
    assert seen["path"] == "/v1/web/urls"
    assert seen["domain"] == "cookbook.openai.com"
    assert seen["include"] == "true"
    assert seen["max"] == "150"
    assert seen["authorization"] == "Bearer ctxt_test_key"
    assert seen["accept"] == "application/json"
    assert "ctxt_test_key" not in json.dumps(parsed.to_context_payload())


@pytest.mark.asyncio
async def test_client_does_not_call_api_for_a_url():
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError(f"unexpected request to {request.url}")

    client = ContextDevClient("ctxt_test_key", transport=httpx.MockTransport(handler))

    with pytest.raises(ContextDevRequestError):
        await client.count_urls("https://cookbook.openai.com/guides")


@pytest.mark.asyncio
async def test_client_maps_usage_exceeded():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "message": "Not enough credits",
                "error_code": "USAGE_EXCEEDED",
                "request_id": REQUEST_ID,
                "key_metadata": {"credits_consumed": 0, "credits_remaining": 0},
            },
            headers={"X-Request-Id": REQUEST_ID},
        )

    client = ContextDevClient("ctxt_test_key", transport=httpx.MockTransport(handler))

    with pytest.raises(ContextDevAPIError) as caught:
        await client.count_urls("cookbook.openai.com")

    assert caught.value.status_code == 401
    assert caught.value.error_code == "USAGE_EXCEEDED"
    assert caught.value.public_detail()["request_id"] == REQUEST_ID
    assert "ctxt_test_key" not in str(caught.value)


@pytest.mark.asyncio
async def test_client_rejects_non_json():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<html></html>", headers={"X-Request-Id": REQUEST_ID})

    client = ContextDevClient("ctxt_test_key", transport=httpx.MockTransport(handler))

    with pytest.raises(ContextDevResponseError) as caught:
        await client.count_urls("cookbook.openai.com")

    assert caught.value.request_id == REQUEST_ID


@pytest.mark.asyncio
async def test_url_count_route_returns_example(client):
    class StubClient:
        async def count_urls(self, domain: str, **kwargs):
            assert domain == "cookbook.openai.com"
            assert kwargs["max_links"] == 150
            return parse_domain_url_count(EXAMPLE)

    app.dependency_overrides[get_current_user] = lambda: User(
        id=1,
        email="test@example.com",
        hashed_password="hashed",
        first_name="Test",
        last_name="User",
    )
    app.dependency_overrides[get_context_client] = lambda: StubClient()

    response = await client.get(
        "/v1/context/url-count",
        params={"domain": "cookbook.openai.com", "max_links": 150},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["domain"] == "cookbook.openai.com"
    assert body["url_count"] == 150
    assert body["key_metadata"]["credits_consumed"] == 1
    assert body["key_metadata"]["credits_remaining"] == 1189
    assert body["request_id"] == REQUEST_ID
    assert body["success"] is True


@pytest.mark.asyncio
async def test_url_count_route_requires_auth(client):
    response = await client.get(
        "/v1/context/url-count",
        params={"domain": "cookbook.openai.com"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_url_count_route_reports_missing_key(client, monkeypatch):
    monkeypatch.setattr("app.api.context.settings.CONTEXT_DEV_API_KEY", "")
    app.dependency_overrides[get_current_user] = lambda: User(
        id=1,
        email="test@example.com",
        hashed_password="hashed",
        first_name="Test",
        last_name="User",
    )

    response = await client.get(
        "/v1/context/url-count",
        params={"domain": "cookbook.openai.com"},
    )

    assert response.status_code == 503
    assert "CONTEXT_DEV_API_KEY" in response.json()["detail"]


@pytest.mark.asyncio
async def test_url_count_route_maps_upstream_error(client):
    class FailingClient:
        async def count_urls(self, domain: str, **kwargs):
            raise ContextDevAPIError(
                "Not enough credits",
                status_code=401,
                error_code="USAGE_EXCEEDED",
                request_id=REQUEST_ID,
            )

    app.dependency_overrides[get_current_user] = lambda: User(
        id=1,
        email="test@example.com",
        hashed_password="hashed",
        first_name="Test",
        last_name="User",
    )
    app.dependency_overrides[get_context_client] = lambda: FailingClient()

    response = await client.get(
        "/v1/context/url-count",
        params={"domain": "cookbook.openai.com"},
    )

    assert response.status_code == 402
    assert response.json()["detail"]["error_code"] == "USAGE_EXCEEDED"
    assert response.json()["detail"]["request_id"] == REQUEST_ID

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


_DOMAIN_PATTERN = re.compile(
    r"^(?=.{3,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)*[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$"
)


class MapUrlsRequest(BaseModel):
    """Query for Context.dev ``GET /web/urls``.

    ``maxLinks`` is accepted as a number or a numeric string, matching payloads
    such as ``{"domain": "cookbook.openai.com", "maxLinks": "150"}``.
    """

    model_config = ConfigDict(populate_by_name=True)

    domain: str = Field(min_length=3, max_length=253)
    max_links: int = Field(alias="maxLinks", ge=1, le=100_000)

    @field_validator("domain")
    @classmethod
    def normalize_domain(cls, value: str) -> str:
        domain = value.strip().lower().rstrip(".")
        if not _DOMAIN_PATTERN.fullmatch(domain):
            raise ValueError(
                "domain must be a bare host such as cookbook.openai.com"
            )
        return domain


class MappedUrl(BaseModel):
    url: str
    title: str | None = None
    description: str | None = None
    keywords: list[str] | None = None
    language: str | None = None


class MapUrlsResult(BaseModel):
    success: bool
    domain: str
    urls: list[MappedUrl]
    partial: bool = False
    request_id: str
    credits_consumed: int | None = None
    credits_remaining: int | None = None

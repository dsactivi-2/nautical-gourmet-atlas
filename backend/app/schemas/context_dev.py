"""Response models for the Context.dev Map URLs API.

A count-only body looks like this::

    {
      "success": true,
      "domain": "cookbook.openai.com",
      "urlCount": 150,
      "key_metadata": {
        "credits_consumed": 1,
        "credits_remaining": 1189
      },
      "request_id": "4fd693c6-eaf6-40d9-8f64-8f61501d7ddf"
    }

The same endpoint can also return a ``urls`` array. ``urlCount`` is used when
it is present; otherwise the count is the length of that array.
"""

from typing import Any, Literal
from uuid import UUID

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


class KeyMetadata(BaseModel):
    """Credits charged for one request and the balance left afterward."""

    model_config = ConfigDict(extra="ignore")

    credits_consumed: int
    credits_remaining: int


class DomainUrlCount(BaseModel):
    """Normalized Map URLs result, including count-only responses."""

    model_config = ConfigDict(extra="ignore")

    success: Literal[True]
    domain: str = Field(min_length=1)
    url_count: int = Field(
        ge=0,
        validation_alias=AliasChoices("urlCount", "url_count"),
    )
    key_metadata: KeyMetadata | None = None
    request_id: UUID
    partial: bool = False

    @model_validator(mode="before")
    @classmethod
    def fill_url_count(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        if "urlCount" in data or "url_count" in data:
            return data
        urls = data.get("urls")
        if isinstance(urls, list):
            return {**data, "urlCount": len(urls)}
        return data

    def to_context_payload(self) -> dict[str, Any]:
        """Serialize back to the Context.dev count-only response shape."""
        payload: dict[str, Any] = {
            "success": self.success,
            "domain": self.domain,
            "urlCount": self.url_count,
            "request_id": str(self.request_id),
        }
        if self.key_metadata is not None:
            payload["key_metadata"] = self.key_metadata.model_dump()
        if self.partial:
            payload["partial"] = True
        return payload

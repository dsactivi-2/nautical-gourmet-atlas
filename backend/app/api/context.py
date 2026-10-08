from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.config import settings
from app.models.user import User
from app.schemas.context_dev import DomainUrlCount
from app.services.auth import get_current_user
from app.services.context_dev import (
    DEFAULT_BASE_URL,
    ContextDevAPIError,
    ContextDevClient,
    ContextDevConfigError,
    ContextDevRequestError,
    ContextDevResponseError,
    status_for_api_error,
)

router = APIRouter()


def get_context_client() -> ContextDevClient:
    try:
        return ContextDevClient(
            api_key=settings.CONTEXT_DEV_API_KEY,
            base_url=settings.CONTEXT_DEV_BASE_URL or DEFAULT_BASE_URL,
        )
    except ContextDevConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get("/url-count", response_model=DomainUrlCount)
async def domain_url_count(
    domain: str = Query(
        ...,
        min_length=3,
        max_length=253,
        description="Bare domain to count, for example cookbook.openai.com",
        example="cookbook.openai.com",
    ),
    include_subdomains: bool = Query(False, description="Include URLs on subdomains"),
    max_links: int | None = Query(
        None,
        ge=1,
        le=100_000,
        description="Maximum number of URLs Context.dev should consider",
    ),
    url_regex: str | None = Query(
        None,
        max_length=256,
        description="RE2 pattern; only matching URLs are counted",
    ),
    search: str | None = Query(
        None,
        min_length=2,
        max_length=200,
        description="Topic filter, most relevant URLs first",
    ),
    _: User = Depends(get_current_user),
    context_client: ContextDevClient = Depends(get_context_client),
) -> DomainUrlCount:
    """Count indexed URLs for a domain via Context.dev Map URLs."""
    try:
        return await context_client.count_urls(
            domain,
            include_subdomains=include_subdomains,
            max_links=max_links,
            url_regex=url_regex,
            search=search,
        )
    except ContextDevRequestError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ContextDevConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except ContextDevAPIError as exc:
        raise HTTPException(
            status_code=status_for_api_error(exc),
            detail=exc.public_detail(),
        ) from exc
    except ContextDevResponseError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

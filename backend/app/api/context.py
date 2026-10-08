from fastapi import APIRouter, Depends, HTTPException

from app.config import settings
from app.models.user import User
from app.schemas.context_map import MapUrlsRequest, MapUrlsResult
from app.services.auth import get_current_user
from app.services.context_dev import ContextDevClient, ContextDevError, public_status

router = APIRouter()


def get_context_client() -> ContextDevClient:
    if not settings.CONTEXT_DEV_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Context.dev is not configured",
        )
    return ContextDevClient(
        api_key=settings.CONTEXT_DEV_API_KEY,
        base_url=settings.CONTEXT_DEV_BASE_URL,
    )


@router.post("/map", response_model=MapUrlsResult)
async def map_domain_urls(
    body: MapUrlsRequest,
    _: User = Depends(get_current_user),
    client: ContextDevClient = Depends(get_context_client),
) -> MapUrlsResult:
    """Map a domain with Context.dev ``GET /web/urls``.

    Accepts the example payload ``{"domain": "cookbook.openai.com", "maxLinks": "150"}``.
    """
    try:
        return await client.map_urls(body)
    except ContextDevError as exc:
        raise HTTPException(
            status_code=public_status(exc.status_code),
            detail={
                "message": exc.message,
                "error_code": exc.error_code,
                "request_id": exc.request_id,
            },
        ) from exc

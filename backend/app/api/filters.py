from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.database import get_db
from app.models.filter import Filter
from app.schemas.filter import FilterResponse
from app.services.language import get_language

router = APIRouter()


@router.get("", response_model=List[FilterResponse])
async def list_filters(
    request: Request,
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: AsyncSession = Depends(get_db),
):
    """List filters, optionally filtered by category"""
    lang = get_language(request)

    query = select(Filter).where(Filter.is_active == True)

    if category_id:
        query = query.where(Filter.category_id == category_id)

    query = query.order_by(Filter.sort_order)
    result = await db.execute(query)
    filters = result.scalars().all()

    return [
        FilterResponse(
            id=f.id,
            category_id=f.category_id,
            slug=f.slug,
            name=f.get_name(lang),
            icon=f.icon,
            sort_order=f.sort_order,
        )
        for f in filters
    ]

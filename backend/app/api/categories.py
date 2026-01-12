from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryResponse
from app.services.language import get_language

router = APIRouter()


@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """List all active categories"""
    lang = get_language(request)

    result = await db.execute(
        select(Category)
        .where(Category.is_active == True)
        .order_by(Category.sort_order)
    )
    categories = result.scalars().all()

    return [
        CategoryResponse(
            id=cat.id,
            slug=cat.slug,
            name=cat.get_name(lang),
            description=cat.get_description(lang),
            icon=cat.icon,
            sort_order=cat.sort_order,
        )
        for cat in categories
    ]

from fastapi import APIRouter, Depends, Request, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.database import get_db
from app.models.treasure import Treasure, TreasureCategory, TreasurePartner
from app.models.partner import Partner
from app.schemas.treasure import TreasureListItem, TreasureDetail, RelatedPartnerResponse
from app.services.language import get_language

router = APIRouter()


@router.get("", response_model=List[TreasureListItem])
async def list_treasures(
    request: Request,
    category: Optional[TreasureCategory] = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_db),
):
    """List treasures, optionally filtered by category"""
    lang = get_language(request)

    query = select(Treasure).where(Treasure.is_active == True)

    if category:
        query = query.where(Treasure.category == category)

    query = query.order_by(Treasure.sort_order)

    result = await db.execute(query)
    treasures = result.scalars().all()

    return [
        TreasureListItem(
            id=t.id,
            slug=t.slug,
            title=t.get_title(lang),
            category=t.category,
            image_url=t.image_url,
        )
        for t in treasures
    ]


@router.get("/categories")
async def list_treasure_categories():
    """List available treasure categories"""
    return [
        {"slug": cat.value, "name": cat.value.replace("_", " ").title()}
        for cat in TreasureCategory
    ]


@router.get("/{treasure_id}", response_model=TreasureDetail)
async def get_treasure(
    treasure_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Get treasure details by ID"""
    lang = get_language(request)

    result = await db.execute(
        select(Treasure)
        .options(
            selectinload(Treasure.related_partners).selectinload(TreasurePartner.partner).selectinload(Partner.images)
        )
        .where(Treasure.id == treasure_id, Treasure.is_active == True)
    )
    treasure = result.scalar_one_or_none()

    if not treasure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Treasure not found",
        )

    related_partners = [
        RelatedPartnerResponse(
            id=tp.partner.id,
            slug=tp.partner.slug,
            name=tp.partner.get_name(lang),
            is_premium=tp.partner.is_premium,
            primary_image=(
                next((img.url for img in tp.partner.images if img.is_primary), None)
                or (tp.partner.images[0].url if tp.partner.images else None)
            ),
        )
        for tp in treasure.related_partners
        if tp.partner and tp.partner.is_active
    ]

    return TreasureDetail(
        id=treasure.id,
        slug=treasure.slug,
        title=treasure.get_title(lang),
        content=treasure.get_content(lang),
        category=treasure.category,
        image_url=treasure.image_url,
        video_url=treasure.video_url,
        related_partners=related_partners,
        created_at=treasure.created_at,
    )

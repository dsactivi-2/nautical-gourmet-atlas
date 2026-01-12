from fastapi import APIRouter, Depends, Request, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from geoalchemy2.functions import ST_MakeEnvelope, ST_Within

from app.database import get_db
from app.models.partner import Partner, PartnerImage, PartnerFilter
from app.models.category import Category
from app.models.filter import Filter
from app.models.favorite import Favorite
from app.models.user import User
from app.schemas.partner import PartnerListItem, PartnerDetail, PartnerImageResponse, PartnerFilterResponse
from app.services.language import get_language
from app.services.auth import get_current_user_optional

router = APIRouter()


@router.get("", response_model=List[PartnerListItem])
async def list_partners(
    request: Request,
    bbox: Optional[str] = Query(None, description="Bounding box: minLng,minLat,maxLng,maxLat"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    filter_ids: Optional[str] = Query(None, description="Comma-separated filter IDs"),
    q: Optional[str] = Query(None, description="Search query"),
    premium_only: bool = Query(False, description="Show only premium partners"),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    List partners with filtering.
    Supports bbox for map-based queries, category, filters, search, and premium filter.
    """
    lang = get_language(request)

    query = (
        select(Partner)
        .options(selectinload(Partner.images), selectinload(Partner.category))
        .where(Partner.is_active == True)
    )

    # BBOX filter (PostGIS)
    if bbox:
        try:
            min_lng, min_lat, max_lng, max_lat = map(float, bbox.split(","))
            envelope = ST_MakeEnvelope(min_lng, min_lat, max_lng, max_lat, 4326)
            query = query.where(ST_Within(Partner.location, envelope))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid bbox format. Expected: minLng,minLat,maxLng,maxLat",
            )

    # Category filter
    if category_id:
        query = query.where(Partner.category_id == category_id)

    # Filter IDs
    if filter_ids:
        try:
            fids = [int(x) for x in filter_ids.split(",")]
            # Subquery: partners that have ALL the specified filters
            subq = (
                select(PartnerFilter.partner_id)
                .where(PartnerFilter.filter_id.in_(fids))
                .group_by(PartnerFilter.partner_id)
                .having(func.count(PartnerFilter.filter_id) == len(fids))
            )
            query = query.where(Partner.id.in_(subq))
        except ValueError:
            pass

    # Search query
    if q:
        search_term = f"%{q}%"
        query = query.where(
            (Partner.name_en.ilike(search_term))
            | (Partner.name_hr.ilike(search_term))
            | (Partner.name_de.ilike(search_term))
            | (Partner.city.ilike(search_term))
        )

    # Premium filter
    if premium_only:
        query = query.where(Partner.is_premium == True)

    # Pagination
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    partners = result.scalars().all()

    # Get user's favorites for marking
    favorite_partner_ids = set()
    if current_user:
        fav_result = await db.execute(
            select(Favorite.partner_id).where(Favorite.user_id == current_user.id)
        )
        favorite_partner_ids = {row[0] for row in fav_result.fetchall()}

    return [
        PartnerListItem(
            id=p.id,
            slug=p.slug,
            name=p.get_name(lang),
            category_id=p.category_id,
            category_slug=p.category.slug if p.category else None,
            latitude=p.latitude,
            longitude=p.longitude,
            city=p.city,
            is_premium=p.is_premium,
            discount_percent=p.discount_percent,
            primary_image=next((img.url for img in p.images if img.is_primary), None)
            or (p.images[0].url if p.images else None),
            is_favorite=p.id in favorite_partner_ids,
        )
        for p in partners
    ]


@router.get("/{partner_id}", response_model=PartnerDetail)
async def get_partner(
    partner_id: int,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Get partner details by ID"""
    lang = get_language(request)

    result = await db.execute(
        select(Partner)
        .options(
            selectinload(Partner.images),
            selectinload(Partner.filters).selectinload(PartnerFilter.filter),
            selectinload(Partner.category),
        )
        .where(Partner.id == partner_id, Partner.is_active == True)
    )
    partner = result.scalar_one_or_none()

    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found",
        )

    # Check if favorited by current user
    is_favorite = False
    if current_user:
        fav_result = await db.execute(
            select(Favorite).where(
                Favorite.user_id == current_user.id,
                Favorite.partner_id == partner_id,
            )
        )
        is_favorite = fav_result.scalar_one_or_none() is not None

    return PartnerDetail(
        id=partner.id,
        slug=partner.slug,
        name=partner.get_name(lang),
        description=partner.get_description(lang),
        category_id=partner.category_id,
        category_slug=partner.category.slug if partner.category else None,
        category_name=partner.category.get_name(lang) if partner.category else None,
        latitude=partner.latitude,
        longitude=partner.longitude,
        address=partner.address,
        city=partner.city,
        country=partner.country,
        phone=partner.phone,
        email=partner.email,
        website=partner.website,
        is_premium=partner.is_premium,
        discount_percent=partner.discount_percent,
        pin_code=partner.pin_code if current_user else None,  # Only show PIN to authenticated users
        opening_hours=partner.opening_hours,
        images=[
            PartnerImageResponse(
                id=img.id,
                url=img.url,
                alt_text=img.alt_text,
                is_primary=img.is_primary,
                sort_order=img.sort_order,
            )
            for img in sorted(partner.images, key=lambda x: (not x.is_primary, x.sort_order))
        ],
        filters=[
            PartnerFilterResponse(
                id=pf.filter.id,
                slug=pf.filter.slug,
                name=pf.filter.get_name(lang),
            )
            for pf in partner.filters
            if pf.filter
        ],
        is_favorite=is_favorite,
        created_at=partner.created_at,
    )

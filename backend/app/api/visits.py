from fastapi import APIRouter, Depends, Request, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.database import get_db
from app.models.visit import Visit
from app.models.partner import Partner
from app.models.user import User
from app.schemas.visit import VisitCreate, VisitUpdate, VisitResponse
from app.services.auth import get_current_user
from app.services.language import get_language

router = APIRouter()


@router.get("", response_model=List[VisitResponse])
async def list_visits(
    request: Request,
    discount_used_only: bool = Query(False, description="Show only visits where discount was used"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List current user's visits (history)"""
    lang = get_language(request)

    query = (
        select(Visit)
        .options(selectinload(Visit.partner))
        .where(Visit.user_id == current_user.id)
    )

    if discount_used_only:
        query = query.where(Visit.discount_used == True)

    query = query.order_by(Visit.visited_at.desc())

    result = await db.execute(query)
    visits = result.scalars().all()

    return [
        VisitResponse(
            id=v.id,
            partner_id=v.partner_id,
            partner_name=v.partner.get_name(lang) if v.partner else None,
            partner_slug=v.partner.slug if v.partner else None,
            discount_used=v.discount_used,
            visited_at=v.visited_at,
        )
        for v in visits
    ]


@router.post("", response_model=VisitResponse, status_code=status.HTTP_201_CREATED)
async def create_visit(
    visit_data: VisitCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a visit record"""
    lang = get_language(request)

    # Check if partner exists
    partner_result = await db.execute(
        select(Partner).where(
            Partner.id == visit_data.partner_id,
            Partner.is_active == True,
        )
    )
    partner = partner_result.scalar_one_or_none()

    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found",
        )

    # Create visit
    visit = Visit(
        user_id=current_user.id,
        partner_id=visit_data.partner_id,
        discount_used=visit_data.discount_used,
    )
    db.add(visit)
    await db.commit()
    await db.refresh(visit)

    return VisitResponse(
        id=visit.id,
        partner_id=visit.partner_id,
        partner_name=partner.get_name(lang),
        partner_slug=partner.slug,
        discount_used=visit.discount_used,
        visited_at=visit.visited_at,
    )


@router.patch("/{visit_id}", response_model=VisitResponse)
async def update_visit(
    visit_id: int,
    visit_update: VisitUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update visit (e.g., mark discount as used)"""
    lang = get_language(request)

    result = await db.execute(
        select(Visit)
        .options(selectinload(Visit.partner))
        .where(Visit.id == visit_id, Visit.user_id == current_user.id)
    )
    visit = result.scalar_one_or_none()

    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visit not found",
        )

    visit.discount_used = visit_update.discount_used
    await db.commit()
    await db.refresh(visit)

    return VisitResponse(
        id=visit.id,
        partner_id=visit.partner_id,
        partner_name=visit.partner.get_name(lang) if visit.partner else None,
        partner_slug=visit.partner.slug if visit.partner else None,
        discount_used=visit.discount_used,
        visited_at=visit.visited_at,
    )

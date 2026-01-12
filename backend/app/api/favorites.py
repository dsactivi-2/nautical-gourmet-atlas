from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.models.favorite import Favorite
from app.models.partner import Partner
from app.models.user import User
from app.schemas.favorite import FavoriteCreate, FavoriteResponse
from app.services.auth import get_current_user
from app.services.language import get_language

router = APIRouter()


@router.get("", response_model=List[FavoriteResponse])
async def list_favorites(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List current user's favorites"""
    lang = get_language(request)

    result = await db.execute(
        select(Favorite)
        .options(selectinload(Favorite.partner).selectinload(Partner.images))
        .where(Favorite.user_id == current_user.id)
        .order_by(Favorite.created_at.desc())
    )
    favorites = result.scalars().all()

    return [
        FavoriteResponse(
            id=fav.id,
            partner_id=fav.partner_id,
            partner_name=fav.partner.get_name(lang) if fav.partner else None,
            partner_slug=fav.partner.slug if fav.partner else None,
            partner_image=(
                next((img.url for img in fav.partner.images if img.is_primary), None)
                or (fav.partner.images[0].url if fav.partner and fav.partner.images else None)
            ),
            partner_is_premium=fav.partner.is_premium if fav.partner else False,
            partner_category_slug=None,  # Could load via category relation
            created_at=fav.created_at,
        )
        for fav in favorites
    ]


@router.post("", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    favorite_data: FavoriteCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add partner to favorites"""
    lang = get_language(request)

    # Check if partner exists
    partner_result = await db.execute(
        select(Partner)
        .options(selectinload(Partner.images))
        .where(Partner.id == favorite_data.partner_id, Partner.is_active == True)
    )
    partner = partner_result.scalar_one_or_none()

    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found",
        )

    # Check if already favorited
    existing = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.partner_id == favorite_data.partner_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Partner already in favorites",
        )

    # Create favorite
    favorite = Favorite(user_id=current_user.id, partner_id=favorite_data.partner_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)

    return FavoriteResponse(
        id=favorite.id,
        partner_id=favorite.partner_id,
        partner_name=partner.get_name(lang),
        partner_slug=partner.slug,
        partner_image=(
            next((img.url for img in partner.images if img.is_primary), None)
            or (partner.images[0].url if partner.images else None)
        ),
        partner_is_premium=partner.is_premium,
        partner_category_slug=None,
        created_at=favorite.created_at,
    )


@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    favorite_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove partner from favorites"""
    result = await db.execute(
        select(Favorite).where(
            Favorite.id == favorite_id,
            Favorite.user_id == current_user.id,
        )
    )
    favorite = result.scalar_one_or_none()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found",
        )

    await db.delete(favorite)
    await db.commit()

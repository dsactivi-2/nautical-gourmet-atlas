from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.treasure import TreasureCategory


class RelatedPartnerResponse(BaseModel):
    id: int
    slug: str
    name: str
    is_premium: bool
    primary_image: Optional[str] = None

    class Config:
        from_attributes = True


class TreasureListItem(BaseModel):
    id: int
    slug: str
    title: str  # Localized
    category: TreasureCategory
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


class TreasureDetail(BaseModel):
    id: int
    slug: str
    title: str  # Localized
    content: Optional[str] = None  # Localized
    category: TreasureCategory
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    related_partners: List[RelatedPartnerResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class PartnerImageResponse(BaseModel):
    id: int
    url: str
    alt_text: Optional[str] = None
    is_primary: bool
    sort_order: int

    class Config:
        from_attributes = True


class PartnerFilterResponse(BaseModel):
    id: int
    slug: str
    name: str

    class Config:
        from_attributes = True


class PartnerListItem(BaseModel):
    id: int
    slug: str
    name: str  # Localized
    category_id: int
    category_slug: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    is_premium: bool
    discount_percent: int
    primary_image: Optional[str] = None
    is_favorite: bool = False

    class Config:
        from_attributes = True


class PartnerDetail(BaseModel):
    id: int
    slug: str
    name: str  # Localized
    description: Optional[str] = None  # Localized
    category_id: int
    category_slug: Optional[str] = None
    category_name: Optional[str] = None

    # Location
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

    # Contact
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None

    # Premium & Discount
    is_premium: bool
    discount_percent: int
    pin_code: Optional[str] = None  # Only shown to authenticated users

    # Opening hours
    opening_hours: Optional[Any] = None

    # Relations
    images: List[PartnerImageResponse] = []
    filters: List[PartnerFilterResponse] = []

    # User-specific
    is_favorite: bool = False

    created_at: datetime

    class Config:
        from_attributes = True

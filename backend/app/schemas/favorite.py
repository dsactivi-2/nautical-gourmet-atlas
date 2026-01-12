from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FavoriteCreate(BaseModel):
    partner_id: int


class FavoriteResponse(BaseModel):
    id: int
    partner_id: int
    partner_name: Optional[str] = None
    partner_slug: Optional[str] = None
    partner_image: Optional[str] = None
    partner_is_premium: bool = False
    partner_category_slug: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

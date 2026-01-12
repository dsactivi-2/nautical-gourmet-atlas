from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class VisitCreate(BaseModel):
    partner_id: int
    discount_used: bool = False


class VisitUpdate(BaseModel):
    discount_used: bool


class VisitResponse(BaseModel):
    id: int
    partner_id: int
    partner_name: Optional[str] = None
    partner_slug: Optional[str] = None
    discount_used: bool
    visited_at: datetime

    class Config:
        from_attributes = True

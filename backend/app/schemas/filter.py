from pydantic import BaseModel
from typing import Optional


class FilterResponse(BaseModel):
    id: int
    category_id: int
    slug: str
    name: str  # Localized based on Accept-Language
    icon: Optional[str] = None
    sort_order: int

    class Config:
        from_attributes = True

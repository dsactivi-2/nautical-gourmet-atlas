from pydantic import BaseModel
from typing import Optional


class CategoryResponse(BaseModel):
    id: int
    slug: str
    name: str  # Localized based on Accept-Language
    description: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int

    class Config:
        from_attributes = True

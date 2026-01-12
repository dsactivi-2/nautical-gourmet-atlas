from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Filter(Base):
    __tablename__ = "filters"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    slug = Column(String(100), index=True, nullable=False)

    # Localized names
    name_hr = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=False)
    name_de = Column(String(200), nullable=False)

    icon = Column(String(100), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    category = relationship("Category", back_populates="filters")
    partners = relationship("PartnerFilter", back_populates="filter")

    def get_name(self, lang: str = "en") -> str:
        return getattr(self, f"name_{lang}", self.name_en) or self.name_en

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)

    # Localized names
    name_hr = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=False)
    name_de = Column(String(200), nullable=False)

    # Localized descriptions
    description_hr = Column(Text, nullable=True)
    description_en = Column(Text, nullable=True)
    description_de = Column(Text, nullable=True)

    icon = Column(String(100), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    filters = relationship("Filter", back_populates="category")
    partners = relationship("Partner", back_populates="category")

    def get_name(self, lang: str = "en") -> str:
        return getattr(self, f"name_{lang}", self.name_en) or self.name_en

    def get_description(self, lang: str = "en") -> str:
        return getattr(self, f"description_{lang}", self.description_en) or self.description_en

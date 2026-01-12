from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.database import Base


class Partner(Base):
    __tablename__ = "partners"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    # Basic info
    slug = Column(String(200), unique=True, index=True, nullable=False)

    # Localized names
    name_hr = Column(String(300), nullable=False)
    name_en = Column(String(300), nullable=False)
    name_de = Column(String(300), nullable=False)

    # Localized descriptions
    description_hr = Column(Text, nullable=True)
    description_en = Column(Text, nullable=True)
    description_de = Column(Text, nullable=True)

    # Location - PostGIS Point
    location = Column(Geometry("POINT", srid=4326), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)

    # Contact
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)

    # Premium & Discount
    is_premium = Column(Boolean, default=False)
    discount_percent = Column(Integer, default=0)
    pin_code = Column(String(10), nullable=True)  # PIN for discount redemption

    # Opening hours as JSON
    opening_hours = Column(JSON, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("Category", back_populates="partners")
    images = relationship("PartnerImage", back_populates="partner", cascade="all, delete-orphan")
    filters = relationship("PartnerFilter", back_populates="partner", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="partner", cascade="all, delete-orphan")
    visits = relationship("Visit", back_populates="partner", cascade="all, delete-orphan")

    def get_name(self, lang: str = "en") -> str:
        return getattr(self, f"name_{lang}", self.name_en) or self.name_en

    def get_description(self, lang: str = "en") -> str:
        return getattr(self, f"description_{lang}", self.description_en) or self.description_en


class PartnerImage(Base):
    __tablename__ = "partner_images"

    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, ForeignKey("partners.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(500), nullable=False)
    alt_text = Column(String(200), nullable=True)
    is_primary = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    partner = relationship("Partner", back_populates="images")


class PartnerFilter(Base):
    __tablename__ = "partner_filters"

    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, ForeignKey("partners.id", ondelete="CASCADE"), nullable=False)
    filter_id = Column(Integer, ForeignKey("filters.id", ondelete="CASCADE"), nullable=False)

    partner = relationship("Partner", back_populates="filters")
    filter = relationship("Filter", back_populates="partners")

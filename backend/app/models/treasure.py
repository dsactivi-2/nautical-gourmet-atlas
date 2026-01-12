from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class TreasureCategory(str, enum.Enum):
    wines = "wines"
    traditional_dishes = "traditional_dishes"
    products = "products"
    crafts_souvenirs = "crafts_souvenirs"


class Treasure(Base):
    __tablename__ = "treasures"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(200), unique=True, index=True, nullable=False)
    category = Column(SQLEnum(TreasureCategory), nullable=False)

    # Localized titles
    title_hr = Column(String(300), nullable=False)
    title_en = Column(String(300), nullable=False)
    title_de = Column(String(300), nullable=False)

    # Localized content
    content_hr = Column(Text, nullable=True)
    content_en = Column(Text, nullable=True)
    content_de = Column(Text, nullable=True)

    # Media
    image_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    related_partners = relationship("TreasurePartner", back_populates="treasure", cascade="all, delete-orphan")

    def get_title(self, lang: str = "en") -> str:
        return getattr(self, f"title_{lang}", self.title_en) or self.title_en

    def get_content(self, lang: str = "en") -> str:
        return getattr(self, f"content_{lang}", self.content_en) or self.content_en


class TreasurePartner(Base):
    __tablename__ = "treasure_partners"

    id = Column(Integer, primary_key=True, index=True)
    treasure_id = Column(Integer, ForeignKey("treasures.id", ondelete="CASCADE"), nullable=False)
    partner_id = Column(Integer, ForeignKey("partners.id", ondelete="CASCADE"), nullable=False)

    treasure = relationship("Treasure", back_populates="related_partners")
    partner = relationship("Partner")

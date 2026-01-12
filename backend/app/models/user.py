from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
import enum


class Gender(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    country = Column(String(100), nullable=True)
    dob = Column(Date, nullable=True)
    gender = Column(SQLEnum(Gender), nullable=True)
    is_nautical = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

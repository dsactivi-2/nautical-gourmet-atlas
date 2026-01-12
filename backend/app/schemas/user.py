from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional
from app.models.user import Gender


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    country: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[Gender] = None
    is_nautical: bool = False


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    country: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[Gender] = None
    is_nautical: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    country: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[Gender] = None
    is_nautical: Optional[bool] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

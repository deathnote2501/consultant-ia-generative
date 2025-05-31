from typing import Optional, List, Dict
from uuid import UUID as PyUUID
from datetime import datetime # Will be needed for the new fields eventually

from pydantic import BaseModel, EmailStr # HttpUrl might be needed by other models
from fastapi_users import schemas
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import String, Boolean, DateTime # DateTime will be needed

# Define a Base for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# SQLAlchemy User Model for FastAPI-Users
class User(SQLAlchemyBaseUserTableUUID, Base):
    # __tablename__ = "user" # This was added for debug, fastapi-users provides it
    # fastapi-users provides: id, email, hashed_password, is_active, is_superuser, is_verified

    # New fields for submitted email verification
    submitted_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    email_verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True, index=True)
    email_verification_token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

# --- Pydantic User Schemas for FastAPI-Users ---
class UserRead(schemas.BaseUser[PyUUID]):
    # Inherits id, email, is_active, is_superuser, is_verified from BaseUser
    submitted_email: Optional[EmailStr] = None # New field added

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass

# --- Existing Pydantic models for Course and Slide ---
class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseRead(CourseBase):
    id: int

class SlideBase(BaseModel):
    course_id: int
    order_index: int
    template_type: str
    content_json: Dict
    specific_prompt: Optional[str] = None
    suggested_messages_json: Optional[List[str]] = None

class SlideCreate(SlideBase):
    pass

class SlideRead(SlideBase):
    id: int

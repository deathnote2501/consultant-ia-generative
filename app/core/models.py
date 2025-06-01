from typing import Optional, List, Dict
from uuid import UUID as PyUUID
from datetime import datetime # Will be needed for the new fields eventually

from pydantic import BaseModel, EmailStr # HttpUrl might be needed by other models
from fastapi_users import schemas
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase # Add relationship if uncommenting relationships below
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, UniqueConstraint # Added ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID # For user_id
from sqlalchemy.sql import func # For server_default=func.now()

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

# Basic Course SQLAlchemy Model
class Course(Base):
    __tablename__ = "course"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    # description: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Example if needed

    # Placeholder for relationship to subscriptions, if needed later
    # subscriptions: Mapped[List["Subscription"]] = relationship(back_populates="course")

# --- Subscription SQLAlchemy Model ---
class Subscription(Base):
    __tablename__ = "subscription"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[PyUUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("course.id"), nullable=False, index=True)

    stripe_customer_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    stripe_subscription_id: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)

    plan_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g., 'weekly', 'monthly', 'annual'
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # e.g., 'active', 'canceled', 'past_due'

    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships (optional for now, but good to define if User/Course models are updated with back_populates)
    # user: Mapped["User"] = relationship() # back_populates="subscriptions"
    # course: Mapped["Course"] = relationship() # back_populates="subscriptions"

    __table_args__ = (
        UniqueConstraint('stripe_subscription_id', name='uq_subscription_stripe_subscription_id'),
        # Composite unique constraint for user_id and course_id if a user can only subscribe once to a course
        # UniqueConstraint('user_id', 'course_id', name='uq_user_course_subscription'),
    )

# --- Pydantic User Schemas for FastAPI-Users ---
class UserRead(schemas.BaseUser[PyUUID]):
    # Inherits id, email, is_active, is_superuser, is_verified from BaseUser
    submitted_email: Optional[EmailStr] = None # New field added

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass

# --- Subscription Pydantic Schemas ---

class SubscriptionBase(BaseModel):
    user_id: PyUUID # Matches User.id type
    course_id: int  # Matches Course.id type
    stripe_customer_id: str
    stripe_subscription_id: str
    plan_type: str  # e.g., 'weekly', 'monthly', 'annual'
    status: str     # e.g., 'active', 'canceled', 'past_due', 'incomplete'
    current_period_start: datetime
    current_period_end: datetime

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionRead(SubscriptionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # For Pydantic v2

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

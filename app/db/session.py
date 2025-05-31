from typing import AsyncGenerator
from fastapi import Depends # Added as per requirement
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase # Already imported in models.py, but good practice for standalone module
from fastapi_users.db import SQLAlchemyUserDatabase
from app.core.config import settings
from app.core.models import User, Base # Ensure Base is imported if User model relies on it

# Database URL from settings
DATABASE_URL = settings.DATABASE_URL

# Create async engine
engine = create_async_engine(DATABASE_URL)

# Async session maker
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Dependency to get DB session
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# SQLAlchemyUserDatabase provider
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

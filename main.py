from fastapi import FastAPI, Depends # Ensure Depends is imported
from contextlib import asynccontextmanager # For lifespan events if needed for DB
from uuid import UUID # For User ID type

from app.core.config import settings
from app.core.models import User, UserRead, UserCreate, UserUpdate # SQLAlchemy User and Pydantic Schemas
from app.db.session import get_async_session, get_user_db # DB session and user_db getter

from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

# --- Bearer Transport and JWT Strategy ---
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.JWT_SECRET_KEY, lifetime_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60) # ACCESS_TOKEN_EXPIRE_MINUTES is in minutes, lifetime_seconds in secs

# --- Authentication Backend ---
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# --- FastAPIUsers Instance ---
# The User model is app.core.models.User
# The User ID type is UUID (from fastapi_users.db.SQLAlchemyBaseUserTableUUID)
# The UserRead schema is app.core.models.UserRead
# The UserCreate schema is app.core.models.UserCreate
# The UserUpdate schema is app.core.models.UserUpdate
fastapi_users = FastAPIUsers[User, UUID, UserRead, UserCreate, UserUpdate](
    get_user_manager=get_user_db, # This should be get_user_manager, which depends on get_user_db
    auth_backends=[auth_backend],
)

# --- Lifespan (optional, for DB connection pool or other setup/teardown) ---
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup: e.g., create DB tables if not using Alembic, or init connection pool
#     # await create_db_and_tables() # Example if you had such a function
#     print("Application startup...")
#     yield
#     # Shutdown: e.g., close connection pool
#     print("Application shutdown...")

# --- FastAPI App Initialization ---
# app = FastAPI(lifespan=lifespan) # If using lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    # openapi_url=f"{settings.API_V1_STR}/openapi.json" # Example if you have versioned API
)

# Import the new router
from app.api.endpoints import users as users_endpoints_router # New import


# --- Include Routers ---
# Auth routes
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt", # Matches BearerTransport tokenUrl prefix
    tags=["auth"],
)

# Register routes
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# Reset password routes (optional, requires email setup)
# app.include_router(
#     fastapi_users.get_reset_password_router(),
#     prefix="/auth",
#     tags=["auth"],
# )

# Verify routes (optional, requires email setup)
# app.include_router(
#     fastapi_users.get_verify_router(UserRead),
#     prefix="/auth",
#     tags=["auth"],
# )

# Users routes
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# Include the new custom users router
app.include_router(
    users_endpoints_router.router,
    prefix="/users", # This will make the endpoint available at /users/me/submit-email
    tags=["users-custom"], # A new tag to distinguish from default fastapi-users "users" tag
)


# --- Original Ping Endpoint ---
@app.get("/ping")
async def ping():
    return {"ping": "pong"}

# --- Original Root Endpoint ---
@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}"}

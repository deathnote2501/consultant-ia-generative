from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select # select is in sqlalchemy directly in newer versions
from datetime import datetime, timezone

from app.core.models import User # SQLAlchemy User model
from app.db.session import get_async_session
# Attempt to import auth_backend from main.py
# This can lead to circular imports if main.py also imports this router.
# A better approach would be a shared dependency or app state.
try:
    from app.main import auth_backend
except ImportError:
    # This is a fallback/placeholder if direct import fails.
    # This will cause runtime errors if not replaced by a valid AuthenticationBackend instance.
    class PlaceholderAuthBackend:
        def get_strategy(self): raise NotImplementedError("Auth backend not available")
        async def login(self, strategy, user): raise NotImplementedError("Auth backend not available")
    auth_backend = PlaceholderAuthBackend()

from app.api.schemas.auth_schemas import TokenResponse # Response schema

router = APIRouter()

@router.get(
    "/verify-submitted-email",
    response_model=TokenResponse,
    name="auth:verify_submitted_email",
    tags=["auth"],
)
async def verify_submitted_email(
    token: str = Query(...),
    session: AsyncSession = Depends(get_async_session),
    # strategy: JWTStrategy = Depends(auth_backend.get_strategy) # Alternative way to get strategy
):
    """
    Verifies a submitted email address using a token sent to the user.
    If successful, updates the user's email, marks them as verified,
    and returns new access and refresh tokens.
    """
    if not token: # Should be caught by Query(...) if token is mandatory.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token is missing.",
        )

    # 1. Find user by token
    stmt = select(User).where(User.email_verification_token == token)
    result = await session.execute(stmt)
    user: User | None = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token.",
        )

    # 2. Check token expiry
    if user.email_verification_token_expires_at is None or \
       user.email_verification_token_expires_at < datetime.now(timezone.utc):
        # Optionally, clear the expired token from the user record here
        user.email_verification_token = None
        user.email_verification_token_expires_at = None
        # user.submitted_email = None # Decide whether to clear this
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired.",
        )

    # 3. Token is valid, update user
    if user.submitted_email is None:
        # This case should ideally not happen if token is valid, means submitted_email was cleared somehow
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No submitted email found for this token. Please try submitting your email again.",
        )

    user.email = user.submitted_email # Promote submitted email to primary
    user.is_verified = True # Mark user as verified (standard fastapi-users field)

    # Clear verification fields
    user.submitted_email = None
    user.email_verification_token = None
    user.email_verification_token_expires_at = None

    session.add(user)
    await session.commit()
    await session.refresh(user)

    # 4. Generate new access and refresh tokens
    # This requires the auth_backend instance from main.py
    # The type of strategy would be JWTStrategy based on main.py setup
    strategy = auth_backend.get_strategy()

    # The login method of AuthenticationBackend creates and returns a BearerResponse
    # which should contain access_token, refresh_token, and token_type.
    response_from_login = await auth_backend.login(strategy, user)

    if not hasattr(response_from_login, 'access_token') or not hasattr(response_from_login, 'refresh_token'):
        # This might happen if the BearerResponse from auth_backend.login doesn't include refresh_token
        # or if the login failed for some reason not caught by an exception.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate tokens after email verification."
        )

    return TokenResponse(
        access_token=response_from_login.access_token,
        refresh_token=response_from_login.refresh_token,
        token_type=response_from_login.token_type
    )

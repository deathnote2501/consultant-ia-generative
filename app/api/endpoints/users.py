from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
# from pydantic import EmailStr # Not directly used, SubmitEmailRequest handles validation
import secrets
from datetime import datetime, timedelta, timezone

from app.core.models import User # SQLAlchemy User model
# Attempt to import fastapi_users instance from main.py
# This can lead to circular imports if main.py also imports this router.
# A better approach would be a shared dependency or app state.
# For now, proceeding with direct import for simplicity of this subtask.
try:
    from app.main import fastapi_users
except ImportError:
    # This is a fallback/placeholder if direct import fails.
    # In a real scenario, current_user dependency needs to be properly resolved.
    # This placeholder will likely cause runtime errors if not replaced by a valid dependency.
    defcurrent_active_user():
        raise NotImplementedError(
            "current_active_user dependency is not available. "
            "Check circular imports or FastAPIUsers instance accessibility."
        )
    current_active_user = Depends(current_active_user)


from app.db.session import get_async_session
from app.core.config import settings
from app.core.ports.email_sender import EmailSenderInterface
from app.infrastructure.services.brevo_sender import BrevoEmailSender
from app.api.schemas.user_schemas import SubmitEmailRequest, MessageResponse

router = APIRouter()

# Dependency for Email Sender
async def get_email_sender() -> EmailSenderInterface:
    # In a real app, this might come from a more complex DI system or app state.
    # For now, directly instantiating. Consider settings check for API key presence.
    try:
        return BrevoEmailSender()
    except ValueError as e:
        # This happens if BREVO_API_KEY or SENDER_EMAIL is missing/placeholder
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Email service misconfiguration: {e}")


@router.post(
    "/me/submit-email",
    response_model=MessageResponse,
    name="users:submit_email_for_verification",
    tags=["users"],
)
async def submit_email_for_verification(
    request_data: SubmitEmailRequest = Body(...),
    user: User = Depends(fastapi_users.current_user(active=True)), # Using the imported instance
    session: AsyncSession = Depends(get_async_session),
    email_sender: EmailSenderInterface = Depends(get_email_sender)
):
    """
    Allows an authenticated user to submit an email address for verification.
    A verification email will be sent to the submitted address.
    """
    submitted_email = request_data.email

    # 1. Generate verification token and expiry
    token = secrets.token_urlsafe(32)
    # TODO: Make token expiry configurable, e.g., from settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24) # Default 24 hours

    # 2. Update user model with submitted email, token, and expiry
    user.submitted_email = submitted_email
    user.email_verification_token = token
    user.email_verification_token_expires_at = expires_at

    session.add(user)
    await session.commit()
    await session.refresh(user)

    # 3. Construct verification URL
    base_url = str(settings.BASE_URL).rstrip('/')
    verification_url = f"{base_url}/auth/verify-submitted-email?token={token}" # Path to be created later

    # 4. Send verification email
    email_subject = f"Verify your email for {settings.PROJECT_NAME}"
    # TODO: Use an HTML template for the email body
    email_html_content = f"""
    <p>Hello {user.email.split('@')[0]},</p>
    <p>You requested to associate the email address {submitted_email} with your account on {settings.PROJECT_NAME}.</p>
    <p>Please verify this email address by clicking the link below:</p>
    <p><a href="{verification_url}">{verification_url}</a></p>
    <p>This link will expire in 24 hours. After expiry, you may need to resubmit your email address.</p>
    <p>If you did not request this, please ignore this email or contact support if you have concerns.</p>
    <p>Thanks,<br/>The {settings.PROJECT_NAME} Team</p>
    """

    email_sent_successfully = await email_sender.send_email(
        to_email=submitted_email,
        subject=email_subject,
        html_content=email_html_content
        # sender_name and sender_email will use defaults from BrevoEmailSender config
    )

    if not email_sent_successfully:
        # Revert changes to avoid inconsistent state if email fails.
        # This is a simple revert; more complex logic might be needed (e.g., retry queue).
        user.submitted_email = None
        user.email_verification_token = None
        user.email_verification_token_expires_at = None
        session.add(user)
        await session.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email. Please try again later or contact support."
        )

    return MessageResponse(message="Verification email sent successfully. Please check your inbox.")

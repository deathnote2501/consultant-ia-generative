from fastapi import APIRouter, Depends, HTTPException, status, Body
from uuid import UUID as PyUUID # For type hinting User.id
import logging # For logging errors

from app.core.models import User # SQLAlchemy User model
# Attempt to import fastapi_users instance from main.py
# This can lead to circular imports if main.py also imports this router.
# A better approach would be a shared dependency or app state.
try:
    from app.main import fastapi_users
except ImportError:
    # This is a fallback/placeholder if direct import fails.
    # This will cause runtime errors if not replaced by a valid dependency.
    def current_active_user_placeholder():
        raise NotImplementedError(
            "current_active_user dependency is not available. "
            "Check circular imports or FastAPIUsers instance accessibility."
        )
    # To be used as Depends(current_active_user_placeholder)
    # For now, the endpoint will rely on fastapi_users being available.

from app.core.config import settings
from app.core.ports.payment_gateway import PaymentGatewayInterface
from app.infrastructure.services.stripe_adapter import StripeAdapter # Concrete implementation for DI
from app.api.schemas.payment_schemas import CreateCheckoutSessionRequest, CreateCheckoutSessionResponse

logger = logging.getLogger(__name__)
router = APIRouter()

# Dependency for Payment Gateway
async def get_payment_gateway() -> PaymentGatewayInterface:
    # In a real app, this might come from a more complex DI system
    # or be configured based on settings.
    try:
        return StripeAdapter()
    except ValueError as e: # Catch init errors from StripeAdapter (e.g. missing key)
        logger.error(f"Failed to initialize Payment Gateway: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Payment system misconfiguration.")


@router.post(
    "/create-checkout-session",
    response_model=CreateCheckoutSessionResponse,
    name="payments:create_checkout_session",
    tags=["payments"],
)
async def create_checkout_session_endpoint(
    request_data: CreateCheckoutSessionRequest = Body(...),
    user: User = Depends(fastapi_users.current_user(active=True)), # Get current authenticated user
    payment_gateway: PaymentGatewayInterface = Depends(get_payment_gateway)
):
    """
    Creates a Stripe Checkout Session for the authenticated user to start a subscription.
    """
    if not user.email: # Should always exist for a fastapi-users user
        # This case should ideally be prevented by user model validation or creation logic
        logger.error(f"User {user.id} attempting to create checkout session without an email address.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User email is missing. Cannot proceed with payment."
        )

    # Construct success and cancel URLs
    frontend_url = str(settings.FRONTEND_URL).rstrip('/')
    success_url = f"{frontend_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}" # Stripe placeholder
    cancel_url = f"{frontend_url}/payment-cancel"

    try:
        checkout_session_id = await payment_gateway.create_checkout_session(
            user_id=user.id, # user.id is PyUUID
            email=user.email,
            plan_id=request_data.plan_id,
            success_url=success_url,
            cancel_url=cancel_url
        )
        return CreateCheckoutSessionResponse(checkout_session_id=checkout_session_id)
    except Exception as e:
        logger.error(f"Error creating checkout session for user {user.id}: {e}", exc_info=True)
        # StripeAdapter already logs Stripe-specific errors. This catches any other exceptions.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session. Please try again later." # Avoid exposing raw str(e)
        )

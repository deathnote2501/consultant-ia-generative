import stripe # Stripe Python library
from uuid import UUID as PyUUID
import logging
import asyncio # For asyncio.to_thread

from app.core.ports.payment_gateway import PaymentGatewayInterface
from app.core.config import settings

logger = logging.getLogger(__name__)

class StripeAdapter(PaymentGatewayInterface):
    """
    Adapter for Stripe payment gateway.
    """

    def __init__(self):
        if not settings.STRIPE_SECRET_KEY or "sk_test_yourstripenetkeyhere" in settings.STRIPE_SECRET_KEY:
            logger.error("Stripe secret key is not configured or is using a placeholder.")
            # Consider raising ValueError("Stripe secret key is not properly configured.")
            # If not raised, Stripe API calls will fail if the key is invalid.
        stripe.api_key = settings.STRIPE_SECRET_KEY

    async def create_checkout_session(
        self,
        *,
        user_id: PyUUID,
        email: str,
        plan_id: str, # This is the Stripe Price ID, e.g., price_xxxxxxxxxxxxxx
        success_url: str,
        cancel_url: str
    ) -> str: # Returns the Stripe Checkout Session ID
        """
        Creates a Stripe Checkout Session.
        """
        checkout_session_params = {
            'payment_method_types': ['card'],
            'line_items': [
                {
                    'price': plan_id,
                    'quantity': 1,
                },
            ],
            'mode': 'subscription', # For recurring payments
            'success_url': success_url,
            'cancel_url': cancel_url,
            'customer_email': email,
            'client_reference_id': str(user_id),
            'metadata': {
                'user_id': str(user_id),
            }
        }

        try:
            logger.info(f"Creating Stripe checkout session for user {user_id} with plan {plan_id}.")
            # Use asyncio.to_thread for the synchronous Stripe SDK call
            checkout_session = await asyncio.to_thread(
                stripe.checkout.Session.create, **checkout_session_params
            )
            logger.info(f"Stripe checkout session created successfully: {checkout_session.id} for user {user_id}")
            return checkout_session.id
        except stripe.error.StripeError as e:
            logger.error(f"Stripe API error while creating checkout session for user {user_id}: {e}")
            # Specific error handling can be added here based on e.type
            raise # Re-raise the StripeError to be handled by the caller
        except Exception as e:
            logger.error(f"Unexpected error while creating Stripe checkout session for user {user_id}: {e}")
            raise # Re-raise to be handled by the caller

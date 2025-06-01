from abc import ABC, abstractmethod
from uuid import UUID as PyUUID # For user_id type hint

class PaymentGatewayInterface(ABC):
    """
    Interface for a payment gateway service.
    """

    @abstractmethod
    async def create_checkout_session(
        self,
        *,
        user_id: PyUUID, # Using PyUUID to match User model ID type
        email: str,
        plan_id: str,     # This will be the Stripe Price ID
        success_url: str,
        cancel_url: str
    ) -> str: # Returns the Stripe Checkout Session ID
        """
        Creates a checkout session for a subscription.

        Args:
            user_id: The internal ID of the user.
            email: The email of the user (for customer matching/creation).
            plan_id: The ID of the plan/price in the payment gateway.
            success_url: The URL to redirect to on successful payment.
            cancel_url: The URL to redirect to if payment is canceled.

        Returns:
            The ID of the created checkout session.
        """
        pass

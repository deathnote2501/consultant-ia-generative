from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID as PyUUID
from datetime import datetime

from app.core.models import SubscriptionCreate, SubscriptionRead # Assuming these are the Pydantic schemas

class SubscriptionRepositoryInterface(ABC):
    @abstractmethod
    async def create_subscription(self, *, subscription_data: SubscriptionCreate) -> SubscriptionRead:
        """
        Creates a new subscription record.
        Args:
            subscription_data: Pydantic model with data for the new subscription.
        Returns:
            The created subscription as a Pydantic model.
        """
        pass

    @abstractmethod
    async def get_subscription_by_stripe_id(self, *, stripe_subscription_id: str) -> Optional[SubscriptionRead]:
        """
        Retrieves a subscription by its Stripe Subscription ID.
        Args:
            stripe_subscription_id: The Stripe ID of the subscription.
        Returns:
            The subscription as a Pydantic model, or None if not found.
        """
        pass

    @abstractmethod
    async def update_subscription_status(
        self,
        *,
        stripe_subscription_id: str,
        status: str,
        current_period_start: datetime,
        current_period_end: datetime
    ) -> Optional[SubscriptionRead]:
        """
        Updates the status and current period of a subscription.
        Args:
            stripe_subscription_id: The Stripe ID of the subscription to update.
            status: The new status (e.g., 'active', 'canceled').
            current_period_start: The start of the current billing period.
            current_period_end: The end of the current billing period.
        Returns:
            The updated subscription as a Pydantic model, or None if not found.
        """
        pass

    @abstractmethod
    async def get_active_subscription_for_user(
        self,
        *,
        user_id: PyUUID,
        course_id: int
    ) -> Optional[SubscriptionRead]:
        """
        Retrieves an active subscription for a specific user and course.
        Args:
            user_id: The ID of the user.
            course_id: The ID of the course.
        Returns:
            The active subscription as a Pydantic model, or None if not found or not active.
        """
        pass

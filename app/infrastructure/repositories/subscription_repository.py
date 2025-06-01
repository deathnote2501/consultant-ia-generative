from typing import Optional
from uuid import UUID as PyUUID
from datetime import datetime, timezone # Added timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_ # Using sqlalchemy directly

from app.core.models import SubscriptionCreate, SubscriptionRead, Subscription as SubscriptionModel
from app.core.ports.subscription_repository import SubscriptionRepositoryInterface
# from app.db.session import get_async_session # Not needed if session is injected

class PostgresSubscriptionRepository(SubscriptionRepositoryInterface):
    """
    PostgreSQL implementation of the Subscription Repository.
    """
    def __init__(self, session: AsyncSession): # Expect session to be injected
        self.session = session

    async def create_subscription(self, *, subscription_data: SubscriptionCreate) -> SubscriptionRead:
        # Ensure all datetime fields from Pydantic are timezone-aware if your DB expects that
        # For example, if current_period_start/end are naive from Stripe, make them aware here or in Pydantic model
        db_subscription = SubscriptionModel(**subscription_data.model_dump())
        self.session.add(db_subscription)
        await self.session.commit()
        await self.session.refresh(db_subscription)
        return SubscriptionRead.model_validate(db_subscription)

    async def get_subscription_by_stripe_id(self, *, stripe_subscription_id: str) -> Optional[SubscriptionRead]:
        stmt = select(SubscriptionModel).where(SubscriptionModel.stripe_subscription_id == stripe_subscription_id)
        result = await self.session.execute(stmt)
        db_subscription = result.scalar_one_or_none()
        if db_subscription:
            return SubscriptionRead.model_validate(db_subscription)
        return None

    async def update_subscription_status(
        self,
        *,
        stripe_subscription_id: str,
        status: str,
        current_period_start: datetime,
        current_period_end: datetime
    ) -> Optional[SubscriptionRead]:
        stmt = (
            update(SubscriptionModel)
            .where(SubscriptionModel.stripe_subscription_id == stripe_subscription_id)
            .values(
                status=status,
                current_period_start=current_period_start,
                current_period_end=current_period_end,
                # updated_at is handled by server_default/onupdate in the model in SubscriptionModel
            )
            .returning(SubscriptionModel)
        )
        result = await self.session.execute(stmt)
        # Check if the execute statement implies a commit or if explicit commit is needed
        # For most ORM operations that change data, commit is needed.
        await self.session.commit()
        updated_subscription = result.scalar_one_or_none()

        if updated_subscription:
            return SubscriptionRead.model_validate(updated_subscription)
        return None

    async def get_active_subscription_for_user(
        self,
        *,
        user_id: PyUUID,
        course_id: int
    ) -> Optional[SubscriptionRead]:
        stmt = select(SubscriptionModel).where(
            and_(
                SubscriptionModel.user_id == user_id,
                SubscriptionModel.course_id == course_id,
                SubscriptionModel.status == 'active',
                SubscriptionModel.current_period_end > datetime.now(timezone.utc)
            )
        )
        result = await self.session.execute(stmt)
        db_subscription = result.scalar_one_or_none()
        if db_subscription:
            return SubscriptionRead.model_validate(db_subscription)
        return None

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from subscription.domain import Subscription
from subscription.infrastructure.persistence.sqlalchemy.mappers import SubscriptionPersistenceMapper
from subscription.infrastructure.persistence.sqlalchemy.models import (
    SubscriptionModel,
    TrialPolicyModel,
    TrialUsageConditionModel,
)


class SqlAlchemySubscriptionHydrator:
    def __init__(self, session: AsyncSession, mapper: SubscriptionPersistenceMapper) -> None:
        self._session = session
        self._mapper = mapper

    async def hydrate(self, model: SubscriptionModel) -> Subscription:
        trial_model = await self._session.get(TrialPolicyModel, model.id)
        result = await self._session.execute(
            select(TrialUsageConditionModel).where(
                TrialUsageConditionModel.subscription_id == model.id
            )
        )
        return self._mapper.to_domain(model, trial_model, tuple(result.scalars().all()))

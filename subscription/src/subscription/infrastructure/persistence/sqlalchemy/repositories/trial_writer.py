from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from subscription.domain import Subscription
from subscription.infrastructure.persistence.sqlalchemy.mappers import SubscriptionPersistenceMapper
from subscription.infrastructure.persistence.sqlalchemy.models import (
    TrialPolicyModel,
    TrialUsageConditionModel,
)


class SqlAlchemyTrialWriter:
    def __init__(self, session: AsyncSession, mapper: SubscriptionPersistenceMapper) -> None:
        self._session = session
        self._mapper = mapper

    def add(self, subscription: Subscription) -> None:
        policy_model, usage_models = self._mapper.trial_models(subscription)
        if policy_model is not None:
            self._session.add(policy_model)
        self._session.add_all(usage_models)

    async def replace(self, subscription: Subscription) -> None:
        subscription_id = str(subscription.id)
        await self._session.execute(
            delete(TrialUsageConditionModel).where(
                TrialUsageConditionModel.subscription_id == subscription_id
            )
        )
        await self._session.execute(
            delete(TrialPolicyModel).where(TrialPolicyModel.subscription_id == subscription_id)
        )
        self.add(subscription)

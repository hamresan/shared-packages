from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from subscription.application import SubscriptionRepository
from subscription.domain import SubjectReference, Subscription
from subscription.infrastructure.persistence.sqlalchemy.mappers import SubscriptionPersistenceMapper
from subscription.infrastructure.persistence.sqlalchemy.models import SubscriptionModel
from subscription.infrastructure.persistence.sqlalchemy.repositories.subscription_hydrator import (
    SqlAlchemySubscriptionHydrator,
)
from subscription.infrastructure.persistence.sqlalchemy.repositories.trial_writer import (
    SqlAlchemyTrialWriter,
)


class SqlAlchemySubscriptionRepository(SubscriptionRepository):
    def __init__(
        self,
        session: AsyncSession,
        mapper: SubscriptionPersistenceMapper,
        hydrator: SqlAlchemySubscriptionHydrator,
        trial_writer: SqlAlchemyTrialWriter,
    ) -> None:
        self._session = session
        self._mapper = mapper
        self._hydrator = hydrator
        self._trial_writer = trial_writer

    async def get_by_id(self, subscription_id: UUID) -> Subscription | None:
        model = await self._session.get(SubscriptionModel, str(subscription_id))
        return None if model is None else await self._hydrator.hydrate(model)

    async def list_for_subject(self, subject: SubjectReference) -> tuple[Subscription, ...]:
        result = await self._session.execute(
            select(SubscriptionModel).where(
                SubscriptionModel.subject_type == subject.subject_type,
                SubscriptionModel.subject_id == subject.subject_id,
            )
        )
        return tuple([await self._hydrator.hydrate(model) for model in result.scalars().all()])

    async def add(self, subscription: Subscription) -> None:
        self._session.add(self._mapper.to_model(subscription))
        self._trial_writer.add(subscription)

    async def save(self, subscription: Subscription) -> None:
        await self._session.merge(self._mapper.to_model(subscription))
        await self._trial_writer.replace(subscription)

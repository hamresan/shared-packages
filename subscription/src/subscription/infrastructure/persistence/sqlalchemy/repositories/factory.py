from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from subscription.application import PlanRepository, SubscriptionRepository, UsageRepository
from subscription.infrastructure.persistence.sqlalchemy.mappers import (
    PlanPersistenceMapper,
    SubscriptionPersistenceMapper,
    UsagePersistenceMapper,
)
from subscription.infrastructure.persistence.sqlalchemy.repositories.plan import (
    SqlAlchemyPlanRepository,
)
from subscription.infrastructure.persistence.sqlalchemy.repositories.plan_hydrator import (
    SqlAlchemyPlanHydrator,
)
from subscription.infrastructure.persistence.sqlalchemy.repositories.subscription import (
    SqlAlchemySubscriptionRepository,
)
from subscription.infrastructure.persistence.sqlalchemy.repositories.subscription_hydrator import (
    SqlAlchemySubscriptionHydrator,
)
from subscription.infrastructure.persistence.sqlalchemy.repositories.trial_writer import (
    SqlAlchemyTrialWriter,
)
from subscription.infrastructure.persistence.sqlalchemy.repositories.usage import (
    SqlAlchemyUsageRepository,
)
from subscription.infrastructure.persistence.sqlalchemy.repositories.usage_window import (
    CalendarUsageWindowCalculator,
    SqlAlchemyUsageWindowResolver,
)


@dataclass(frozen=True, slots=True)
class SubscriptionRepositories:
    plans: PlanRepository
    subscriptions: SubscriptionRepository
    usage: UsageRepository


class SqlAlchemySubscriptionRepositoryFactory:
    def __init__(
        self,
        plan_mapper: PlanPersistenceMapper,
        subscription_mapper: SubscriptionPersistenceMapper,
        usage_mapper: UsagePersistenceMapper,
        calendar_usage_window_calculator: CalendarUsageWindowCalculator,
    ) -> None:
        self._plan_mapper = plan_mapper
        self._subscription_mapper = subscription_mapper
        self._usage_mapper = usage_mapper
        self._calendar_usage_window_calculator = calendar_usage_window_calculator

    def create(self, session: AsyncSession) -> SubscriptionRepositories:
        return SubscriptionRepositories(
            plans=SqlAlchemyPlanRepository(
                session,
                self._plan_mapper,
                SqlAlchemyPlanHydrator(session, self._plan_mapper),
            ),
            subscriptions=SqlAlchemySubscriptionRepository(
                session,
                self._subscription_mapper,
                SqlAlchemySubscriptionHydrator(session, self._subscription_mapper),
                SqlAlchemyTrialWriter(session, self._subscription_mapper),
            ),
            usage=SqlAlchemyUsageRepository(
                session,
                self._usage_mapper,
                SqlAlchemyUsageWindowResolver(
                    session,
                    self._calendar_usage_window_calculator,
                ),
            ),
        )

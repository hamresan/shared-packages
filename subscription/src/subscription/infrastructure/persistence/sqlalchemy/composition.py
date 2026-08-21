from subscription.infrastructure.persistence.sqlalchemy.mappers import (
    EntitlementPersistenceMapper,
    PlanPersistenceMapper,
    SubscriptionPersistenceMapper,
    UsagePersistenceMapper,
)
from subscription.infrastructure.persistence.sqlalchemy.repositories import (
    SqlAlchemySubscriptionRepositoryFactory,
)
from subscription.infrastructure.persistence.sqlalchemy.repositories.usage_window import (
    CalendarUsageWindowCalculator,
)
from subscription.infrastructure.persistence.sqlalchemy.session import AsyncSessionFactory
from subscription.infrastructure.persistence.sqlalchemy.unit_of_work import (
    SqlAlchemySubscriptionUnitOfWorkFactory,
)


def build_sqlalchemy_subscription_unit_of_work_factory(
    session_factory: AsyncSessionFactory,
) -> SqlAlchemySubscriptionUnitOfWorkFactory:
    repository_factory = SqlAlchemySubscriptionRepositoryFactory(
        plan_mapper=PlanPersistenceMapper(EntitlementPersistenceMapper()),
        subscription_mapper=SubscriptionPersistenceMapper(),
        usage_mapper=UsagePersistenceMapper(),
        calendar_usage_window_calculator=CalendarUsageWindowCalculator(),
    )
    return SqlAlchemySubscriptionUnitOfWorkFactory(session_factory, repository_factory)

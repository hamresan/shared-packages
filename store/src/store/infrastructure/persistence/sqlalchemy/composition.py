from store.infrastructure.persistence.sqlalchemy.mappers import (
    DailyWorkingHoursPersistenceMapper,
    StoreAddressPersistenceMapper,
    StoreContactPersistenceMapper,
    StoreCurrencyPersistenceMapper,
    StorePersistenceMapper,
    UtcDateTimeMapper,
    WeeklyWorkingSchedulePersistenceMapper,
)
from store.infrastructure.persistence.sqlalchemy.repositories import (
    SqlAlchemyStoreRepositoryFactory,
)
from store.infrastructure.persistence.sqlalchemy.session import AsyncSessionFactory
from store.infrastructure.persistence.sqlalchemy.unit_of_work import (
    SqlAlchemyStoreUnitOfWorkFactory,
)


def build_store_persistence_mapper() -> StorePersistenceMapper:
    return StorePersistenceMapper(
        address_mapper=StoreAddressPersistenceMapper(),
        contact_mapper=StoreContactPersistenceMapper(),
        currency_mapper=StoreCurrencyPersistenceMapper(),
        schedule_mapper=WeeklyWorkingSchedulePersistenceMapper(
            DailyWorkingHoursPersistenceMapper()
        ),
        datetime_mapper=UtcDateTimeMapper(),
    )


def build_sqlalchemy_store_unit_of_work_factory(
    session_factory: AsyncSessionFactory,
) -> SqlAlchemyStoreUnitOfWorkFactory:
    repository_factory = SqlAlchemyStoreRepositoryFactory(build_store_persistence_mapper())
    return SqlAlchemyStoreUnitOfWorkFactory(session_factory, repository_factory)

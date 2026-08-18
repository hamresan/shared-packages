from datetime import UTC, datetime
from uuid import UUID, uuid4

from store import (
    CountryCodeValidator,
    CreateStoreCommandValidator,
    CreateStoreService,
    CurrencyCodeValidator,
    GetOwnedStoreService,
    GetStoreService,
    LanguageSettingsValidator,
    StoreFactory,
    StoreIdentifierGenerator,
    StoreNameValidator,
    StoreOwnershipPolicy,
)
from store.application import Clock
from store.infrastructure.persistence import build_sqlalchemy_store_unit_of_work_factory
from store.presentation import FastApiStoreAdapter, build_fastapi_store_adapter
from store.presentation.dependencies import AuthenticatedActorDependency

from consumer_app.database import ConsumerDatabase


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(UTC)


class UuidStoreIdentifierGenerator(StoreIdentifierGenerator):
    def new_store_id(self) -> UUID:
        return uuid4()


def build_store_adapter(
    database: ConsumerDatabase,
    authenticated_actor_dependency: AuthenticatedActorDependency,
) -> FastApiStoreAdapter:
    unit_of_work_factory = build_sqlalchemy_store_unit_of_work_factory(
        database.session_factory
    )
    create_store = CreateStoreService(
        unit_of_work_factory=unit_of_work_factory,
        validator=CreateStoreCommandValidator(
            name_validator=StoreNameValidator(),
            language_validator=LanguageSettingsValidator(),
            country_validator=CountryCodeValidator(),
            currency_validator=CurrencyCodeValidator(),
        ),
        ownership_policy=StoreOwnershipPolicy(),
        factory=StoreFactory(
            identifier_generator=UuidStoreIdentifierGenerator(),
            clock=SystemClock(),
        ),
    )
    return build_fastapi_store_adapter(
        authenticated_actor_dependency=authenticated_actor_dependency,
        store_creator=create_store,
        owned_store_reader=GetOwnedStoreService(unit_of_work_factory),
        store_reader=GetStoreService(unit_of_work_factory),
    )

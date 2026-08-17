from uuid import UUID, uuid4

import pytest

from store.application import (
    CreateStoreCommand,
    CreateStoreCommandValidator,
    CreateStoreService,
    GetOwnedStoreQuery,
    GetOwnedStoreService,
    GetStoreQuery,
    GetStoreService,
    StoreFactory,
    StoreOwnershipPolicy,
)
from store.domain import (
    CountryCodeValidator,
    CurrencyCodeValidator,
    LanguageSettingsValidator,
    StoreNameValidator,
)
from tests.support import (
    FakeStoreRepository,
    FakeStoreUnitOfWork,
    FakeStoreUnitOfWorkFactory,
    FixedClock,
    FixedStoreIdentifierGenerator,
    build_store,
)


def build_create_service(
    repository: FakeStoreRepository,
    store_id: UUID,
) -> tuple[CreateStoreService, FakeStoreUnitOfWork]:
    unit_of_work = FakeStoreUnitOfWork(repository)
    validator = CreateStoreCommandValidator(
        StoreNameValidator(),
        LanguageSettingsValidator(),
        CountryCodeValidator(),
        CurrencyCodeValidator(),
    )
    service = CreateStoreService(
        FakeStoreUnitOfWorkFactory(unit_of_work),
        validator,
        StoreOwnershipPolicy(),
        StoreFactory(FixedStoreIdentifierGenerator(store_id), FixedClock()),
    )
    return service, unit_of_work


@pytest.mark.asyncio
async def test_create_store_normalizes_and_persists_store() -> None:
    owner_id = uuid4()
    store_id = uuid4()
    repository = FakeStoreRepository()
    service, unit_of_work = build_create_service(repository, store_id)

    result = await service.execute(
        CreateStoreCommand(
            owner_user_id=owner_id,
            name="  My Store  ",
            business_type=" Retail ",
            primary_language="EN",
            country_code="om",
            base_currency_code="omr",
        )
    )

    assert result.store.id == store_id
    assert result.store.owner_user_id == owner_id
    assert result.store.name == "My Store"
    assert result.store.business_type == "retail"
    assert result.store.primary_language == "en"
    assert result.store.country_code == "OM"
    assert result.store.base_currency_code == "OMR"
    assert repository.added == [result.store]
    assert unit_of_work.committed is True


@pytest.mark.asyncio
async def test_create_store_rejects_second_store_for_same_owner() -> None:
    owner_id = uuid4()
    repository = FakeStoreRepository([build_store(owner_user_id=owner_id)])
    service, unit_of_work = build_create_service(repository, uuid4())

    with pytest.raises(ValueError, match="Owner already has a store"):
        await service.execute(
            CreateStoreCommand(
                owner_user_id=owner_id,
                name="Store",
                business_type="retail",
                primary_language="en",
                country_code="OM",
                base_currency_code="OMR",
            )
        )

    assert repository.added == []
    assert unit_of_work.committed is False


@pytest.mark.asyncio
async def test_read_services_get_store_by_id_and_owner() -> None:
    store = build_store()
    repository = FakeStoreRepository([store])
    unit_of_work_factory = FakeStoreUnitOfWorkFactory(FakeStoreUnitOfWork(repository))

    by_id = await GetStoreService(unit_of_work_factory).execute(GetStoreQuery(store.id))
    by_owner = await GetOwnedStoreService(unit_of_work_factory).execute(
        GetOwnedStoreQuery(store.owner_user_id)
    )

    assert by_id is store
    assert by_owner is store

import pytest

from store.infrastructure.persistence.sqlalchemy import (
    SqlAlchemyStoreRepository,
    build_store_persistence_mapper,
)
from tests.support.persistence import SqliteStorePersistence, build_persistence_store


@pytest.mark.asyncio
async def test_repository_add_and_get_by_id_round_trip() -> None:
    persistence = await SqliteStorePersistence.create()
    store = build_persistence_store()

    try:
        async with persistence.session_factory() as session:
            repository = SqlAlchemyStoreRepository(session, build_store_persistence_mapper())
            await repository.add(store)
            await session.commit()

        async with persistence.session_factory() as session:
            repository = SqlAlchemyStoreRepository(session, build_store_persistence_mapper())
            restored = await repository.get_by_id(store.id)

        assert restored == store
    finally:
        await persistence.close()


@pytest.mark.asyncio
async def test_repository_get_by_owner_id_and_missing_store() -> None:
    persistence = await SqliteStorePersistence.create()
    store = build_persistence_store()

    try:
        async with persistence.session_factory() as session:
            repository = SqlAlchemyStoreRepository(session, build_store_persistence_mapper())
            await repository.add(store)
            await session.commit()

        async with persistence.session_factory() as session:
            repository = SqlAlchemyStoreRepository(session, build_store_persistence_mapper())
            owned_store = await repository.get_by_owner_id(store.owner_user_id)
            missing = await repository.get_by_id(build_persistence_store().id)

        assert owned_store == store
        assert missing is None
    finally:
        await persistence.close()

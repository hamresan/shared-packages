import pytest

from store.infrastructure.persistence.sqlalchemy import build_sqlalchemy_store_unit_of_work_factory
from tests.support.persistence import SqliteStorePersistence, build_persistence_store


@pytest.mark.asyncio
async def test_unit_of_work_commits_store() -> None:
    persistence = await SqliteStorePersistence.create()
    store = build_persistence_store()
    factory = build_sqlalchemy_store_unit_of_work_factory(persistence.session_factory)

    try:
        async with factory() as unit_of_work:
            await unit_of_work.stores.add(store)
            await unit_of_work.commit()

        async with factory() as unit_of_work:
            restored = await unit_of_work.stores.get_by_id(store.id)

        assert restored == store
    finally:
        await persistence.close()


@pytest.mark.asyncio
async def test_unit_of_work_requires_entered_context() -> None:
    persistence = await SqliteStorePersistence.create()
    unit_of_work = build_sqlalchemy_store_unit_of_work_factory(persistence.session_factory)()

    try:
        with pytest.raises(RuntimeError, match="has not been entered"):
            _ = unit_of_work.stores
        with pytest.raises(RuntimeError, match="has not been entered"):
            await unit_of_work.commit()
    finally:
        await persistence.close()


@pytest.mark.asyncio
async def test_unit_of_work_rolls_back_on_exception() -> None:
    persistence = await SqliteStorePersistence.create()
    store = build_persistence_store()
    factory = build_sqlalchemy_store_unit_of_work_factory(persistence.session_factory)

    try:
        with pytest.raises(RuntimeError, match="force rollback"):
            async with factory() as unit_of_work:
                await unit_of_work.stores.add(store)
                raise RuntimeError("force rollback")

        async with factory() as unit_of_work:
            restored = await unit_of_work.stores.get_by_id(store.id)

        assert restored is None
    finally:
        await persistence.close()

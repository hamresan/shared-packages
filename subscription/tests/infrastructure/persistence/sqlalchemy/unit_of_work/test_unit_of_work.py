import pytest

from subscription.infrastructure.persistence.sqlalchemy import (
    build_sqlalchemy_subscription_unit_of_work_factory,
)
from tests.infrastructure.persistence.sqlalchemy.support.database import SqliteTestDatabase


async def test_unit_of_work_requires_context_before_repository_access() -> None:
    database = SqliteTestDatabase()
    factory = build_sqlalchemy_subscription_unit_of_work_factory(database.session_factory())
    unit_of_work = factory()

    with pytest.raises(RuntimeError, match="Unit of work has not been entered"):
        _ = unit_of_work.plans

    with pytest.raises(RuntimeError, match="Unit of work has not been entered"):
        await unit_of_work.commit()

    await database.dispose()

import pytest

from business.migrations import business_metadata, include_business_name
from tests.support.alembic_checks import assert_no_business_schema_drift
from tests.support.sqlalchemy_environment import SqlAlchemyEnvironment


def test_metadata_names_and_host_filter() -> None:
    metadata = business_metadata()
    assert len(metadata.tables) == 5
    assert all(name.startswith("business_") for name in metadata.tables)
    assert include_business_name("business_branches", "table", {})
    assert not include_business_name("store_stores", "table", {})
    assert include_business_name(
        "ix_business_branches_city", "index", {"table_name": "business_branches"}
    )
    assert not include_business_name(
        "ix_store_stores_name", "index", {"table_name": "store_stores"}
    )


@pytest.mark.asyncio
async def test_alembic_autogenerate_has_no_drift_after_schema_creation(
    sqlalchemy_environment: SqlAlchemyEnvironment,
) -> None:
    async with sqlalchemy_environment.engine.connect() as connection:
        await connection.run_sync(assert_no_business_schema_drift)

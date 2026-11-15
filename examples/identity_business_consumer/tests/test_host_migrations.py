from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from business.migrations import business_metadata
from identity.migrations import identity_metadata
from sqlalchemy import MetaData, create_engine, inspect

from tests.support.host_migration import apply_initial_host_migration


def test_host_can_upgrade_identity_and_business_in_one_alembic_schema() -> None:
    metadata = MetaData()
    for package_metadata in (identity_metadata(), business_metadata()):
        for table in package_metadata.sorted_tables:
            table.to_metadata(metadata)

    expected_tables = set(identity_metadata().tables) | set(business_metadata().tables)
    assert len(expected_tables) == 10
    assert set(metadata.tables) == expected_tables

    engine = create_engine("sqlite://")
    try:
        with engine.begin() as connection:
            apply_initial_host_migration(connection, metadata)
            assert set(inspect(connection).get_table_names()) == expected_tables
            assert compare_metadata(MigrationContext.configure(connection), metadata) == []
    finally:
        engine.dispose()

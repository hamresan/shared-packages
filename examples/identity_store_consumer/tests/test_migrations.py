from typing import cast

from alembic.autogenerate.api import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import Table, create_engine

from consumer_app.database import consumer_metadata, include_consumer_name

EXPECTED_TABLES = {
    "identity_users",
    "identity_user_identities",
    "identity_otp_challenges",
    "identity_sessions",
    "store_stores",
}


def test_host_metadata_exposes_identity_and_store_tables() -> None:
    table_names = {table_name for metadata in consumer_metadata() for table_name in metadata.tables}
    assert table_names == EXPECTED_TABLES


def test_host_alembic_autogenerate_discovers_both_packages() -> None:
    engine = create_engine("sqlite://")
    with engine.connect() as connection:
        migration_context = MigrationContext.configure(connection)
        differences = [
            difference
            for metadata in consumer_metadata()
            for difference in compare_metadata(migration_context, metadata)
        ]

    added_tables = {
        cast(Table, difference[1]).name
        for difference in differences
        if difference[0] == "add_table"
    }
    assert added_tables == EXPECTED_TABLES


def test_host_include_name_accepts_only_owned_package_tables() -> None:
    assert include_consumer_name("identity_users", "table", {}) is True
    assert include_consumer_name("store_stores", "table", {}) is True
    assert include_consumer_name("orders", "table", {}) is False

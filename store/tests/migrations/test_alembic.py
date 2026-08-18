from typing import cast

from alembic.autogenerate.api import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import Table, create_engine

from store.migrations import include_store_name, store_metadata

EXPECTED_STORE_TABLES = {"store_stores"}


def test_store_metadata_contains_only_store_tables() -> None:
    assert set(store_metadata().tables) == EXPECTED_STORE_TABLES


def test_alembic_autogenerate_discovers_store_tables() -> None:
    engine = create_engine("sqlite://")

    with engine.connect() as connection:
        migration_context = MigrationContext.configure(connection)
        differences = compare_metadata(migration_context, store_metadata())

    added_tables = {
        cast(Table, difference[1]).name
        for difference in differences
        if difference[0] == "add_table"
    }

    engine.dispose()
    assert added_tables == EXPECTED_STORE_TABLES


def test_include_store_name_accepts_store_tables() -> None:
    assert include_store_name("store_stores", "table", {}) is True
    assert include_store_name("identity_users", "table", {}) is False


def test_include_store_name_follows_parent_table_for_children() -> None:
    assert include_store_name("owner_user_id", "column", {"table_name": "store_stores"}) is True
    assert include_store_name("email", "column", {"table_name": "identity_users"}) is False


def test_include_store_name_keeps_non_table_scopes() -> None:
    assert include_store_name(None, "schema", {}) is True

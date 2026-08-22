"""Tests for host-owned Alembic integration helpers."""

from typing import cast

from alembic.autogenerate.api import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import Column, Integer, MetaData, Table, create_engine

from integration_auth.migrations import (
    include_integration_auth_name,
    integration_auth_metadata,
)

EXPECTED_INTEGRATION_AUTH_TABLES = {
    "integration_auth_clients",
    "integration_auth_credentials",
    "integration_auth_consumed_nonces",
}


def test_integration_auth_metadata_contains_only_package_tables() -> None:
    assert set(integration_auth_metadata().tables) == EXPECTED_INTEGRATION_AUTH_TABLES


def test_alembic_autogenerate_discovers_integration_auth_tables() -> None:
    engine = create_engine("sqlite://")

    with engine.connect() as connection:
        migration_context = MigrationContext.configure(connection)
        differences = compare_metadata(migration_context, integration_auth_metadata())

    added_tables = {
        cast(Table, difference[1]).name
        for difference in differences
        if difference[0] == "add_table"
    }

    engine.dispose()
    assert added_tables == EXPECTED_INTEGRATION_AUTH_TABLES


def test_alembic_filter_ignores_host_owned_tables() -> None:
    engine = create_engine("sqlite://")
    host_metadata = MetaData()
    Table("identity_users", host_metadata, Column("id", Integer, primary_key=True))
    host_metadata.create_all(engine)

    with engine.connect() as connection:
        migration_context = MigrationContext.configure(
            connection,
            opts={"include_name": include_integration_auth_name},
        )
        differences = compare_metadata(migration_context, integration_auth_metadata())

    removed_tables = {
        cast(Table, difference[1]).name
        for difference in differences
        if difference[0] == "remove_table"
    }

    engine.dispose()
    assert "identity_users" not in removed_tables


def test_include_name_accepts_only_integration_auth_tables() -> None:
    assert include_integration_auth_name("integration_auth_clients", "table", {}) is True
    assert include_integration_auth_name("identity_users", "table", {}) is False
    assert include_integration_auth_name(None, "table", {}) is False


def test_include_name_follows_parent_table_for_child_objects() -> None:
    assert (
        include_integration_auth_name(
            "client_id",
            "column",
            {"table_name": "integration_auth_credentials"},
        )
        is True
    )
    assert (
        include_integration_auth_name(
            "email",
            "column",
            {"table_name": "identity_users"},
        )
        is False
    )


def test_include_name_keeps_non_table_scopes_without_parent_table() -> None:
    assert include_integration_auth_name(None, "schema", {}) is True

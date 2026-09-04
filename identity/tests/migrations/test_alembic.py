from typing import cast

from alembic.autogenerate.api import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import Table, create_engine

from identity.migrations import identity_metadata, include_identity_name

EXPECTED_IDENTITY_TABLES = {
    "identity_users",
    "identity_user_identities",
    "identity_external_identities",
    "identity_otp_challenges",
    "identity_sessions",
}


def test_identity_metadata_contains_only_identity_tables() -> None:
    assert set(identity_metadata().tables) == EXPECTED_IDENTITY_TABLES


def test_alembic_autogenerate_discovers_identity_tables() -> None:
    engine = create_engine("sqlite://")

    with engine.connect() as connection:
        migration_context = MigrationContext.configure(connection)
        differences = compare_metadata(migration_context, identity_metadata())

    added_tables = {
        cast(Table, difference[1]).name
        for difference in differences
        if difference[0] == "add_table"
    }

    assert added_tables == EXPECTED_IDENTITY_TABLES


def test_include_identity_name_accepts_identity_tables() -> None:
    assert include_identity_name("identity_users", "table", {}) is True
    assert include_identity_name("orders", "table", {}) is False


def test_include_identity_name_follows_parent_table_for_children() -> None:
    assert (
        include_identity_name(
            "user_id",
            "column",
            {"table_name": "identity_sessions"},
        )
        is True
    )
    assert (
        include_identity_name(
            "status",
            "column",
            {"table_name": "orders"},
        )
        is False
    )


def test_include_identity_name_keeps_non_table_scopes() -> None:
    assert include_identity_name(None, "schema", {}) is True

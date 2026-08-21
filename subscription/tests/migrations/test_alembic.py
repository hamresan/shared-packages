from typing import cast

from alembic.autogenerate.api import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import Table, create_engine

from subscription.migrations import include_subscription_name, subscription_metadata

EXPECTED_SUBSCRIPTION_TABLES = {
    "subscription_plan",
    "subscription_plan_entitlement",
    "subscription_subscription",
    "subscription_trial_policy",
    "subscription_trial_usage_condition",
    "subscription_usage_record",
}


def test_subscription_metadata_contains_only_subscription_tables() -> None:
    assert set(subscription_metadata().tables) == EXPECTED_SUBSCRIPTION_TABLES


def test_alembic_autogenerate_discovers_subscription_tables() -> None:
    engine = create_engine("sqlite://")

    with engine.connect() as connection:
        migration_context = MigrationContext.configure(connection)
        differences = compare_metadata(migration_context, subscription_metadata())

    added_tables = {
        cast(Table, difference[1]).name
        for difference in differences
        if difference[0] == "add_table"
    }

    engine.dispose()
    assert added_tables == EXPECTED_SUBSCRIPTION_TABLES


def test_include_subscription_name_accepts_subscription_tables() -> None:
    assert include_subscription_name("subscription_plan", "table", {}) is True
    assert include_subscription_name("identity_users", "table", {}) is False


def test_include_subscription_name_follows_parent_table_for_children() -> None:
    assert (
        include_subscription_name(
            "subject_id",
            "column",
            {"table_name": "subscription_subscription"},
        )
        is True
    )
    assert (
        include_subscription_name("email", "column", {"table_name": "identity_users"})
        is False
    )


def test_include_subscription_name_keeps_non_table_scopes() -> None:
    assert include_subscription_name(None, "schema", {}) is True

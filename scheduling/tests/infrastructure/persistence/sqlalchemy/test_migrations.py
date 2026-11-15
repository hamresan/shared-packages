"""Verify metadata is isolated and Alembic can inspect scheduling tables."""

from sqlalchemy import MetaData, Table

from scheduling.infrastructure.persistence.sqlalchemy import (
    is_scheduling_table,
    scheduling_metadata,
)


def test_host_can_combine_metadata_without_package_specific_engine() -> None:
    host = MetaData()
    Table("host_accounts", host)
    package = scheduling_metadata()

    assert "scheduling_calendars" in package.tables
    assert "host_accounts" in host.tables
    assert is_scheduling_table("scheduling_calendars", "table")
    assert not is_scheduling_table("host_accounts", "table")
    assert not is_scheduling_table(None, "table")
    assert not is_scheduling_table("scheduling_calendars", "column")

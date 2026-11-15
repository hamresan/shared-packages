"""Unrelated host schema deliberately combined with scheduling-owned metadata."""

from sqlalchemy import Column, Integer, MetaData, String, Table

from scheduling.infrastructure.persistence.sqlalchemy import scheduling_metadata


def host_metadata() -> MetaData:
    metadata = MetaData()
    Table(
        "host_migration_accounts",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(64), nullable=False),
    )
    return metadata


def combined_metadata() -> MetaData:
    metadata = MetaData()
    for source in (host_metadata(), scheduling_metadata()):
        for table in source.tables.values():
            table.to_metadata(metadata)
    return metadata

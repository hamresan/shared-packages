from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.operations.ops import CreateIndexOp, CreateTableOp
from sqlalchemy import Connection, MetaData


def apply_initial_host_migration(connection: Connection, metadata: MetaData) -> None:
    """Exercise Alembic DDL against the actual combined package metadata."""
    operations = Operations(MigrationContext.configure(connection))
    for table in metadata.sorted_tables:
        operations.invoke(CreateTableOp.from_table(table))
        for index in sorted(table.indexes, key=lambda item: item.name or ""):
            operations.invoke(CreateIndexOp.from_index(index))

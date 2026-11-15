from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy.engine import Connection

from business.migrations import business_metadata


def assert_no_business_schema_drift(connection: Connection) -> None:
    context = MigrationContext.configure(connection, opts={"target_metadata": business_metadata()})
    assert compare_metadata(context, business_metadata()) == []

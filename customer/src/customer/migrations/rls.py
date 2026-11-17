"""Install explicit fail-closed RLS for all package-owned tables.

Call with an Alembic migration connection after tables exist. The migration
role owns schema objects; the runtime role must be non-owner without BYPASSRLS.
"""

from sqlalchemy import Connection, text

from customer.migrations.alembic import customer_metadata


def install_customer_rls(connection: Connection) -> None:
    if connection.dialect.name != "postgresql":
        raise ValueError("Customer RLS requires PostgreSQL")

    for table_name in customer_metadata().tables:
        # Names come only from immutable ORM metadata, never user input.
        connection.execute(text(f'ALTER TABLE "{table_name}" ENABLE ROW LEVEL SECURITY'))
        connection.execute(text(f'ALTER TABLE "{table_name}" FORCE ROW LEVEL SECURITY'))
        connection.execute(text(f'DROP POLICY IF EXISTS customer_tenant_scope ON "{table_name}"'))
        scope = "business_id = NULLIF(current_setting('app.customer_business_id', true), '')::uuid"
        connection.execute(
            text(
                f'CREATE POLICY customer_tenant_scope ON "{table_name}" '
                f"USING ({scope}) WITH CHECK ({scope})"
            )
        )

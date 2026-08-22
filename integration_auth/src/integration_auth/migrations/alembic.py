"""Host-owned Alembic integration helpers."""

from collections.abc import Mapping

from sqlalchemy import MetaData

from integration_auth.infrastructure.persistence.sqlalchemy.models.base import IntegrationAuthBase

INTEGRATION_AUTH_TABLE_PREFIX = "integration_auth_"


def integration_auth_metadata() -> MetaData:
    """Return SQLAlchemy metadata owned by the integration-auth package."""
    return IntegrationAuthBase.metadata


def include_integration_auth_name(
    name: str | None,
    type_: str,
    parent_names: Mapping[str, str | None],
) -> bool:
    """Limit Alembic reflection to integration-auth tables and their child objects."""
    if type_ == "table":
        return name is not None and name.startswith(INTEGRATION_AUTH_TABLE_PREFIX)

    parent_table_name = parent_names.get("table_name")
    if parent_table_name is not None:
        return parent_table_name.startswith(INTEGRATION_AUTH_TABLE_PREFIX)

    return True

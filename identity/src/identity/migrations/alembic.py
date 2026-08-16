from collections.abc import Mapping

from sqlalchemy import MetaData

from identity.infrastructure.persistence.sqlalchemy import IdentityBase

IDENTITY_TABLE_PREFIX = "identity_"


def identity_metadata() -> MetaData:
    """Return the SQLAlchemy metadata owned by the Identity package."""
    return IdentityBase.metadata


def include_identity_name(
    name: str | None,
    type_: str,
    parent_names: Mapping[str, str | None],
) -> bool:
    """Limit Alembic reflection to Identity-owned tables and their children."""
    if type_ == "table":
        return name is not None and name.startswith(IDENTITY_TABLE_PREFIX)

    parent_table_name = parent_names.get("table_name")
    if parent_table_name is not None:
        return parent_table_name.startswith(IDENTITY_TABLE_PREFIX)

    return True

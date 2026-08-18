from collections.abc import Mapping

from sqlalchemy import MetaData

from store.infrastructure.persistence.sqlalchemy import StoreBase

STORE_TABLE_PREFIX = "store_"


def store_metadata() -> MetaData:
    """Return SQLAlchemy metadata owned by the Store package."""
    return StoreBase.metadata


def include_store_name(
    name: str | None,
    type_: str,
    parent_names: Mapping[str, str | None],
) -> bool:
    """Limit Alembic reflection to Store-owned tables and their children."""
    if type_ == "table":
        return name is not None and name.startswith(STORE_TABLE_PREFIX)

    parent_table_name = parent_names.get("table_name")
    if parent_table_name is not None:
        return parent_table_name.startswith(STORE_TABLE_PREFIX)

    return True

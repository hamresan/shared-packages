"""Alembic integration; migrations remain in the host's revision history."""

from sqlalchemy import MetaData

from customer.infrastructure.persistence.sqlalchemy import models
from customer.infrastructure.persistence.sqlalchemy.base import CustomerBase


def customer_metadata() -> MetaData:
    _ = models.__all__
    return CustomerBase.metadata


def include_customer_name(
    name: str | None, type_: str, parent_names: dict[str, str | None]
) -> bool:
    if type_ == "table":
        return name is not None and name in CustomerBase.metadata.tables
    if type_ == "schema":
        return True
    return parent_names.get("table_name") in CustomerBase.metadata.tables

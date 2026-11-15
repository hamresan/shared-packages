from collections.abc import Mapping

from sqlalchemy import MetaData

from business.infrastructure.persistence.sqlalchemy import BusinessBase


def business_metadata() -> MetaData:
    return BusinessBase.metadata


def include_business_name(
    name: str | None, type_: str, parent_names: Mapping[str, str | None]
) -> bool:
    if type_ == "table":
        return name is not None and name.startswith("business_")
    parent_table_name = parent_names.get("table_name")
    return parent_table_name.startswith("business_") if parent_table_name is not None else True

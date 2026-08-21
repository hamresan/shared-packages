from collections.abc import Mapping

from sqlalchemy import MetaData

from subscription.infrastructure.persistence.sqlalchemy import SubscriptionBase

SUBSCRIPTION_TABLE_PREFIX = "subscription_"


def subscription_metadata() -> MetaData:
    """Return SQLAlchemy metadata owned by the Subscription package."""
    return SubscriptionBase.metadata


def include_subscription_name(
    name: str | None,
    type_: str,
    parent_names: Mapping[str, str | None],
) -> bool:
    """Limit Alembic reflection to Subscription-owned tables and their children."""
    if type_ == "table":
        return name is not None and name.startswith(SUBSCRIPTION_TABLE_PREFIX)

    parent_table_name = parent_names.get("table_name")
    if parent_table_name is not None:
        return parent_table_name.startswith(SUBSCRIPTION_TABLE_PREFIX)

    return True

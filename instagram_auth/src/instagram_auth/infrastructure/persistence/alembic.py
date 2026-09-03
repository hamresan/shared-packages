"""Alembic integration helpers for host-owned migration histories."""

from sqlalchemy import MetaData

from instagram_auth.infrastructure.persistence.base import InstagramAuthBase

TABLE_PREFIX = "instagram_auth_"


def get_instagram_auth_metadata() -> MetaData:
    """Return package-owned SQLAlchemy metadata for host Alembic composition."""
    return InstagramAuthBase.metadata


def is_instagram_auth_table(name: str) -> bool:
    """Return whether a database table belongs to this package."""
    return name.startswith(TABLE_PREFIX)

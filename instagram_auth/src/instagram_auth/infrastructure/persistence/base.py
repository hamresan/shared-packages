"""SQLAlchemy metadata owned by the Instagram auth package."""

from sqlalchemy.orm import DeclarativeBase


class InstagramAuthBase(DeclarativeBase):
    """Declarative base for package-owned persistence tables."""

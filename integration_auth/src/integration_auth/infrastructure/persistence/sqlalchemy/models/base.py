"""Declarative base for integration-auth SQLAlchemy records."""

from sqlalchemy.orm import DeclarativeBase


class IntegrationAuthBase(DeclarativeBase):
    """Base metadata owned by the package, bound by the host application."""

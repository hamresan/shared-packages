"""Isolated metadata for scheduling-owned tables."""

from sqlalchemy.orm import DeclarativeBase


class SchedulingBase(DeclarativeBase):
    """Metadata that a consuming host can register in its migrations."""

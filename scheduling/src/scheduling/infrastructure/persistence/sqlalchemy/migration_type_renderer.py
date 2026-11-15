"""Render the scheduling JSONB variant as executable Alembic revision code."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB, dialect

if TYPE_CHECKING:
    from alembic.autogenerate.api import AutogenContext


def render_scheduling_type(
    kind: str, value: object, context: AutogenContext
) -> str | Literal[False]:
    """Avoid SQLAlchemy's unqualified Text() repr for our JSONB column variant."""
    if kind != "type" or not isinstance(value, JSON):
        return False
    if not isinstance(value.dialect_impl(dialect()), JSONB):
        return False
    context.imports.add("from sqlalchemy.dialects import postgresql")
    return "sa.JSON().with_variant(postgresql.JSONB(), 'postgresql')"

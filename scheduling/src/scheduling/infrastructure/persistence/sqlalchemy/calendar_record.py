"""SQLAlchemy storage model for calendar configuration snapshots."""

from typing import Any

from sqlalchemy import JSON, Boolean, CheckConstraint, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import SchedulingBase


class CalendarRecord(SchedulingBase):
    """One authoritative calendar per tenant/scope identity."""

    __tablename__ = "scheduling_calendars"
    __table_args__ = (
        UniqueConstraint("tenant_id", "scope", "scope_id", name="uq_scheduling_tenant_scope"),
        CheckConstraint("version >= 1", name="ck_scheduling_version_positive"),
    )

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    calendar_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    scope: Mapped[str] = mapped_column(String(32), nullable=False)
    scope_id: Mapped[str] = mapped_column(String(128), nullable=False)
    timezone_name: Mapped[str] = mapped_column(String(128), nullable=False)
    weekly_schedule: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )
    exceptions: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )
    annual_closures: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )
    blocked_periods: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

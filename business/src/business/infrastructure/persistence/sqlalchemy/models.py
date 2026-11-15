from datetime import datetime
from uuid import UUID

from business.infrastructure.persistence.sqlalchemy.base import BusinessBase
from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column


class BusinessModel(BusinessBase):
    __tablename__ = "business_businesses"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    business_type: Mapped[str | None] = mapped_column(String(80))
    country_code: Mapped[str] = mapped_column(String(2))
    default_language: Mapped[str] = mapped_column(String(16))
    default_currency_code: Mapped[str] = mapped_column(String(3))
    status: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class BranchModel(BusinessBase):
    __tablename__ = "business_branches"
    __table_args__ = (
        UniqueConstraint("id", "business_id", name="uq_business_branches_id_business_id"),
        Index("ix_business_branches_business_city", "business_id", "city"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    business_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("business_businesses.id", ondelete="RESTRICT"), index=True
    )
    name: Mapped[str] = mapped_column(String(160))
    timezone: Mapped[str] = mapped_column(String(64))
    address: Mapped[dict[str, str | None] | None] = mapped_column(JSON)
    contact: Mapped[dict[str, str | None] | None] = mapped_column(JSON)
    city: Mapped[str | None] = mapped_column(String(160))
    country_code: Mapped[str | None] = mapped_column(String(2))
    status: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class MembershipModel(BusinessBase):
    __tablename__ = "business_memberships"
    __table_args__ = (
        UniqueConstraint("id", "business_id", name="uq_business_memberships_id_business_id"),
        Index(
            "ix_business_memberships_business_user_current",
            "business_id",
            "user_id",
            unique=True,
            postgresql_where=text("status IN ('active', 'invited')"),
            sqlite_where=text("status IN ('active', 'invited')"),
        ),
        Index("ix_business_memberships_user", "user_id"),
        Index(
            "uq_business_memberships_one_active_owner",
            "business_id",
            unique=True,
            postgresql_where=text("role = 'owner' AND status = 'active'"),
            sqlite_where=text("role = 'owner' AND status = 'active'"),
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    business_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("business_businesses.id", ondelete="RESTRICT"), index=True
    )
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True))
    role: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(16))
    branch_access_scope: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MembershipBranchAccessModel(BusinessBase):
    __tablename__ = "business_membership_branch_access"
    __table_args__ = (
        ForeignKeyConstraint(
            ["membership_id", "business_id"],
            ["business_memberships.id", "business_memberships.business_id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["branch_id", "business_id"],
            ["business_branches.id", "business_branches.business_id"],
            ondelete="RESTRICT",
        ),
    )

    membership_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    branch_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    business_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)


class MembershipAuditModel(BusinessBase):
    __tablename__ = "business_membership_audit"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    business_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("business_businesses.id", ondelete="RESTRICT"), index=True
    )
    membership_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("business_memberships.id", ondelete="RESTRICT")
    )
    actor_user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True))
    action: Mapped[str] = mapped_column(String(40))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    previous_value: Mapped[str | None] = mapped_column(String(40))
    new_value: Mapped[str | None] = mapped_column(String(40))
    branch_ids: Mapped[list[str]] = mapped_column(JSON)

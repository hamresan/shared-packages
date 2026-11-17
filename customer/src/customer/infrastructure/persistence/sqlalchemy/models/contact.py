from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKeyConstraint, Index, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from customer.infrastructure.persistence.sqlalchemy.base import CustomerBase


class CustomerContactModel(CustomerBase):
    __tablename__ = "customer_contacts"
    __table_args__ = (
        ForeignKeyConstraint(
            ["customer_id", "business_id"],
            ["customer_customers.id", "customer_customers.business_id"],
            ondelete="CASCADE",
        ),
        Index("ix_customer_contacts_business_value", "business_id", "kind", "value"),
        Index(
            "uq_customer_contacts_primary_kind",
            "business_id",
            "customer_id",
            "kind",
            unique=True,
            postgresql_where=text("is_primary = true"),
            sqlite_where=text("is_primary = 1"),
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    business_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    value: Mapped[str] = mapped_column(String(254), nullable=False)
    is_primary: Mapped[bool] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verification_method: Mapped[str | None] = mapped_column(String(80))

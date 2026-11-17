"""PII-minimized immutable Customer audit ledger."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKeyConstraint, Index, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from customer.infrastructure.persistence.sqlalchemy.base import CustomerBase


class CustomerAuditModel(CustomerBase):
    __tablename__ = "customer_audit_events"
    __table_args__ = (
        ForeignKeyConstraint(
            ["customer_id", "business_id"],
            ["customer_customers.id", "customer_customers.business_id"],
        ),
        Index("ix_customer_audit_business_subject", "business_id", "customer_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    business_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    actor_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    actor_type: Mapped[str] = mapped_column(String(16), nullable=False)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKeyConstraint, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from customer.infrastructure.persistence.sqlalchemy.base import CustomerBase


class CustomerCreationReceiptModel(CustomerBase):
    __tablename__ = "customer_creation_receipts"
    __table_args__ = (
        ForeignKeyConstraint(
            ["customer_id", "business_id"],
            ["customer_customers.id", "customer_customers.business_id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("business_id", "key", name="uq_customer_creation_receipt_key"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    business_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    key: Mapped[str] = mapped_column(String(200), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

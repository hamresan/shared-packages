from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKeyConstraint, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from customer.infrastructure.persistence.sqlalchemy.base import CustomerBase


class CustomerNoteModel(CustomerBase):
    __tablename__ = "customer_notes"
    __table_args__ = (
        ForeignKeyConstraint(
            ["customer_id", "business_id"],
            ["customer_customers.id", "customer_customers.business_id"],
            ondelete="CASCADE",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    business_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    author_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    author_type: Mapped[str] = mapped_column(String(16), nullable=False)
    body: Mapped[str] = mapped_column(String(4000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

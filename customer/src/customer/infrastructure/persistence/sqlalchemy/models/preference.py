from uuid import UUID

from sqlalchemy import JSON, ForeignKeyConstraint, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from customer.infrastructure.persistence.sqlalchemy.base import CustomerBase


class CustomerPreferenceModel(CustomerBase):
    __tablename__ = "customer_preferences"
    __table_args__ = (
        ForeignKeyConstraint(
            ["customer_id", "business_id"],
            ["customer_customers.id", "customer_customers.business_id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("business_id", "customer_id", "key", name="uq_customer_preference_key"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    business_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    key: Mapped[str] = mapped_column(String(80), nullable=False)
    value: Mapped[str | int | bool] = mapped_column(JSON, nullable=False)

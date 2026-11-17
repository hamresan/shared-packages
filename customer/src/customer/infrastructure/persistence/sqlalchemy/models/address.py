from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, Index, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from customer.infrastructure.persistence.sqlalchemy.base import CustomerBase


class CustomerAddressModel(CustomerBase):
    __tablename__ = "customer_addresses"
    __table_args__ = (
        ForeignKeyConstraint(
            ["customer_id", "business_id"],
            ["customer_customers.id", "customer_customers.business_id"],
            ondelete="CASCADE",
        ),
        Index(
            "uq_customer_addresses_default",
            "business_id",
            "customer_id",
            unique=True,
            postgresql_where=text("is_default = true"),
            sqlite_where=text("is_default = 1"),
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    business_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    label: Mapped[str] = mapped_column(String(80))
    country_code: Mapped[str] = mapped_column(String(2))
    line1: Mapped[str] = mapped_column(String(300))
    city: Mapped[str] = mapped_column(String(150))
    region: Mapped[str | None] = mapped_column(String(150))
    postal_code: Mapped[str | None] = mapped_column(String(40))
    is_default: Mapped[bool] = mapped_column(nullable=False)

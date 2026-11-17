from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKeyConstraint, Index, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from customer.infrastructure.persistence.sqlalchemy.base import CustomerBase


class CustomerExternalIdentityModel(CustomerBase):
    __tablename__ = "customer_external_identities"
    __table_args__ = (
        ForeignKeyConstraint(
            ["customer_id", "business_id"],
            ["customer_customers.id", "customer_customers.business_id"],
            ondelete="CASCADE",
        ),
        Index(
            "uq_customer_external_identity_active_key",
            "business_id",
            "provider",
            "channel_account_id",
            "external_user_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
            sqlite_where=text("status = 'active'"),
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    business_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    channel_account_id: Mapped[str] = mapped_column(String(200), nullable=False)
    external_user_id: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    linked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    verification_method: Mapped[str] = mapped_column(String(80), nullable=False)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

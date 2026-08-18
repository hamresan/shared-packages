from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, DateTime, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from store.infrastructure.persistence.sqlalchemy.base import StoreBase


class StoreModel(StoreBase):
    __tablename__ = "store_stores"
    __table_args__ = (
        Index("ix_store_stores_owner_user_id_id", "owner_user_id", "id"),
        Index("ix_store_stores_country_code", "country_code"),
        Index("ix_store_stores_business_type", "business_type"),
        Index("ix_store_stores_setup_status", "setup_status"),
        Index("ix_store_stores_availability_status", "availability_status"),
        Index("ix_store_stores_moderation_status", "moderation_status"),
        Index("ix_store_stores_deleted_at", "deleted_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    owner_user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    business_type: Mapped[str] = mapped_column(String(80), nullable=False)
    primary_language: Mapped[str] = mapped_column(String(16), nullable=False)
    supported_languages: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    address: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    contacts: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    base_currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    currencies: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False)
    timezone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    working_schedule: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    setup_status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    availability_status: Mapped[str] = mapped_column(String(32), nullable=False, default="offline")
    moderation_status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    suspension_reason: Mapped[str | None] = mapped_column(String(64), nullable=True)
    suspension_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    suspended_by_actor_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    suspended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

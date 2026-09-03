"""SQLAlchemy models for Instagram authorization persistence."""

from datetime import datetime

from sqlalchemy import JSON, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from instagram_auth.infrastructure.persistence.base import InstagramAuthBase
from instagram_auth.infrastructure.persistence.types import UtcDateTime


class InstagramConnectionRecord(InstagramAuthBase):
    """Persist one independent Instagram authorization connection."""

    __tablename__ = "instagram_auth_connections"
    __table_args__ = (
        UniqueConstraint(
            "owner_user_id",
            "instagram_account_id",
            name="uq_instagram_auth_connections_owner_account",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    instagram_account_id: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type: Mapped[str] = mapped_column(String(32), nullable=False)
    permissions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    protected_access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    credential_expires_at: Mapped[datetime | None] = mapped_column(UtcDateTime())
    revoked_at: Mapped[datetime | None] = mapped_column(UtcDateTime())
    last_validated_at: Mapped[datetime | None] = mapped_column(UtcDateTime())
    connected_at: Mapped[datetime] = mapped_column(UtcDateTime(), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

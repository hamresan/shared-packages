from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from identity.domain import IdentityType, OtpPurpose, UserStatus
from identity.infrastructure.persistence.sqlalchemy.base import IdentityBase


class UserModel(IdentityBase):
    __tablename__ = "identity_users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="identity_user_status", native_enum=False),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class UserIdentityModel(IdentityBase):
    __tablename__ = "identity_user_identities"
    __table_args__ = (
        UniqueConstraint(
            "type",
            "normalized_value",
            name="uq_identity_user_identities_type_normalized_value",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("identity_users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[IdentityType] = mapped_column(
        Enum(IdentityType, name="identity_type", native_enum=False), nullable=False
    )
    value: Mapped[str] = mapped_column(String(320), nullable=False)
    normalized_value: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OtpChallengeModel(IdentityBase):
    __tablename__ = "identity_otp_challenges"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("identity_users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    identity_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("identity_user_identities.id", ondelete="CASCADE"), nullable=True, index=True
    )
    identifier_type: Mapped[IdentityType] = mapped_column(
        Enum(IdentityType, name="identity_otp_identifier_type", native_enum=False), nullable=False
    )
    normalized_destination: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    destination_snapshot: Mapped[str] = mapped_column(String(320), nullable=False)
    purpose: Mapped[OtpPurpose] = mapped_column(
        Enum(OtpPurpose, name="identity_otp_purpose", native_enum=False), nullable=False, index=True
    )
    code_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    resend_available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attempts_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class SessionModel(IdentityBase):
    __tablename__ = "identity_sessions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("identity_users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    refresh_token_hash: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    family_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    parent_session_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("identity_sessions.id", ondelete="SET NULL"), nullable=True
    )
    replaced_by_session_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("identity_sessions.id", ondelete="SET NULL"), nullable=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    device_info: Mapped[str | None] = mapped_column(String(512), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


__all__ = ["OtpChallengeModel", "SessionModel", "UserIdentityModel", "UserModel"]

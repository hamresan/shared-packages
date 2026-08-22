"""SQLAlchemy record for integration credentials."""

from datetime import datetime

from sqlalchemy import DateTime, Index, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from integration_auth.infrastructure.persistence.sqlalchemy.models.base import IntegrationAuthBase


class IntegrationCredentialRecord(IntegrationAuthBase):
    """Persist credential metadata plus protected secret material."""

    __tablename__ = "integration_auth_credentials"
    __table_args__ = (
        Index(
            "ix_integration_auth_credentials_client_status_direction",
            "client_id",
            "status",
            "direction",
        ),
    )

    credential_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    protected_secret: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

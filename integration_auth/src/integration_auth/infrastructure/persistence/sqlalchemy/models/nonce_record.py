"""SQLAlchemy record for consumed request nonces."""

from sqlalchemy import BigInteger, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from integration_auth.infrastructure.persistence.sqlalchemy.models.base import IntegrationAuthBase


class ConsumedNonceRecord(IntegrationAuthBase):
    """Persist one consumed nonce per integration client."""

    __tablename__ = "integration_auth_consumed_nonces"
    __table_args__ = (
        UniqueConstraint("client_id", "nonce", name="uq_integration_auth_nonce_client_nonce"),
        Index("ix_integration_auth_nonce_expiry", "expires_at_timestamp"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[str] = mapped_column(String(128), nullable=False)
    nonce: Mapped[str] = mapped_column(String(256), nullable=False)
    expires_at_timestamp: Mapped[int] = mapped_column(BigInteger, nullable=False)

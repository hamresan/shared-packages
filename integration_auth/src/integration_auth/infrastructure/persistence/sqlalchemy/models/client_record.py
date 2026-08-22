"""SQLAlchemy record for integration clients."""

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from integration_auth.infrastructure.persistence.sqlalchemy.models.base import IntegrationAuthBase


class IntegrationClientRecord(IntegrationAuthBase):
    """Persisted integration client and authorization grants."""

    __tablename__ = "integration_auth_clients"

    client_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    permissions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    scopes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

"""Atomic SQLAlchemy nonce store for replay protection."""

from sqlalchemy.exc import IntegrityError

from integration_auth.application.contracts.replay.nonce_store import NonceStore
from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.infrastructure.persistence.sqlalchemy.models.nonce_record import (
    ConsumedNonceRecord,
)
from integration_auth.infrastructure.persistence.sqlalchemy.session import AsyncSessionFactory


class SqlAlchemyNonceStore(NonceStore):
    """Consume client-scoped nonces atomically using a database uniqueness constraint."""

    def __init__(self, session_factory: AsyncSessionFactory) -> None:
        self._session_factory = session_factory

    async def consume_once(
        self,
        *,
        client_id: IntegrationClientId,
        nonce: str,
        expires_at_timestamp: int,
    ) -> bool:
        async with self._session_factory() as session:
            session.add(
                ConsumedNonceRecord(
                    client_id=client_id.value,
                    nonce=nonce,
                    expires_at_timestamp=expires_at_timestamp,
                )
            )
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                return False
            return True

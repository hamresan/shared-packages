"""SQLAlchemy-backed transient credential secret provider."""

from integration_auth.application.contracts.authentication.credential_secret_provider import (
    CredentialSecretProvider,
)
from integration_auth.application.contracts.provisioning.secrets import (
    CredentialSecretUnprotector,
)
from integration_auth.application.security.protected_credential_secret import (
    ProtectedCredentialSecret,
)
from integration_auth.domain.value_objects.identifiers import IntegrationCredentialId
from integration_auth.infrastructure.persistence.sqlalchemy.models.credential_record import (
    IntegrationCredentialRecord,
)
from integration_auth.infrastructure.persistence.sqlalchemy.session import AsyncSessionFactory


class SqlAlchemyCredentialSecretProvider(CredentialSecretProvider):
    """Load protected material and recover a transient verification secret."""

    def __init__(
        self,
        session_factory: AsyncSessionFactory,
        unprotector: CredentialSecretUnprotector,
    ) -> None:
        self._session_factory = session_factory
        self._unprotector = unprotector

    async def get_verification_secret(
        self,
        credential_id: IntegrationCredentialId,
    ) -> bytes | None:
        async with self._session_factory() as session:
            record = await session.get(IntegrationCredentialRecord, credential_id.value)
            if record is None:
                return None
            protected = ProtectedCredentialSecret(record.protected_secret)
            return self._unprotector.unprotect(protected)

"""SQLAlchemy integration-credential repository adapter."""

from sqlalchemy import select

from integration_auth.application.contracts.authentication import (
    IntegrationCredentialRepository,
)
from integration_auth.application.contracts.provisioning.repositories import (
    IntegrationCredentialProvisioningRepository,
)
from integration_auth.application.security.protected_credential_secret import (
    ProtectedCredentialSecret,
)
from integration_auth.domain.entities.integration_credential import IntegrationCredential
from integration_auth.domain.value_objects.identifiers import (
    IntegrationClientId,
    IntegrationCredentialId,
)
from integration_auth.infrastructure.persistence.sqlalchemy.mappers.credential_mapper import (
    IntegrationCredentialRecordMapper,
)
from integration_auth.infrastructure.persistence.sqlalchemy.models.credential_record import (
    IntegrationCredentialRecord,
)
from integration_auth.infrastructure.persistence.sqlalchemy.session import AsyncSessionFactory


class SqlAlchemyIntegrationCredentialRepository(
    IntegrationCredentialRepository,
    IntegrationCredentialProvisioningRepository,
):
    """Persist credential metadata and protected secrets with async SQLAlchemy."""

    def __init__(
        self,
        session_factory: AsyncSessionFactory,
        mapper: IntegrationCredentialRecordMapper,
    ) -> None:
        self._session_factory = session_factory
        self._mapper = mapper

    async def get_by_id(
        self,
        credential_id: IntegrationCredentialId,
    ) -> IntegrationCredential | None:
        async with self._session_factory() as session:
            record = await session.get(IntegrationCredentialRecord, credential_id.value)
            return None if record is None else self._mapper.to_domain(record)

    async def list_for_client(
        self,
        client_id: IntegrationClientId,
    ) -> tuple[IntegrationCredential, ...]:
        async with self._session_factory() as session:
            statement = select(IntegrationCredentialRecord).where(
                IntegrationCredentialRecord.client_id == client_id.value
            )
            records = (await session.execute(statement)).scalars().all()
            return tuple(self._mapper.to_domain(record) for record in records)

    async def add(
        self,
        credential: IntegrationCredential,
        protected_secret: ProtectedCredentialSecret,
    ) -> None:
        async with self._session_factory() as session, session.begin():
            session.add(self._mapper.to_record(credential, protected_secret))

    async def update(self, credential: IntegrationCredential) -> None:
        async with self._session_factory() as session, session.begin():
            record = await session.get(IntegrationCredentialRecord, credential.credential_id.value)
            if record is None:
                raise LookupError("integration credential was not found")
            self._mapper.apply_metadata(record, credential)

    async def rotate(
        self,
        *,
        previous_credentials: tuple[IntegrationCredential, ...],
        new_credential: IntegrationCredential,
        protected_secret: ProtectedCredentialSecret,
    ) -> None:
        async with self._session_factory() as session, session.begin():
            for credential in previous_credentials:
                record = await session.get(
                    IntegrationCredentialRecord,
                    credential.credential_id.value,
                )
                if record is None:
                    raise LookupError("rotation credential was not found")
                self._mapper.apply_metadata(record, credential)
            session.add(self._mapper.to_record(new_credential, protected_secret))

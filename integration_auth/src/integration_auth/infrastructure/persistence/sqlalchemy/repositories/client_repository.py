"""SQLAlchemy integration-client repository adapter."""

from sqlalchemy import select

from integration_auth.application.contracts.authentication.integration_client_repository import (
    IntegrationClientRepository,
)
from integration_auth.application.contracts.provisioning.repositories import (
    IntegrationClientProvisioningRepository,
)
from integration_auth.domain.entities.integration_client import IntegrationClient
from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.infrastructure.persistence.sqlalchemy.mappers.client_mapper import (
    IntegrationClientRecordMapper,
)
from integration_auth.infrastructure.persistence.sqlalchemy.models.client_record import (
    IntegrationClientRecord,
)
from integration_auth.infrastructure.persistence.sqlalchemy.session import AsyncSessionFactory


class SqlAlchemyIntegrationClientRepository(
    IntegrationClientRepository,
    IntegrationClientProvisioningRepository,
):
    """Persist and load integration clients with host-owned async sessions."""

    def __init__(
        self,
        session_factory: AsyncSessionFactory,
        mapper: IntegrationClientRecordMapper,
    ) -> None:
        self._session_factory = session_factory
        self._mapper = mapper

    async def get_by_id(self, client_id: IntegrationClientId) -> IntegrationClient | None:
        async with self._session_factory() as session:
            record = await session.get(IntegrationClientRecord, client_id.value)
            return None if record is None else self._mapper.to_domain(record)

    async def add(self, client: IntegrationClient) -> None:
        async with self._session_factory() as session, session.begin():
            session.add(self._mapper.to_record(client))

    async def update(self, client: IntegrationClient) -> None:
        async with self._session_factory() as session, session.begin():
            statement = select(IntegrationClientRecord).where(
                IntegrationClientRecord.client_id == client.client_id.value
            )
            record = (await session.execute(statement)).scalar_one()
            mapped = self._mapper.to_record(client)
            record.permissions = mapped.permissions
            record.scopes = mapped.scopes

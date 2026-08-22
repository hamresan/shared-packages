"""Map integration clients between domain and SQLAlchemy records."""

from integration_auth.domain.entities.integration_client import IntegrationClient
from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.domain.value_objects.integration_scope import IntegrationScope
from integration_auth.domain.value_objects.permission import Permission
from integration_auth.infrastructure.persistence.sqlalchemy.models.client_record import (
    IntegrationClientRecord,
)


class IntegrationClientRecordMapper:
    """Convert integration-client persistence data without leaking ORM into the domain."""

    def to_record(self, client: IntegrationClient) -> IntegrationClientRecord:
        return IntegrationClientRecord(
            client_id=client.client_id.value,
            permissions=sorted(permission.value for permission in client.permissions),
            scopes=sorted(scope.value for scope in client.scopes),
        )

    def to_domain(self, record: IntegrationClientRecord) -> IntegrationClient:
        return IntegrationClient(
            client_id=IntegrationClientId(record.client_id),
            permissions=frozenset(Permission(value) for value in record.permissions),
            scopes=frozenset(IntegrationScope.from_value(value) for value in record.scopes),
        )

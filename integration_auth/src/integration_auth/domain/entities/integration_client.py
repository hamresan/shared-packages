"""Integration client domain entity."""

from dataclasses import dataclass, field

from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.domain.value_objects.integration_scope import IntegrationScope
from integration_auth.domain.value_objects.permission import Permission


@dataclass(frozen=True, slots=True)
class IntegrationClient:
    """Machine integration identity and its authorization grants."""

    client_id: IntegrationClientId
    permissions: frozenset[Permission] = field(default_factory=frozenset)
    scopes: frozenset[IntegrationScope] = field(default_factory=frozenset)

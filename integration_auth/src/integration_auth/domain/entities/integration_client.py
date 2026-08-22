"""Integration client domain entity."""

from dataclasses import dataclass

from integration_auth.domain.value_objects import IntegrationClientId, IntegrationScope, Permission


@dataclass(frozen=True, slots=True)
class IntegrationClient:
    """Machine integration identity and its authorization grants."""

    client_id: IntegrationClientId
    permissions: frozenset[Permission] = frozenset()
    scopes: frozenset[IntegrationScope] = frozenset()

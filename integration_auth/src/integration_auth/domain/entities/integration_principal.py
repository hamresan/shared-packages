"""Authenticated integration principal."""

from dataclasses import dataclass

from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.domain.value_objects.integration_scope import IntegrationScope
from integration_auth.domain.value_objects.permission import Permission


@dataclass(frozen=True, slots=True)
class IntegrationPrincipal:
    """Authenticated machine identity with authorization facts."""

    client_id: IntegrationClientId
    permissions: frozenset[Permission] = frozenset()
    scopes: frozenset[IntegrationScope] = frozenset()

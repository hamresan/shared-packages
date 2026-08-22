"""Authenticated integration principal."""

from dataclasses import dataclass, field

from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.domain.value_objects.integration_scope import IntegrationScope
from integration_auth.domain.value_objects.permission import Permission


@dataclass(frozen=True, slots=True)
class IntegrationPrincipal:
    """Authenticated machine identity with authorization facts."""

    client_id: IntegrationClientId
    permissions: frozenset[Permission] = field(default_factory=frozenset)
    scopes: frozenset[IntegrationScope] = field(default_factory=frozenset)

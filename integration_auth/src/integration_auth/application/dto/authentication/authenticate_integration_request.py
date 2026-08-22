"""Authentication request DTO."""

from dataclasses import dataclass

from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.protocol.value_objects.canonical_request import CanonicalRequest


@dataclass(frozen=True, slots=True)
class AuthenticateIntegrationRequest:
    """Input required to authenticate one signed integration request."""

    client_id: IntegrationClientId
    request: CanonicalRequest
    signature: str

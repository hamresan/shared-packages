"""Credential issuance result returned only at secret-delivery boundaries."""

from dataclasses import dataclass, field

from integration_auth.domain.entities.integration_credential import IntegrationCredential


@dataclass(frozen=True, slots=True)
class IssuedCredential:
    """New credential metadata and its one-time raw secret."""

    credential: IntegrationCredential
    raw_secret: bytes = field(repr=False)

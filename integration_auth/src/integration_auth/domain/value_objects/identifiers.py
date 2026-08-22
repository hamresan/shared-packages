"""Strongly typed integration identifiers."""

from dataclasses import dataclass

from integration_auth.domain.validators.identifier_validator import (
    IntegrationIdentifierValidator,
)

_IDENTIFIER_VALIDATOR = IntegrationIdentifierValidator()


@dataclass(frozen=True, slots=True)
class IntegrationClientId:
    """Identifier for an integration client."""

    value: str

    def __post_init__(self) -> None:
        _IDENTIFIER_VALIDATOR.validate(self.value, field_name="client_id")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class IntegrationCredentialId:
    """Identifier for an integration credential."""

    value: str

    def __post_init__(self) -> None:
        _IDENTIFIER_VALIDATOR.validate(self.value, field_name="credential_id")

    def __str__(self) -> str:
        return self.value

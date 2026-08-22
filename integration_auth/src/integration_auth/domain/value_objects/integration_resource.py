"""Integration resource value object."""

from dataclasses import dataclass

from integration_auth.domain.validators.resource_scope_validator import ResourceScopeValidator

_RESOURCE_SCOPE_VALIDATOR = ResourceScopeValidator()


@dataclass(frozen=True, slots=True)
class IntegrationResource:
    """Target resource used by authorization policies."""

    resource_type: str
    resource_id: str

    def __post_init__(self) -> None:
        _RESOURCE_SCOPE_VALIDATOR.validate(self.resource_type, self.resource_id)

    @property
    def scope_value(self) -> str:
        """Return the scope representation required for this resource."""
        return f"{self.resource_type}:{self.resource_id}"

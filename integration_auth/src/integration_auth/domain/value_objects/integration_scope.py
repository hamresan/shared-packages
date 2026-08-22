"""Integration scope value object."""

from dataclasses import dataclass

from integration_auth.domain.validators.resource_scope_validator import ResourceScopeValidator

_RESOURCE_SCOPE_VALIDATOR = ResourceScopeValidator()


@dataclass(frozen=True, slots=True)
class IntegrationScope:
    """Authorization scope granted to an integration."""

    resource_type: str
    resource_id: str

    def __post_init__(self) -> None:
        _RESOURCE_SCOPE_VALIDATOR.validate(self.resource_type, self.resource_id)

    @property
    def value(self) -> str:
        """Return the canonical external representation."""
        return f"{self.resource_type}:{self.resource_id}"

    @classmethod
    def from_value(cls, value: str) -> "IntegrationScope":
        """Create a scope from its canonical ``type:id`` representation."""
        if value.count(":") != 1:
            raise ValueError("scope must use the canonical 'resource_type:resource_id' format")
        resource_type, resource_id = value.split(":", maxsplit=1)
        return cls(resource_type=resource_type, resource_id=resource_id)

    def __str__(self) -> str:
        return self.value

"""Permission value object."""

from dataclasses import dataclass

from integration_auth.domain.validators.permission_validator import PermissionValidator

_PERMISSION_VALIDATOR = PermissionValidator()


@dataclass(frozen=True, slots=True)
class Permission:
    """A validated generic integration permission."""

    value: str

    def __post_init__(self) -> None:
        _PERMISSION_VALIDATOR.validate(self.value)

    def __str__(self) -> str:
        return self.value

"""Authorization result DTOs."""

from dataclasses import dataclass
from enum import StrEnum


class AuthorizationDecisionReason(StrEnum):
    """Stable reasons for authorization decisions."""

    ALLOWED = "allowed"
    MISSING_PERMISSION = "missing_permission"
    MISSING_RESOURCE_SCOPE = "missing_resource_scope"


@dataclass(frozen=True, slots=True)
class AuthorizationResult:
    """Framework-neutral authorization decision with no invalid state."""

    reason: AuthorizationDecisionReason

    @property
    def allowed(self) -> bool:
        return self.reason is AuthorizationDecisionReason.ALLOWED

    @classmethod
    def allow(cls) -> "AuthorizationResult":
        return cls(reason=AuthorizationDecisionReason.ALLOWED)

    @classmethod
    def deny(cls, reason: AuthorizationDecisionReason) -> "AuthorizationResult":
        if reason is AuthorizationDecisionReason.ALLOWED:
            raise ValueError("denied authorization result requires a denial reason")
        return cls(reason=reason)

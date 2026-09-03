"""Permission evaluation models."""

from dataclasses import dataclass
from enum import StrEnum

from instagram_auth.baseline import InstagramPermission


class InstagramPermissionStatus(StrEnum):
    """Normalized result of comparing required and granted permissions."""

    COMPLETE = "complete"
    PARTIAL = "partial"


@dataclass(frozen=True, slots=True)
class InstagramPermissionEvaluation:
    """Actionable permission evaluation result."""

    status: InstagramPermissionStatus
    granted_permissions: frozenset[InstagramPermission]
    missing_permissions: frozenset[InstagramPermission]

    @property
    def requires_reauthorization(self) -> bool:
        return self.status is InstagramPermissionStatus.PARTIAL

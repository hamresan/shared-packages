"""Apply a granted-permission snapshot to one selected connection."""

from dataclasses import replace

from instagram_auth.application.contracts import InstagramConnectionRepository
from instagram_auth.baseline import InstagramConnectionState, InstagramPermission
from instagram_auth.domain import InstagramConnectionId

from .models import InstagramPermissionEvaluation, InstagramPermissionStatus
from .policy import InstagramPermissionPolicy


class ApplyInstagramPermissionSnapshot:
    """Persist permission status for one explicit Instagram connection."""

    def __init__(
        self,
        repository: InstagramConnectionRepository,
        policy: InstagramPermissionPolicy,
    ) -> None:
        self._repository = repository
        self._policy = policy

    async def execute(
        self,
        *,
        connection_id: InstagramConnectionId,
        required_permissions: frozenset[InstagramPermission],
        granted_permissions: frozenset[InstagramPermission],
    ) -> InstagramPermissionEvaluation:
        connection = await self._repository.get_by_id(connection_id)
        if connection is None:
            raise LookupError("Instagram connection not found")
        evaluation = self._policy.evaluate(
            required_permissions=required_permissions,
            granted_permissions=granted_permissions,
        )
        status = (
            InstagramConnectionState.CONNECTED
            if evaluation.status is InstagramPermissionStatus.COMPLETE
            else InstagramConnectionState.REAUTHORIZATION_REQUIRED
        )
        await self._repository.update(
            replace(
                connection,
                permissions=evaluation.granted_permissions,
                status=status,
            )
        )
        return evaluation

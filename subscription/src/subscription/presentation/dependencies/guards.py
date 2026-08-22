from subscription.domain import SubjectReference
from subscription.presentation.dependencies.authentication import AuthenticatedActor
from subscription.presentation.dependencies.authorization import SubscriptionAuthorizer
from subscription.presentation.errors.http import SubscriptionAuthorizationDeniedError


class PlanManagementGuard:
    def __init__(self, authorizer: SubscriptionAuthorizer) -> None:
        self._authorizer = authorizer

    async def ensure_allowed(self, actor: AuthenticatedActor) -> None:
        if not await self._authorizer.can_manage_plans(actor):
            raise SubscriptionAuthorizationDeniedError


class SubjectAccessGuard:
    def __init__(self, authorizer: SubscriptionAuthorizer) -> None:
        self._authorizer = authorizer

    async def ensure_allowed(
        self,
        actor: AuthenticatedActor,
        subject: SubjectReference,
    ) -> None:
        if not await self._authorizer.can_access_subject(actor, subject):
            raise SubscriptionAuthorizationDeniedError

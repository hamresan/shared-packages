from typing import Protocol

from subscription.domain import SubjectReference
from subscription.presentation.dependencies.authentication import AuthenticatedActor


class SubscriptionAuthorizer(Protocol):
    async def can_manage_plans(self, actor: AuthenticatedActor) -> bool: ...

    async def can_access_subject(
        self,
        actor: AuthenticatedActor,
        subject: SubjectReference,
    ) -> bool: ...

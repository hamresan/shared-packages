from subscription.domain import SubjectReference
from subscription.presentation import (
    AuthenticatedActor,
    AuthenticatedActorDependency,
    SubscriptionAuthorizer,
)


class FixedAuthenticatedActorDependency(AuthenticatedActorDependency):
    def __init__(self, actor: AuthenticatedActor | None = None) -> None:
        self.actor = actor or AuthenticatedActor("actor-1")

    async def __call__(self) -> AuthenticatedActor:
        return self.actor


class FakeSubscriptionAuthorizer(SubscriptionAuthorizer):
    def __init__(
        self,
        *,
        allow_plan_management: bool = True,
        allow_subject_access: bool = True,
    ) -> None:
        self.allow_plan_management = allow_plan_management
        self.allow_subject_access = allow_subject_access
        self.checked_subjects: list[SubjectReference] = []

    async def can_manage_plans(self, actor: AuthenticatedActor) -> bool:
        del actor
        return self.allow_plan_management

    async def can_access_subject(
        self,
        actor: AuthenticatedActor,
        subject: SubjectReference,
    ) -> bool:
        del actor
        self.checked_subjects.append(subject)
        return self.allow_subject_access

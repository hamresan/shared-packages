from uuid import UUID

from subscription.application.services.subscription.get import GetSubscriptionService
from subscription.domain import Subscription
from subscription.presentation.dependencies.authentication import AuthenticatedActor
from subscription.presentation.dependencies.guards import SubjectAccessGuard


class SubscriptionResourceAccessGuard:
    def __init__(
        self,
        subscription_reader: GetSubscriptionService,
        subject_access_guard: SubjectAccessGuard,
    ) -> None:
        self._subscription_reader = subscription_reader
        self._subject_access_guard = subject_access_guard

    async def ensure_allowed(
        self,
        actor: AuthenticatedActor,
        subscription_id: UUID,
    ) -> Subscription:
        subscription = await self._subscription_reader.execute(subscription_id)
        await self._subject_access_guard.ensure_allowed(actor, subscription.subject)
        return subscription

from subscription import SubjectReference
from subscription.presentation import AuthenticatedActor, SubscriptionAuthorizer


class StoreSubscriptionAuthorizer(SubscriptionAuthorizer):
    def __init__(self, admin_actor_id: str, owned_store_ids: set[str]) -> None:
        self._admin_actor_id = admin_actor_id
        self._owned_store_ids = frozenset(owned_store_ids)

    async def can_manage_plans(self, actor: AuthenticatedActor) -> bool:
        return actor.actor_id == self._admin_actor_id

    async def can_access_subject(
        self,
        actor: AuthenticatedActor,
        subject: SubjectReference,
    ) -> bool:
        if actor.actor_id == self._admin_actor_id:
            return True
        return subject.subject_type == "store" and subject.subject_id in self._owned_store_ids
